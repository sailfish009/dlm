"""One Basis91 model: checked EML bodies, Attention92 execution, formation feedback."""
import cmath
import copy
import itertools
import json
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

from test_sequent import maru
from test_repl import Live
from test_basis91 import reference, bindings
from test_attention92 import answers
from sexp import Symbol as S, dumps, loads_many

ROOT = Path(__file__).resolve().parents[1]
SETUP = '(require "experiments/integration94/setup.l")\n'
INITIAL = """
(basis91 'init '(r s t))
(basis91 'observe 'initial94 '((atom r (a b)) (atom s (b c)) (atom r (p q)) (atom s (q z))))
(basis91 'interpret-controlled 'initial94 200000 'adaptive92)
(basis91 'learn)
"""
ENCODED = INITIAL + "(basis91 'encode 1 'eml94 'principal93)\n"
NEXT = """
(basis91 'observe 'subsequent94 '((atom r (u v)) (atom s (v w)) (atom t (w k))
 (atom r (j l)) (atom s (l m)) (atom t (m n))))
"""
TRIPLE = "'((r 0 1) (s 1 2) (t 2 3))"


def run_fixture(arm='eml94', policy='adaptive92', branch='principal93'):
    data = loads_many((ROOT/'experiments/integration94/input-example.sexp').read_text())[0]
    data[6:9] = [S(arm), S(branch), S(policy)]
    p = subprocess.run([str(ROOT/'scripts/run.sh'), 'integrate94-input'],
                       input=dumps(data), text=True, capture_output=True, timeout=120)
    if p.returncode:
        raise AssertionError(p.stderr[:4000] + p.stdout[:1000])
    return loads_many(p.stdout)


class Integration94Tests(unittest.TestCase):
    def test_migration_preserves_one_model_roles_views_support_and_answers(self):
        out = maru(INITIAL + """
(define old (basis91 'model)) (define evidence (basis91 'evidence))
(define oldrows (dlm-nth (basis91 'query 'initial94 '((r 0 1) (s 1 2)) 200000) 3))
(define numeric-state *e93-state*)
(assert (= (car (basis91 'encode 1 'eml94 'principal93)) 'committed91))
(assert (= (car *b91-state*) 'basis-state91))
(assert (equal evidence (basis91 'evidence)))
(assert (equal (dlm-nth old 4) (dlm-nth (basis91 'model) 4)))
(assert (equal (dlm-nth old 5) (dlm-nth (basis91 'model) 5)))
(assert (equal numeric-state *e93-state*) "no separate numeric learner updates")
(assert (equal oldrows (dlm-nth (basis91 'query 'initial94 '((r 0 1) (s 1 2)) 200000) 3)))
(assert (b91-encoded? (dlm-nth (car (dlm-nth *b91-state* 4)) 3)))
(assert (b91-snapshot? (basis91 'snapshot))) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_entire_boolean_domains_and_independent_cmath_circuit_oracle(self):
        output = loads_many(maru("""
(list-do branch '(principal93 lower93) (list-do n '(1 2 3)
 (let ((code (e94-circuit n)))
  (assert (e94-certified? n code branch))
  (list-do xs (e94-bit-inputs n)
   (dump (list branch code xs (e94-eval-code code xs branch 200000 false))) (print "\n")))))
"""))
        self.assertEqual(len(output), 28)
        maximum = 0
        min_log = float('inf')
        for branch, code, inputs, result in output:
            values = []
            def resolve(ref):
                if ref == 'one93': return 1+0j
                if ref[0] == 'x93': return complex(inputs[ref[1]][1]/1e6, 0)
                return values[ref[1]]
            for tag, a, b in code[1]:
                self.assertEqual(tag, 'eml93')
                aa, bb = resolve(a), resolve(b)
                self.assertGreater(bb.real, 0)
                self.assertLess(abs(bb.imag), 1e-10)
                self.assertLessEqual(abs(aa.real), 6)
                min_log = min(min_log, bb.real)
                values.append(cmath.exp(aa) - cmath.log(bb))
            want = resolve(code[2])
            product = 1
            for _, x, _ in inputs: product *= x//1000000
            self.assertLess(abs(want-product), 1e-9)
            self.assertEqual(result[1], 'complete')
            self.assertEqual(bool(result[2]), product == 2**len(inputs))
            err = abs(complex(result[3][1]/1e6, result[3][2]/1e6)-want)
            maximum = max(maximum, err)
            self.assertLess(err, .002)
        print(f'EML94 FINITE 28 cases, max error={maximum:.9f}, minimum log operand={min_log:.9f}')

    def test_controlled_application_feeds_same_readings_and_next_basis(self):
        out = maru(ENCODED + NEXT + """
