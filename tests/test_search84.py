"""Native search-control invariants and real original-REPL integration."""
import json
from pathlib import Path
import tempfile
import unittest
from test_sequent import maru
from test_repl import Live
from sexp import loads_many

RARE = '''(dlm 'observe 'rare '((atom edge (a b)) (atom edge (b c))
 (atom edge (c d)) (atom edge (d e)) (atom edge (u v)) (atom edge (v w))
 (atom edge (w x)) (atom edge (j k)) (atom edge (k l)) (atom edge (l m))))
(dlm 'step) (dlm 'step)
'''


class Search84Tests(unittest.TestCase):
    def test_indexed_search_and_native_proof_gate(self):
        out = maru('''(dlm 'demo) (dlm 'search 'ucb)
(set *dlm-pair-budget* 1)
(times-do 3 (dlm 'step))
(assert (= (dlm-length (a77-defs *dlm-model*)) 3) "recursive definitions")
(assert (= (dlm-nth *s84-control* 7) 3) "one certification per round")
(assert (= (car (dlm 'query 'demo-a '(atom "c77-2" (a e)))) 'proved) "kernel-approved query")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_negative_transpositions_and_evidence_invalidation(self):
        out = maru(RARE + '''(dlm 'search 'cache)
(set *dlm-pair-budget* 1)
(times-do 4 (dlm 'step))
(assert (= (dlm-nth *s84-control* 7) 1) "one full insufficient-reuse check")
(assert (>= (dlm-nth *s84-control* 8) 1) "different splits share negative result")
(assert (= (dlm-length (a77-defs *dlm-model*)) 2) "one rare path is insufficient")
(dlm 'observe 'more '((atom edge (n o)) (atom edge (o p)) (atom edge (p q)) (atom edge (q r))))
(dlm 'step)
(assert (= (dlm-length (a77-defs *dlm-model*)) 3) "evidence change invalidates stale rejection")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_verification_failure_is_not_memoized(self):
        out = maru('''(dlm 'demo)
(define original84 a77-certify)
(define-function fail84 (model candidate) '(rejected verification))
(set a77-certify fail84)
(define r (a84-run *dlm-model* (a84-mode (a84-new) 'cache) 1))
(assert (not (dlm-nth (dlm-nth r 2) 4)) "incomplete/verification failure is not a logical negative")
(assert (= (car r) 'incomplete) "uncertain verification cannot imply saturation")
(assert (dlm-nth (dlm-nth r 2) 3) "uncertain candidate remains retryable")
(set a77-certify original84)
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_fixed_point_ucb_explores_untried_family(self):
        out = maru('''(define c (a84-mode (a84-new) 'ucb))
(define a '((edge edge) (compose edge edge) 1 1))
(define b '((edge edge edge) (compose edge c) 1 2))
(set c (s79-field c 5 (list (list '(2 1 1) '(10 20 100)))))
(set c (s79-field c 6 10))
(assert (> (a84-score c b) (a84-score c a)) "untried family exploration")
(assert (= (a84-sqrt 65536) 256) "deterministic integer sqrt")
(assert (= (a84-log2 16) 4) "integer logarithm")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_persistent_statistics_and_next_step_match_fresh_process(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 's.sexp'
            q = json.dumps(str(path))
            first = maru(f'''(dlm 'open {q}) (dlm 'demo) (dlm 'search 'ucb)
(set *dlm-pair-budget* 1)
(dlm 'step) (dlm 'save)
(dump *s84-control*) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump *s84-control*) (print "\\n")''')
            self.assertIn('dlm-session86', path.read_text())  # Public commands use the current explicit format.
            path.write_bytes(Path(str(path) + '.previous').read_bytes())
            restored = maru(f'''(dlm 'open {q})
(set *dlm-pair-budget* 1)
(dump *s84-control*) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump *s84-control*) (print "\\n")
(dlm 'close)''')
            self.assertEqual(loads_many(first), loads_many(restored))

    def test_saturation_wait_state_restores(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 's.sexp'
            q = json.dumps(str(path))
            first = maru(f'''(dlm 'open {q}) (dlm 'demo) (dlm 'search 'cache)
(times-do 4 (dlm 'step))
(dlm 'save)
(dump (dlm 'step))''')
            restored = maru(f'''(dlm 'open {q})
(dump (dlm 'step))
(dlm 'close)''')
            self.assertEqual(loads_many(first), loads_many(restored))
            self.assertEqual(loads_many(restored)[0][2][0], 'waiting')

    def test_bad_events_and_checkpoint_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 's.sexp'
            q = json.dumps(str(path))
            out = maru(f'''(dlm 'open {q}) (dlm 'demo) (dlm 'search 'ucb)
(define before *s84-control*) (define model-before *dlm-model*)
(d77-write {q} '(corrupt))
(dlm 'step)
(assert (equal before *s84-control*) "controller not published after failed save")
(assert (equal model-before *dlm-model*) "model rollback")
(assert (= (car (d77-replay '((search84 ucb) (search84-run -1)))) 'rejected) "bad budget")
(print "passed")''')
            self.assertEqual(out, 'passed')

    def test_live_budget_guard_matches_replay_bound(self):
        out = maru('''(define events84 ())
(times-do 100 (set events84 (cons '(search84-run 1000) events84)))
(assert (not (s84-admit '(search84-run 1) events84)) "live cap matches replay cap")
(assert (s84-admit '(search84 off) events84) "can disable at budget cap")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_original_idle_repl_uses_search_controller(self):
        repl = Live()
        try:
            repl.exchange("(dlm 'demo)", rb'observed demo-b')
            repl.exchange("(dlm 'search 'ucb)", rb'search84 ucb')
            repl.exchange("(dlm 'start 20)", rb'dlm77 running')
            repl.wait(rb'Defined ', seconds=8)
            repl.exchange("(dlm 'pause)", rb'paused')
            repl.exchange('(assert (> (dlm-nth *s84-control* 7) 0) "real idle search")', rb'true')
        finally:
            repl.close()


if __name__ == '__main__':
    unittest.main()
