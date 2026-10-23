"""Generated alternatives execute in the real space79 nondeterministic machine."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_sequent import maru
from test_repl import Live
from sexp import loads_many

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/recursive-selfssl.sh'


class Recursive86Tests(unittest.TestCase):
    def test_generated_alternatives_fail_and_succeed_without_admitting(self):
        out = maru('''(dlm 'demo)
(define good '(definition77 good (edge edge) (compose edge edge)))
(define bad '(definition77 bad (edge edge) (compose missing edge)))
(define engine (s79-program-job (s79-new) 'p (n86-program *dlm-model* (list bad good))))
(set engine (s79-run engine 100))
(define records (n86-records engine))
(assert (= (car (car (s79-at records bad))) 'rejected) "failed branch recorded")
(assert (= (car (car (s79-at records good))) 'learned) "valid branch checked")
(assert (= (car (dlm-nth (s79-job engine 'p) 5)) 'provisional) "accept is not theorem admission")
(assert (not (a77-defs *dlm-model*)) "engine cannot mutate authoritative library")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_actual_recursive_learning_and_hindsight_branch_labels(self):
        out = maru('''(dlm 'demo) (dlm 'search 'nd-ucb)
(set *dlm-pair-budget* 4)
(times-do 3 (dlm 'step))
(assert (= (dlm-length (a77-defs *dlm-model*)) 3) "recursive definitions admitted")
(assert (> (dlm-nth *s84-control* 6) 3) "nonchosen checked branches also supervise policy")
(assert (> (dlm-nth *s84-control* 7) (dlm-nth *s84-control* 6)) "admission rechecks counted")
(assert (= (car (dlm-nth *s84-control* 12)) 'nd86) "real machine trace")
(assert (> (dlm-nth (dlm-nth *s84-control* 12) 2) 1) "multiple generated branches")
(assert (= (car (dlm 'query 'demo-a '(atom "c77-2" (a e)))) 'proved) "native recursive proof")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_bare_accept_cannot_bypass_native_gate(self):
        out = maru('''(dlm 'demo)
(define-function bare86 (model definitions) (list (list 'accept (car definitions))))
(set n86-program bare86)
(define r (n86-run *dlm-model* (a84-mode (a84-new) 'nd-cache) 4))
(assert (not (a77-defs (dlm-nth r 1))) "provisional without checked ticket is rejected")
(assert (= (car r) 'incomplete) "candidate remains pending")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_unknown_failure_is_retryable(self):
        out = maru('''(dlm 'demo)
(define original86 a77-certify)
(define-function unknown86 (model definition) '(rejected verification))
(set a77-certify unknown86)
(define r (n86-run *dlm-model* (a84-mode (a84-new) 'nd-cache) 4))
(assert (= (car r) 'incomplete) "no false refutation/saturation")
(assert (not (dlm-nth (dlm-nth r 2) 4)) "unknown not memoized")
(set a77-certify original86)
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_fresh_process_replays_machine_feedback_and_next_step(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.sexp'
            q = json.dumps(str(path))
            first = maru(f'''(dlm 'open {q}) (dlm 'demo) (dlm 'search 'nd-ucb)
(set *dlm-pair-budget* 4)
(dlm 'step) (dlm 'step) (dlm 'save)
(dump *s84-control*) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump *s84-control*) (print "\\n")''')
            self.assertIn('dlm-session86', path.read_text())
            path.write_bytes(Path(str(path) + '.previous').read_bytes())
            second = maru(f'''(dlm 'open {q})
(set *dlm-pair-budget* 4)
(dump *s84-control*) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump *s84-control*) (print "\\n")
(dlm 'close)''')
            self.assertEqual(loads_many(first), loads_many(second))

    def test_finite_shell_demo_and_restart_preserve_evidence_and_log(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.sexp'
            run = subprocess.run([str(SCRIPT), '--demo', '--rounds', '4', '--budget', '4', str(path)],
                                 text=True, capture_output=True, timeout=120)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            self.assertIn('branches 3', run.stdout)
            first = loads_many(path.read_text())[0]
            self.assertEqual(first[0], 'dlm-session86')
            self.assertEqual(len(first[2][2]), 2)
            self.assertEqual(len(first[2][3]), 3)
            again = subprocess.run([str(SCRIPT), '--demo', '--rounds', '1', str(path)],
                                   text=True, capture_output=True, timeout=120)
            self.assertEqual(again.returncode, 0, again.stderr + again.stdout)
            self.assertIn('Demo not injected', again.stdout)
            self.assertIn('waiting', again.stdout)
            second = loads_many(path.read_text())[0]
            self.assertEqual(first[4], second[4])  # No synthetic learning on saturation.
            self.assertEqual(first[2], second[2])

    def test_interactive_shell_is_one_original_native_repl_process(self):
        with tempfile.TemporaryDirectory() as directory:
            repl = Live([str(SCRIPT), '--demo', '--interval', '20', '--budget', '4',
                         str(Path(directory) / 'state.sexp')])
            try:
                repl.wait(rb'Defined ', seconds=20)
                repl.exchange("(dlm 'pause)", rb'paused')
                repl.exchange('(assert (= (car (dlm-nth *s84-control* 12)) \'nd86) "native loop")', rb'true')
                args = Path(f'/proc/{repl.p.pid}/cmdline').read_bytes()
                self.assertIn(b'experiments/repl/recursive86.l', args)
                self.assertIn(b'maru', args)
                repl.exchange("(dlm 'close)", rb'closed')
            finally:
                output = repl.close()
            self.assertEqual(repl.p.returncode, 0, output[-3000:])

    def test_cli_validation_and_corrupt_store_are_fail_closed(self):
        for args in (['--budget', '17'], ['--interval', '19'], ['--rounds', '0'],
                     ['--rounds', '08'], ['--bad-option']):
            result = subprocess.run([str(SCRIPT), *args], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'corrupt.sexp'
            original = b'(print "NOT-DATA")'
            path.write_bytes(original)
            result = subprocess.run([str(SCRIPT), '--rounds', '1', str(path)],
                                    capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