(set *e94-metrics* '(eml-metrics94 0 0 0 0 0 0))
(assert (= (car (basis91 'interpret-controlled 'subsequent94 200000 'adaptive92)) 'committed91))
(assert (> (dlm-nth *e94-metrics* 2) 0))
(assert (> (dlm-nth *e94-metrics* 4) 0) "EML filters false candidates, not all-ones decoration")
(define proposal (basis91 'proposal 'eml94 'principal93))
(assert (equal (car (dlm-nth (dlm-nth (dlm-nth proposal 1) 3) 3)) '(call91 1 (0 1 2))))
(assert (= (car (basis91 'learn 'eml94 'principal93)) 'committed91))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 2))
(define result (attention92 'query (basis91 'model) 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000))
(assert (equal (dlm-nth result 5) '((call91 2 (0 1 2 3)))))
(assert (equal (dlm-nth (dlm-nth result 4) 12) '(2 1)))
(assert (= (dlm-length (dlm-nth result 3)) 2)) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_causal_controls_distinguish_prefix_feedback_and_execution(self):
        records = {arm: run_fixture(arm) for arm in
                   ('eml94', 'logical94', 'no-prefix94', 'no-feedback94', 'no-execution94')}
        def record(arm, tag): return next(r for r in records[arm] if r[0] == tag)
        self.assertEqual(len(record('eml94', 'frozen-model94')[1][3]), 2)
        self.assertEqual(len(record('logical94', 'frozen-model94')[1][3]), 2)
        for arm in ('no-prefix94', 'no-feedback94', 'no-execution94'):
            self.assertEqual(len(record(arm, 'frozen-model94')[1][3]), 1)
        triple = [[S('r'), 0, 1], [S('s'), 1, 2], [S('t'), 2, 3]]
        self.assertIn(triple, [c[1] for c in record('eml94', 'formation-candidates94')[1]])
        self.assertNotIn(triple, [c[1] for c in record('no-prefix94', 'formation-candidates94')[1]])
        self.assertEqual(record('no-feedback94', 'formation-update94')[1][0], 'waiting91')
        self.assertEqual(record('no-execution94', 'feedback94')[1][0], 'rejected91')
        self.assertEqual(record('no-execution94', 'answer94')[2][1], 'unknown')
        # Same answers do not imply the same learned organization.
        for left, right in zip([r for r in records['eml94'] if r[0]=='answer94'],
                               [r for r in records['logical94'] if r[0]=='answer94']):
            self.assertEqual(left[2][3], right[2][3])

    def test_standalone_execution_after_removing_training_and_both_learners(self):
        out = maru(SETUP + """
(define model (basis91 'model)) (basis91 'init '(edge)) (eml93 'reset)
(define-function disabled94 args (error "learning/archive forbidden"))
(set b91-propose disabled94) (set b91-data-patterns disabled94) (set b91-replay disabled94)
(set e93-search disabled94) (set e93-propose disabled94) (set e93-fit disabled94)
(define r (attention92 'query model 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000))
(assert (= (dlm-nth r 1) 'complete)) (assert (= (dlm-length (dlm-nth r 3)) 2))
(assert (equal (dlm-nth (dlm-nth r 4) 12) '(2 1)))
(define b (basis91 'infer model 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 200000))
(assert (= (dlm-nth b 1) 'complete)) (assert (equal (dlm-nth b 3) (dlm-nth r 3)))
(print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_mixed_legacy_prefix_and_encoded_successor_then_migration(self):
        out = maru(INITIAL + NEXT + """
(basis91 'interpret-controlled 'subsequent94 200000 'adaptive92)
(basis91 'learn 'eml94 'lower93)
(assert (not (b91-encoded? (dlm-nth (car (dlm-nth *b91-state* 4)) 3))))
(define r (basis91 'query 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 200000))
(assert (= (dlm-nth r 1) 'complete)) (assert (= (dlm-length (dlm-nth r 3)) 2))
(basis91 'encode 1 'eml94 'principal93)
(assert (equal (dlm-nth r 3) (dlm-nth (basis91 'query 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 200000) 3)))
(assert (b91-snapshot? (basis91 'snapshot))) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_migrate_already_hierarchical_existing_library_in_place(self):
        out = maru('(require "experiments/attention92/setup.l")\n' + """
(define old (basis91 'model))
(basis91 'encode 2 'eml94 'principal93) (basis91 'encode 1 'eml94 'principal93)
(assert (= (dlm-nth (basis91 'model) 5) 2))
(define r (attention92 'query (basis91 'model) 'train '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000))
(assert (= (dlm-nth r 1) 'complete)) (assert (= (dlm-length (dlm-nth r 3)) 2))
(assert (equal (dlm-nth (dlm-nth r 4) 12) '(2 1)))
(assert (b91-snapshot? (basis91 'snapshot))) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_fork_target_cycle_and_shared_roles_are_not_silently_chains(self):
        examples = [
            ('((atom r (a b)) (atom s (a c)) (atom r (p q)) (atom s (p z)))',
             '((r 0 1) (s 0 2))'),
            ('((atom r (a c)) (atom s (b c)) (atom r (p z)) (atom s (q z)))',
             '((r 0 1) (s 2 1))'),
            ('((atom r (a b)) (atom s (b a)) (atom r (p q)) (atom s (q p)))',
             '((r 0 1) (s 1 0))')]
        for facts, pattern in examples:
            with self.subTest(pattern=pattern):
                out = maru(f"""
(basis91 'init '(r s)) (basis91 'observe 'g '{facts})
(basis91 'interpret 'g 200000) (basis91 'learn 'eml94 'principal93)
(assert (equal (dlm-nth (car (dlm-nth *b91-state* 4)) 2) '{pattern}))
(define r (attention92 'query (basis91 'model) 'g '{pattern} 'narrow92 200000))
(assert (= (dlm-nth r 1) 'complete)) (assert (= (dlm-length (dlm-nth r 3)) 2))
(assert (b91-snapshot? (basis91 'snapshot))) (print "passed")
""")
                self.assertEqual(out, 'passed')

    def test_finite_graph_oracle_original_witnesses_both_native_paths(self):
        patterns = [
            [[S('r'),0,1],[S('s'),1,2]],
            [[S('r'),0,1],[S('s'),0,2]],
            [[S('r'),0,1],[S('s'),2,1]],
            [[S('r'),0,1],[S('s'),1,0]],
            [[S('r'),0,1],[S('s'),1,2],[S('t'),2,3]],
            [[S('r'),0,0],[S('s'),0,1]]]
        slots = [(p,a,b) for p,a,b in [('r','a','a'),('r','a','b'),('r','b','a'),
                    ('s','a','a'),('s','a','b'),('s','b','a'),('t','a','b'),('t','b','a')]]
        checks = 0
        for branch in ('principal93', 'lower93'):
            for offset in range(0, 256, 64):
                cases = []
                code = SETUP + '(require "experiments/integration94/driver.l")\n'
                if branch == 'lower93':
                    code += "(basis91 'encode 1 'eml94 'lower93) (basis91 'encode 2 'eml94 'lower93)\n"
                code += '(define base (basis91 \'model))\n'
                for mask in range(offset, offset+64):
                    facts = [[S('atom'),S(p),[S(a),S(b)]] for i,(p,a,b) in enumerate(slots) if mask & (1<<i)]
                    code += f"(define m (i94-query-model base '{dumps(facts)}))\n"
                    for j, pattern in enumerate(patterns):
                        cases.append((facts,pattern))
                        policy = 'narrow92' if (mask+j)%2 else 'adaptive92'
                        code += f"(dump (basis91 'infer m 'heldout94 '{dumps(pattern)} 200000)) (print \"\\n\")\n"
                        code += f"(dump (attention92 'query m 'heldout94 '{dumps(pattern)} '{policy} 200000)) (print \"\\n\")\n"
                output = loads_many(maru(code))
                self.assertEqual(len(output), len(cases)*2)
                for (facts, pattern), b, a in zip(cases, output[::2], output[1::2]):
                    want = reference(pattern, facts)
                    self.assertEqual(bindings(b, facts), want)
                    self.assertEqual(answers(a, facts), want)
                    checks += 2
        self.assertEqual(checks, 6144)
        print(f'INTEGRATION94 ORACLE {checks} complete binding/witness checks, zero mismatches')

    def test_foreign_duplicate_and_aliased_roles_preserved(self):
        out = maru(SETUP + """
(basis91 'observe 'alias '((atom r (a a)) (atom s (a a)) (atom t (a a))))
(define r (attention92 'query (basis91 'model) 'alias '((r 0 0) (s 0 1) (t 1 0)) 'ordered92 200000))
(assert (= (dlm-nth r 1) 'complete))
(assert (equal (dlm-nth (car (dlm-nth r 3)) 1) '(a a)))
(assert (equal (dlm-nth (car (dlm-nth r 3)) 2) '(0 1 2))) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_forged_circuits_metadata_roles_and_prefixes_rejected(self):
        out = maru(SETUP + """
(define model (basis91 'model)) (define lib (dlm-nth model 3))
(define module (car lib)) (define body (dlm-nth module 3))
(list-do bad (list (s79-field body 1 'other) (s79-field body 2 'unknown-branch)
 (s79-field body 3 '((fact91 r (0 1)) (fact91 s (0 2))))
 (s79-field body 3 '((call91 2 (0 1 2 3)) (fact91 r (0 1))))
 (s79-field body 4 '(circuit94 () (x93 0)))
 (s79-field body 4 '(circuit94 ((eml93 one93 (wire94 0))) (wire94 0)))
 (s79-field body 4 '(circuit94 ((eml93 one93 (x93 -1))) (wire94 0))))
 (assert (not (b91-model? (s79-field model 3 (cons (s79-field module 3 bad) (cdr lib)))))))
(define before *b91-state*)
(assert (= (car (basis91 'encode 1 'eml94 'other)) 'rejected91))
(assert (= (car (basis91 'learn 'other 'principal93)) 'rejected91))
(assert (equal before *b91-state*)) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_malformed_external_data_does_not_crash_codec_or_model_checks(self):
        rng = random.Random(9401)
        atoms = [[], 0, -1, 999, S('encoded91'), S('wire94'), 'x', S('one93')]
        def tree(depth):
            if not depth or rng.random()<.5: return rng.choice(atoms)
            return [tree(depth-1) for _ in range(rng.randrange(7))]
        values = [tree(4) for _ in range(400)]
        code = '(define xs (read *standard-input*))\n(list-do x xs (e94-read-body x) (b91-model? x) (b91-snapshot? x)) (print "passed")'
        self.assertEqual(maru(code, dumps(values)), 'passed')

    def test_omitted_eml_worker_rows_are_rejected_by_both_independent_gates(self):
        out = maru(SETUP + """
(define-function omit94 (body args ep lib scope envs r) (a92-computed 'complete () r))
(set *b91-codec-controlled* omit94)
(define before *b91-state*)
(assert (= (car (attention92 'query (basis91 'model) 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)) 'rejected92))
;; Basis91 uses the same shared worker, not a legacy solved-answer fallback.
(set e94-controlled-execute omit94)
(assert (= (dlm-nth (basis91 'query 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 200000) 1) 'rejected))
(assert (equal before *b91-state*)) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_numerical_failure_is_unknown_not_false_or_fallback(self):
        out = maru(SETUP + """
(define-function broken94 (a b branch) '(undefined93 injected))
(set e93-eml broken94)
(define r (basis91 'query 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 200000))
(assert (= (dlm-nth r 1) 'unknown)) (assert (not (dlm-nth r 3)))
(define a (attention92 'query (basis91 'model) 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000))
(assert (= (dlm-nth a 1) 'unknown)) (assert (not (dlm-nth a 3))) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_budget_failure_and_failed_feedback_publish_no_partial_readings(self):
        out = maru(ENCODED + NEXT + """
(define before *b91-state*)
(assert (= (car (basis91 'interpret-controlled 'subsequent94 1 'adaptive92)) 'rejected91))
(assert (equal before *b91-state*))
(list-do fuel '(0 1 20)
 (define a (attention92 'query (basis91 'model) 'initial94 '((r 0 1) (s 1 2)) 'adaptive92 fuel))
 (assert (= (dlm-nth a 1) 'unknown)) (assert (not (dlm-nth a 3))))
(assert (= (car (basis91 'interpret-controlled 'subsequent94 200000 'not-policy)) 'rejected91))
(assert (equal before *b91-state*)) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_partial_empty_scope_requires_widen_then_keeps_original_ids(self):
        out = maru(SETUP + """
(attention92 'start (basis91 'model) 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)
(attention92 'step '(focus92 subsequent94 5 2 (0) (2) (call91 2 (0 1 2 3))))
(attention92 'tick) (attention92 'tick)
(assert (= (dlm-nth (a92-work *a92-state*) 7) 'need-widen))
(assert (not (dlm-nth (attention92 'result) 3)))
(define r (attention92 'run 64))
(assert (= (dlm-nth r 1) 'complete))
(assert (equal (dlm-nth (car (dlm-nth r 3)) 2) '(0 1 2)))
(assert (= (dlm-nth (dlm-nth r 4) 9) 1)) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_retraction_new_source_and_historical_frozen_context(self):
        out = maru(SETUP + """
(define old (basis91 'model)) (define library (dlm-nth old 3))
(basis91 'retract 'subsequent94)
(assert (equal library (dlm-nth (basis91 'model) 3)))
(assert (= (car (attention92 'query (basis91 'model) 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)) 'rejected92))
(basis91 'observe 'subsequent94 '((atom r (a b)) (atom s (b c)) (atom t (other d))))
(define r (attention92 'query (basis91 'model) 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000))
(assert (= (dlm-nth r 1) 'complete)) (assert (not (dlm-nth r 3)))
(define historical (attention92 'query old 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000))
(assert (= (dlm-length (dlm-nth historical 3)) 2))
(assert (b91-snapshot? (basis91 'snapshot))) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_replay_rejects_forged_core_audit_and_training_witnesses(self):
        out = maru(SETUP + """
(define snap (basis91 'snapshot))
(assert (b91-snapshot? snap))
(assert (not (b91-snapshot? (s79-field snap 3 ()))))
(assert (not (b91-snapshot? (s79-field snap 4 (cdr (dlm-nth snap 4))))))
(define core (dlm-nth snap 2)) (define lib (dlm-nth core 3))
(define altered (s79-field (car lib) 3 (e94-encode (b91-body-ops (dlm-nth (car lib) 3)) 'eml94 'lower93)))
(assert (b91-model? (s79-field core 3 (cons altered (cdr lib)))))
(assert (not (b91-snapshot? (s79-field snap 2 (s79-field core 3 (cons altered (cdr lib)))))))
(print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_fresh_process_checkpoint_continues_same_cumulative_learning(self):
        with tempfile.TemporaryDirectory() as d:
            q = json.dumps(str(Path(d)/'shared.sexp'))
            out = maru(ENCODED + f"(basis91 'open {q}) (assert (= (car (basis91 'close)) 'closed91)) (print \"passed\")")
            self.assertEqual(out, 'passed')
            out = maru(f"(basis91 'init '(r s t)) (assert (= (car (basis91 'open {q})) 'basis91))\n" + NEXT + """
(basis91 'interpret-controlled 'subsequent94 200000 'adaptive92)
(assert (= (car (basis91 'learn 'eml94 'principal93)) 'committed91))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 2))
(assert (b91-snapshot? (basis91 'snapshot)))
(assert (= (car (basis91 'close)) 'closed91)) (print "passed")
""")
            self.assertEqual(out, 'passed')
            out = maru(f"(basis91 'init '(r s t)) (basis91 'open {q})\n" + """
(define r (basis91 'query 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 200000))
(assert (= (dlm-length (dlm-nth r 3)) 2)) (basis91 'close) (print "passed")
""")
            self.assertEqual(out, 'passed')

    def test_failed_checkpoint_preserves_same_live_model_and_attachment(self):
        with tempfile.TemporaryDirectory() as d:
            q = json.dumps(str(Path(d)/'shared.sexp'))
            out = maru(INITIAL + f"(basis91 'open {q})\n" + """
(define before *b91-state*)
(define saved-checkpoint b91-checkpoint)
(define-function fail94 args false) (set b91-checkpoint fail94)
(assert (= (car (basis91 'encode 1 'eml94 'principal93)) 'rejected91))
(assert (equal before *b91-state*))
(assert (= (car (basis91 'close)) 'rejected91)) (assert *b91-path*)
(set b91-checkpoint saved-checkpoint)
(assert (= (car (basis91 'close)) 'closed91)) (print "passed")
""")
            self.assertEqual(out, 'passed')

    def test_two_process_lock_ownership_survives_failed_close(self):
        with tempfile.TemporaryDirectory() as d:
            q = json.dumps(str(Path(d)/'shared.sexp'))
            live = Live()
            try:
                live.exchange("(basis91 'init '(r s t))", rb'\(basis91 epoch 0')
                live.exchange(f"(basis91 'open {q})", rb'\(basis91 epoch 0')
                out = maru(f"(assert (equal (basis91 'open {q}) '(rejected91 locked-or-path))) (print \"passed\")")
                self.assertEqual(out, 'passed')
            finally:
                live.close()

    def test_attention_snapshot_replay_retains_encoded_context_and_next_action(self):
        out = maru(SETUP + """
(attention92 'start (basis91 'model) 'subsequent94 '((r 0 1) (s 1 2) (t 2 3)) 'narrow92 200000)
(attention92 'run 3) (define snap (attention92 'snapshot))
(assert (a92-snapshot? snap))
(define expected (a92-next *a92-state*))
(attention92 'reset) (attention92 'restore snap)
(assert (equal expected (a92-next *a92-state*)))
(assert (= (dlm-nth (attention92 'run 64) 1) 'complete)) (print "passed")
""")
        self.assertEqual(out, 'passed')

    def test_data_only_input_rejects_trailing_text_and_injected_programs(self):
        text = (ROOT/'experiments/integration94/input-example.sexp').read_text()
        for data in (text+'\n(extra)', text.replace('eml94 principal93', 'unknown principal93'),
                     text.replace('(atom r (a b))', '(eval (basis91 reset))')):
            p = subprocess.run([str(ROOT/'scripts/run.sh'),'integrate94-input'], input=data,
                               text=True,capture_output=True,timeout=120)
            self.assertNotEqual(p.returncode, 0)

    def test_four_controls_two_branches_preserve_fresh_and_broken_bindings(self):
        for branch, policy in itertools.product(('principal93','lower93'),
                ('ordered92','indexed92','adaptive92','narrow92')):
            with self.subTest(branch=branch, policy=policy):
                records = run_fixture(policy=policy, branch=branch)
                found = [r for r in records if r[0]=='answer94']
                self.assertEqual(found[0][2][1], 'complete')
                self.assertEqual(len(found[0][2][3]), 1)
                self.assertEqual(found[1][2][1], 'complete')
                self.assertEqual(found[1][2][3], [])
                self.assertTrue(next(r[1] for r in records if r[0]=='snapshot-valid94'))

    def test_unsupported_codec_and_read_only_proposal_never_publish(self):
        out = maru(ENCODED + NEXT + """
(basis91 'interpret-controlled 'subsequent94 200000 'adaptive92)
(define before *b91-state*)
(define p (basis91 'proposal 'eml94 'principal93))
(assert (= (car p) 'learn91)) (assert (equal before *b91-state*))
(assert (= (car (basis91 'encode 99 'eml94 'principal93)) 'rejected91))
(assert (= (car (basis91 'learn 'eml94 'wrong)) 'rejected91))
(assert (equal before *b91-state*)) (print "passed")
""")
        self.assertEqual(out, 'passed')


if __name__ == '__main__':
    unittest.main()
