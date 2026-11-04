"""Web ingress -> SAME learner; source integrity, no repair, revision and replay.

Tiny generated CSVs are synthetic protocol fixtures, not downloaded web evidence.
Actual full-source tests use the private offline cache and never fabricate it.
"""
import base64
import copy
import hashlib
import http.client
import json
import random
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from test_sequent import maru
from test_repl import Live
from sexp import Symbol as S, dumps, loads_many
from web import CachedWeb, digest
from web96 import URL, acquire, extract, packet, RestrictedRedirects
from web96_experiment import run, raw_records, oracle

ROOT = Path(__file__).resolve().parents[1]
RAW = (b'M49,Sub-region Code,Region Code,Global Code,comment\r\n'
       b'4,34,142,1,"synthetic, first"\r\n8,39,150,1,second\r\n'
       b'12,15,2,1,third\r\n16,61,9,1,fourth\r\n20,39,150,1,"quoted ""cell""\ncontinued"\r\n'
       b'24,17,2,1,sixth\r\n10,,,1,unresolved\r\n90,54,9,1,seventh\r\n')


def record(raw=RAW):
    return dict(url=URL, final_url=URL, fetched_at='2000-01-01T00:00:00+00:00',
                sha256=hashlib.sha256(raw).hexdigest(), raw_base64=base64.b64encode(raw).decode(), media_type='text/csv')


P = packet(record())
D = dumps(P)
BASE = '(require "experiments/web96/driver.l")\n(set i96-emit (lambda (x) ()))\n(define p96 \'%s)\n' % D
PREP = BASE + '(i96-prepare p96 \'logical96)\n'
VIEW = '"web-row96:020"'
PATTERN = "'((country-subregion96 0 1) (subregion-region96 1 2) (region-global96 2 3))"
QUERY = f'(basis91 \'web-query {VIEW} {PATTERN} 200000 \'adaptive92)'


