"""Separate inherited-boundary fixes; no sockets/network required."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_sequent import maru
from sexp import loads_many

ROOT = Path(__file__).resolve().parents[1]


class Review90Tests(unittest.TestCase):
    def test_web_document_shape_validation_is_total(self):
        out = maru("""
(list-do x (list 42 'bad (cons 'document 42)
 '(document x (url h) 42 (fetched-at h) (media-type h) (sha256 h) (raw h) (source-group c) (status acquired-uninterpreted)))
 (assert (not (web-document? x)) "malformed document"))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_malformed_web_import_errors_without_sigsegv(self):
        expressions = ["(web-ingest (web-new) '(acquisition 74 42 ()))",
                       "(web-ingest (web-new) '(acquisition 74 () 42))",
                       "(web-verify-state 42)", "(web-replay (list 42))",
                       "(web-ingest '(web-state 74 (42) ()) '(acquisition 74 () ()))"]
        for code in expressions:
            with self.subTest(code=code), tempfile.NamedTemporaryFile(mode='w', suffix='.l') as f:
                f.write(code)
                f.flush()
                p = subprocess.run([str(ROOT / 'scripts/run.sh'), 'proof', f.name],
                                   text=True, capture_output=True, timeout=20)
                self.assertGreater(p.returncode, 0, p.stderr)  # application error, not a signal

    def test_web_shell_with_seeded_offline_cache_and_no_executable_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            url = 'https://example.invalid/offline90'
            raw = '(error "not executable") 외부 원문'.encode()
            record = dict(url=url, final_url=url, fetched_at='2026-10-29T00:00:00Z',
                          media_type='text/plain', sha256=hashlib.sha256(raw).hexdigest(),
                          raw_base64=base64.b64encode(raw).decode())
            cache = root / 'cache/fetch'
            cache.mkdir(parents=True)
            (cache / (hashlib.sha256(url.encode()).hexdigest() + '.json')).write_text(json.dumps(record))
            for count in (1, 2):
                p = subprocess.run([str(ROOT / 'scripts/web.sh'), '--offline', '--url', url],
                                   env=dict(os.environ, STORE=directory), text=True,
                                   capture_output=True, timeout=30)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertIn('(documents 1)', p.stdout)
                self.assertIn(f'(acquisitions {count})', p.stdout)
                self.assertIn('(admitted-facts 0)', p.stdout)
            p = subprocess.run([str(ROOT / 'scripts/run.sh'), 'web-ingest'], input='42',
                               text=True, capture_output=True, timeout=20)
            self.assertGreater(p.returncode, 0)

    def test_joint_plain_replay_is_independent_of_live_ground_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'joint.sexp'
            q = json.dumps(str(path))
            first = maru(f"""(dlm 'open {q}) (dlm 'demo) (dlm 'ground 'on)
(dlm 'curriculum 'relations) (dlm 'relation-budget 1)
(times-do 2 (dlm 'step)) (dlm 'save)
(dump (d77-pack *dlm-model* *dlm-round* *dlm-events*)) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump *c88-frame*) (print "\\n")
(assert (d77-snapshot? (d77-pack *dlm-model* *dlm-round* *dlm-events*)) "canonical snapshot")""")
            # Third step's previous checkpoint equals the explicit two-step save.
            path.write_bytes(Path(str(path) + '.previous').read_bytes())
            second = maru(f"""(dlm 'open {q})
(dump (d77-pack *dlm-model* *dlm-round* *dlm-events*)) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump *c88-frame*) (print "\\n")
(dlm 'close)""")
            self.assertEqual(loads_many(first), loads_many(second))

    def test_legacy_plain_route_still_uses_its_order_callback(self):
        out = maru("""
(dlm 'demo)
(define route-count90 0)
(define-function count-order90 (s facts) (set route-count90 (+ route-count90 1)) facts)
(set a83-order count-order90)
(a77-step *dlm-model* 0 1)
(assert (> route-count90 0) "legacy callback preserved")
(set route-count90 0)
(a77-step-canonical *dlm-model* 0 1)
(assert (= route-count90 0) "canonical path has no live callback")
(print "passed")""")
        self.assertEqual(out, 'passed')


if __name__ == '__main__':
    unittest.main()
