"""Actual DLM77 REPL step/idle/restore integration, not a standalone demo."""
import json
from pathlib import Path
import tempfile
import unittest

from test_sequent import maru
from test_session77 import batch
from test_repl import Live
from sexp import loads_many


class Bridge83Tests(unittest.TestCase):
    def test_next_round_uses_previous_verified_cache(self):
        out = maru('''(dlm 'demo) (dlm 'ground 'on)
(dlm 'step)
(define first *g83-space*)
(assert (= (dlm-length (dlm-nth first 2)) 2) "only explicit sources are evidence")
(assert (> (dlm-length (dlm-nth first 3)) 8) "derived facts accumulated")
(define calls *g83-orders*)
(dlm 'step)
(assert (> *g83-orders* calls) "next step consumed prior cache")
(assert (> *g83-hits* 0) "actual candidate routing hits")
(assert (= (dlm-length (dlm-nth *g83-space* 2)) 2) "own output never observation")
(define result (dlm 'query 'demo-a '(atom "c77-0" (a c))))
(assert (= (car result) 'proved) "cached native proof")
(assert (= *g83-query-hits* 1) "retrieved and reverified proof")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_retract_removes_stale_episode_support(self):
        out = maru('''(dlm 'demo) (dlm 'ground 'on) (dlm 'step)
(dlm 'retract 'demo-a)
(assert (= (dlm-length (dlm-nth *g83-space* 2)) 1) "source removed on rebuild")
(assert (= (car (dlm 'query 'demo-a '(atom "c77-0" (a c)))) 'unknown-episode) "no stale result")
(assert (= (car (dlm 'query 'demo-b '(atom "c77-0" (u w)))) 'proved) "independent source")
(assert (= (dlm-length (a77-defs *dlm-model*)) 1) "definitions not observations")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_saved_mode_cache_and_next_step_restore_in_new_process(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 's.sexp'
            q = json.dumps(str(path))
            first = maru(f'''(dlm 'open {q}) (dlm 'demo) (dlm 'ground 'on) (dlm 'step)
(dump (list *g83-space* *g83-map*)) (print "\\n")
(dlm 'save)
(dump (dlm 'step)) (print "\\n")
''')
            self.assertIn('dlm-session83', path.read_text())
            # Copy the first-step checkpoint: step above also checkpoints step two.
            previous = Path(str(path) + '.previous')
            path.write_bytes(previous.read_bytes())
            restored = maru(f'''(dlm 'open {q})
(dump (list *g83-space* *g83-map*)) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dlm 'close)''')
            self.assertEqual(loads_many(first), loads_many(restored))

    def test_unsupported_projection_falls_back_without_changing_learning(self):
        out = maru('''(dlm 'observe 'numeric '((atom edge (1 2)) (atom edge (2 3))
 (atom edge (3 4)) (atom edge (4 5))))
(dlm 'ground 'on)
(assert (= *g83-status* 'unavailable) "projection not supported")
(dlm 'step)
(assert (= (dlm-length (a77-defs *dlm-model*)) 1) "native learner still operates")
(assert (= (car (dlm 'query 'numeric '(atom "c77-0" (1 3)))) 'proved) "native query fallback")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_invalid_mode_does_not_commit(self):
        out = maru('''(dlm 'demo)
(define old *dlm-events*)
(assert (= (car (dlm 'ground 'bogus)) 'rejected) "invalid mode")
(assert (equal old *dlm-events*) "no rejected event")
(dlm 'ground 'on) (dlm 'step) (dlm 'ground 'off)
(assert (not *g83-enabled*) "explicit ablation")
(assert (not *g83-map*) "no hidden cache on off arm")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_idle_learning_in_original_repl(self):
        repl = Live()
        try:
            repl.exchange("(dlm 'demo)", rb'observed demo-b')
            repl.exchange("(dlm 'ground 'on)", rb'ground83 ready')
            repl.exchange("(dlm 'start 20)", rb'dlm77 running')
            repl.wait(rb'Defined ', seconds=8)
            repl.exchange("(dlm 'ground)", rb'candidate-cache-hits')
            repl.exchange("(dlm 'pause)", rb'paused')
            repl.exchange("(assert (> *g83-orders* 0) \"idle route\")", rb'true')
        finally:
            repl.close()


if __name__ == '__main__':
    unittest.main()