class Web96Tests(unittest.TestCase):
    def checked(self, text, prefix=PREP):
        self.assertEqual(maru(prefix + text + '\n(print "passed")'), 'passed')

    def test_native_sha256_against_stdlib_boundaries_and_random_bytes(self):
        rng = random.Random(96)
        raws = [b'', b'abc', b'\0', bytes(range(256))] + [rng.randbytes(n) for n in (1, 7, 55, 56, 63, 64, 65, 127, 128, 1000)]
        checks = '\n'.join('(assert (equal (w96-sha256 (w96-unhex "%s")) "%s"))' % (r.hex(), hashlib.sha256(r).hexdigest()) for r in raws)
        self.checked(checks, prefix='')

    def test_native_csv_projection_matches_independent_worker_with_quotes_newlines_crlf(self):
        self.checked('(assert (w96-packet? p96))\n(assert (equal (w96-extract (w96-unhex (dlm-nth p96 6))) (dlm-nth p96 7)))', prefix=BASE)
        self.assertEqual(len(P[7][4]), 3)
        self.assertEqual(len(P[7][5]), 1)

    def test_actual_full_web_csv_native_integrity_and_extraction(self):
        p = packet(acquire())  # No network permission. Missing cache is an error.
        self.assertEqual(p[4], 'bb199ebc9636b9872705e8216f1f849359f136a7668ebfa23a3c58048462ab92')
        self.checked('(assert (w96-packet? \'%s))' % dumps(p), prefix='')
        self.assertEqual((p[7][6], len(p[7][4]), len(p[7][5])), (249, 244, 1))

    def test_cache_keys_are_full_copied_bytes_not_digest_only(self):
        self.checked('''
(assert (w96-packet? p96))
(define hex96 (concat-strings "" (dlm-nth p96 6)))
(define copy96 (s79-field p96 6 hex96))
(assert (w96-packet? copy96))
(set (string-at hex96 0) (if (= (string-at hex96 0) 48) 49 48))
(assert (not (w96-packet? copy96)))
(assert (w96-packet? p96))
''', prefix=BASE)

    def test_later_numeric_formation_preserves_web_execution(self):
        self.checked('''
(assert (= (car (basis91 'calibrate "synthetic-numeric-after-web" 1
 '((row93 a ((z93 100000 0)) (z93 1105170 0))
   (row93 b ((z93 200000 0)) (z93 1221403 0))
   (row93 c ((z93 300000 0)) (z93 1349859 0))))) 'committed91))
(assert (= (car (basis91 'learn-numeric "synthetic-numeric-after-web" 1 200000)) 'committed91))
(assert (equal (map car (dlm-nth *b91-state* 4)) '(basis91 basis91 numeric95)))
(assert (= (dlm-nth %s 1) 'complete))
(assert (b91-snapshot? (basis91 'snapshot)))
''' % QUERY)

    def test_failed_source_checkpoint_does_not_publish_or_detach(self):
        with tempfile.TemporaryDirectory() as directory:
            path = dumps(str(Path(directory) / 'state.sexp'))
            p2 = packet(record(RAW.replace(b'20,39,150,1,', b'20,34,142,1,')))
            self.checked('''
(basis91 'open %s)
(define before96 (basis91 'snapshot))
(define checkpoint96 b91-checkpoint)
(set b91-checkpoint (lambda args false))
(assert (equal (basis91 'web-import '%s (basis91 'web-token)) '(rejected91 checkpoint)))
(assert (equal before96 (basis91 'snapshot)))
(assert *b91-path*)
(set b91-checkpoint checkpoint96)
(assert (= (car (basis91 'close)) 'closed91))
''' % (path, dumps(p2)))

    def test_same_owner_actual_prefix_graph_and_source_grounding(self):
        self.checked('''
(assert (= (car *b91-state*) 'basis-state91))
(assert (= (dlm-nth *b91-state* 1) 2))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 2))
(assert (equal (dlm-nth (dlm-nth (dlm-nth *b91-state* 4) 1) 3)
  '((call91 1 (0 1 2)) (fact91 region-global96 (2 3)))))
(assert (not *e93-state*))
(assert (b91-snapshot? (basis91 'snapshot)))
(assert (w96-state? *b91-state*))
(assert (equal (dlm-nth (basis91 'web-source) 4) (dlm-nth p96 4)))
(assert (not (dlm-nth (dlm-nth (basis91 'model) 6) 2)))
''')

    def test_worker_omitted_changed_facts_or_byte_proof_rejected_without_repair(self):
        bads = []
        for where in ('facts', 'proof', 'heldout', 'unresolved'):
            p = copy.deepcopy(P)
            if where == 'facts': p[7][2][4].pop()
            if where == 'proof': p[7][2][5][0][6] += 1
            if where == 'heldout': p[7][4].pop()
            if where == 'unresolved': p[7][5] = []
            bads.append(p)
        code = '(basis91 \'init *w96-predicates*)\n(define before96 (basis91 \'snapshot))\n'
        for p in bads:
            code += '(assert (= (car (basis91 \'web-import \'%s \'missing96)) \'rejected91))\n' % dumps(p)
            code += '(assert (equal before96 (basis91 \'snapshot)))\n'
        self.checked(code, prefix=BASE)

    def test_wrong_digest_raw_hex_and_bounds_rejected(self):
        bads = []
        p = copy.deepcopy(P); p[4] = '0' * 64; bads.append(p)
        p = copy.deepcopy(P); p[6] = p[6][:-1]; bads.append(p)
        p = copy.deepcopy(P); p[6] = 'zz' + p[6][2:]; bads.append(p)
        p = copy.deepcopy(P); p[6] = '00' * 262145; bads.append(p)
        self.checked('\n'.join('(assert (not (w96-packet? \'%s)))' % dumps(p) for p in bads), prefix=BASE)

    def test_malformed_csv_schema_duplicate_country_and_limits(self):
        invalid = [b'a,b\n1,2\n', RAW.replace(b'M49,', b'Global Code,', 1),
                   RAW.replace(b'4,34,', b'8,34,', 1), RAW + b'"unfinished', RAW.replace(b'second', b'"bad"x'),
                   RAW + b'1,2\n', RAW + b'1,2,3,4,' + b'x' * 8193]
        checks = []
        for raw in invalid:
            checks.append('(assert (not (= (car (w96-extract (w96-unhex "%s"))) \'extraction96)))' % raw.hex())
        self.checked('\n'.join(checks), prefix='')

    def test_duplicate_fetch_does_not_add_support_or_events(self):
        p = copy.deepcopy(P); p[3] = '2001-01-01T00:00:00Z'
        self.checked('''(define before96 (basis91 'snapshot))
(assert (= (car (basis91 'web-import '%s (basis91 'web-token))) 'unchanged96))
(assert (equal before96 (basis91 'snapshot)))''' % dumps(p))

    def test_source_cas_and_protected_episode_retraction(self):
        self.checked('''(define before96 (basis91 'snapshot))
(assert (= (car (basis91 'web-retract "wrong")) 'rejected91))
(assert (= (car (basis91 'web-import p96 "wrong")) 'rejected91))
(assert (= (car (basis91 'retract "web-train96")) 'rejected91))
(assert (equal before96 (basis91 'snapshot)))''')

    def test_missing_source_row_and_budget_are_unknown_not_empty_complete(self):
        self.checked('''
(assert (equal (basis91 'web-query "web-row96:010" %s 200000 'adaptive92)
  '(web-answer96 unknown unresolved-source-row ())))
(assert (equal (basis91 'web-query "web-row96:020" %s 1 'adaptive92)
  '(web-answer96 unknown incomplete-worker ())))''' % (PATTERN, PATTERN))

    def test_query_worker_omission_is_not_filled(self):
        self.checked('''(define before96 (basis91 'snapshot))
(set a92-execute (lambda (op ep lib scope envs r) (a92-computed 'complete () r)))
(assert (equal %s '(web-answer96 unknown incomplete-worker ())))
(assert (equal before96 (basis91 'snapshot)))''' % QUERY)

    def test_revision_changes_current_answers_not_frozen_core(self):
        p2 = packet(record(RAW.replace(b'20,39,150,1,', b'20,34,142,1,')))
        self.checked('''
(define historical96 (basis91 'model))
(define p2 '%s)
(assert (= (car (basis91 'web-import p2 (basis91 'web-token))) 'committed91))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 2))
(assert (not (dlm-nth *b91-state* 5)))
(assert (equal (basis91 'web-infer (basis91 'model) p96 %s %s 200000 'adaptive92)
  '(web-answer96 unknown source-version ())))
(define current96 %s)
(assert (equal (dlm-nth (car (dlm-nth current96 3)) 1) '("country:020" "subregion:034" "region:142" "global:001")))
(define old96 (basis91 'web-infer historical96 p96 %s %s 200000 'adaptive92))
(assert (equal (dlm-nth (car (dlm-nth old96 3)) 1) '("country:020" "subregion:039" "region:150" "global:001")))
(assert (b91-snapshot? (basis91 'snapshot)))
''' % (dumps(p2), VIEW, PATTERN, QUERY, VIEW, PATTERN))

    def test_withdrawal_restoration_and_historical_context(self):
        self.checked('''
(define old96 (basis91 'model))
(define token96 (basis91 'web-token))
(assert (= (car (basis91 'web-retract token96)) 'committed91))
(assert (not (dlm-nth *b91-state* 3)))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 2))
(assert (equal %s '(web-answer96 unknown inactive-source ())))
(assert (= (dlm-nth (w96-infer old96 p96 %s %s 200000 'adaptive92) 1) 'complete))
(assert (= (car (basis91 'web-import p96 (basis91 'web-token))) 'committed91))
(assert (= (car (basis91 'web-retract token96)) 'rejected91))
(assert (= (dlm-nth %s 1) 'complete))
(assert (b91-snapshot? (basis91 'snapshot)))
''' % (QUERY, VIEW, PATTERN, QUERY))

    def test_forged_snapshot_source_metadata_or_projection_rejected(self):
        self.checked('''
(define snap96 (basis91 'snapshot))
(define model96 (dlm-nth snap96 2))
(define facet96 (dlm-nth model96 6))
(define manifest96 (dlm-nth facet96 3))
(define bad96 (s79-field snap96 2 (s79-field model96 6 (s79-field facet96 3 (s79-field manifest96 4 "0000000000000000000000000000000000000000000000000000000000000000")))))
(assert (not (b91-snapshot? bad96)))
(assert (= (car (basis91 'restore bad96)) 'rejected91))
(assert (equal snap96 (basis91 'snapshot)))
''')

    def test_core_only_without_learner_live_owner_or_training_episodes(self):
        self.checked('''
(define core96 (s79-field (s79-field (basis91 'model) 2 ()) 4 ()))
(set *b91-state* ()) (set *e93-state* ())
(set b91-replay (lambda args '(disabled96)))
(set b91-propose (lambda args '(disabled96)))
(set b91-candidates (lambda args '(disabled96)))
(set b91-interpret (lambda args '(disabled96)))
(assert (= (dlm-nth (w96-infer core96 p96 %s %s 200000 'adaptive92) 1) 'complete))
(assert (not *b91-state*))
''' % (VIEW, PATTERN))

    def test_later_numeric_learning_same_global_library_and_source_replay(self):
        self.checked('''
(basis91 'init *w96-predicates*) (basis91 'types 'principal93)
(assert (= (car (basis91 'calibrate "synthetic-unit-test" 1
 '((row93 a ((z93 100000 0)) (z93 1105170 0))
   (row93 b ((z93 200000 0)) (z93 1221403 0))
   (row93 c ((z93 300000 0)) (z93 1349859 0))))) 'committed91))
(assert (= (car (basis91 'learn-numeric "synthetic-unit-test" 1 200000)) 'committed91))
(assert (= (car (basis91 'web-import p96 'missing96)) 'committed91))
(basis91 'interpret "web-train96" 200000) (basis91 'learn)
(basis91 'interpret-controlled "web-next96" 200000 'adaptive92) (basis91 'learn)
(assert (equal (map car (dlm-nth *b91-state* 4)) '(numeric95 basis91 basis91)))
(assert (equal (map (lambda (m) (dlm-nth m 1)) (dlm-nth *b91-state* 4)) '(1 2 3)))
(assert (not *e93-state*)) (assert (b91-snapshot? (basis91 'snapshot)))
''', prefix=BASE)

    def test_all_causal_arms_and_representation_control(self):
        for arm in ('logical96', 'eml96', 'no-prefix96', 'no-formation96', 'no-extraction96'):
            with self.subTest(arm=arm):
                r, _ = run(P, arm, queries=3)
                self.assertEqual(r['mismatches'], 0)
                self.assertEqual(r['attempts'], 12)

    def test_all_policies_and_independent_binding_witness_oracle(self):
        r, _ = run(P, queries=3, policies=('adaptive92', 'ordered92', 'indexed92', 'raw96'))
        self.assertEqual((r['attempts'], r['complete_rows'], r['mismatches']), (24, 24, 0))
        records = raw_records(RAW)
        self.assertEqual(oracle(records['web-row96:020'][1], [[S('country-subregion96'), 0, 0]]), {})

    def test_malformed_native_packets_cores_and_models_are_rejected(self):
        rng = random.Random(96)
        def tree(depth):
            if depth == 0 or rng.random() < .35:
                return rng.choice([[], S('web-document96'), S('web-core96'), 0, -1, 42, 'junk'])
            return [tree(depth - 1) for _ in range(rng.randrange(12))]
        values = [tree(3) for _ in range(400)]
        self.checked('''(list-do x '%s
(assert (not (w96-packet? x)))
(assert (not (w96-core? x)))
(assert (= (car (w96-infer x p96 "x" '((country-subregion96 0 1)) 1 'adaptive92)) 'rejected96)))''' % dumps(values), prefix=BASE)

    def test_native_checkpoint_restore_and_lock_exclusion(self):
        with tempfile.TemporaryDirectory() as directory:
            path = dumps(str(Path(directory) / 'shared.sexp'))
            with_file = PREP + f'(assert (= (car (basis91 \'open {path})) \'basis91))\n'
            live = Live()
            try:
                live.exchange(with_file + '(print "WEB96_READY")\n', b'WEB96_READY')
                self.checked(f'(basis91 \'init *w96-predicates*) (assert (= (car (basis91 \'open {path})) \'rejected91))', prefix='')
                live.exchange('(dump (basis91 \'close))\n', b'closed91')
            finally:
                live.close()
            self.checked(f'''(basis91 'init *w96-predicates*)
(assert (= (car (basis91 'open {path})) 'basis91))
(assert (= (dlm-nth {QUERY} 1) 'complete))
(assert (b91-snapshot? (basis91 'snapshot)))
(assert (= (car (basis91 'close)) 'closed91))''', prefix='')

    def test_data_only_input_rejects_trailing_executable_forms(self):
        data = dumps([S('web-run96'), P, S('logical96'), 1, [S('raw96')]])
        p = subprocess.run([str(ROOT / 'scripts/run.sh'), 'web96-input'], input=data + '\n(print "INJECTED96")\n', text=True, capture_output=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn('INJECTED96', p.stdout)

    def test_http_truncation_errors_and_cache_integrity_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            web = CachedWeb(directory)
            response = Mock()
            response.__enter__ = Mock(return_value=response)
            response.__exit__ = Mock(return_value=False)
            response.headers = {'Content-Length': '20'}
            response.read.return_value = b'abc'
            response.geturl.return_value = URL
            web.opener = Mock()
            web.opener.open.return_value = response
            self.assertEqual(web.get_record(URL), (None, 'truncated-response'))
            response.headers = {}
            response.read.side_effect = http.client.IncompleteRead(b'abc', 5)
            self.assertEqual(web.get_record(URL), (None, 'http-error:IncompleteRead'))
            self.assertEqual(list(web.root.iterdir()), [])
            response.read.side_effect = None
            response.read.return_value = RAW
            response.headers = {'Content-Length': str(len(RAW)), 'Content-Type': 'text/csv'}
            good, error = web.get_record(URL)
            self.assertIsNone(error)
            cache_file = web.root / (digest(URL.encode()) + '.json')
            bad = json.loads(cache_file.read_text()); bad['sha256'] = '0' * 64
            cache_file.write_text(json.dumps(bad))
            self.assertEqual(CachedWeb(directory, offline=True).get_record(URL), (None, 'invalid-cache'))

    def test_disallowed_redirect_is_rejected_before_open(self):
        handler = RestrictedRedirects()
        for url in ('file:///etc/passwd', 'http://127.0.0.1/x', 'https://example.com/a', URL + '?x=1'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                handler.redirect_request(None, None, 302, '', {}, url)
