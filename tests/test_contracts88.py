"""One native agenda, event log and checkpoint, not two cooperating processes."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_sequent import maru
from test_repl import Live
from sexp import loads_many

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/recursive-selfssl.sh'
X = "'(contract87 setx (x y) (bool 1) () (var x) (x))"
Y = "'(contract87 sety (x y) (bool 1) () (var y) (y))"
BOTH = "'(contract87 both (x y) (bool 1) () (and (var x) (var y)) (x y))"
SETUP = f"""(dlm 'demo) (dlm 'search 'nd-ucb)
(dlm 'goal {X}) (dlm 'goal {Y}) (dlm 'goal {BOTH})
(dlm 'curriculum 'mixed) (dlm 'relation-budget 4)"""


class Contracts88Tests(unittest.TestCase):
    def test_one_step_curriculum_learns_both_domains_and_reuses_modules(self):
        out = maru(SETUP + '''
(times-do 10 (dlm 'step))
(assert (= (dlm-length (a77-defs *dlm-model*)) 3) "native relations retained")
(assert (= (dlm-length (dlm-nth *c87-library* 1)) 3) "three checked procedures")
(assert (equal (dlm-nth (dlm-nth (c87-module *c87-library* 'both) 1) 4)
               '((call setx) (call sety))) "later goal uses earlier learned procedures")
(assert (= (dlm-nth (contracts 'check-library) 1) 'verified) "independent full library check")
(assert (= (car (dlm 'query 'demo-a '(atom "c77-2" (a e)))) 'proved) "original query still works")
(define log *dlm-events*) (dlm 'step) (dlm 'step)
(assert (equal log *dlm-events*) "waiting is not synthetic learning")
(assert (= (car *dlm-last*) 'waiting) "both domains saturated")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_fresh_process_restores_partial_frontier_control_budget_and_next_step(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'joint.sexp'
            q = json.dumps(str(path))
            first = maru(f'''(dlm 'open {q}) (dlm 'demo) (dlm 'search 'nd-ucb)
(dlm 'goal {X}) (dlm 'curriculum 'mixed)
(dlm 'contract-budget 1 2000) (dlm 'relation-budget 4)
(dlm 'step) (dlm 'step) (dlm 'save)
(dump (list *c88-frame* *s84-control* *dlm-round* *dlm-pair-budget*)) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump (list *c88-frame* *s84-control* *dlm-round* *dlm-pair-budget*)) (print "\\n")''')
            self.assertEqual(loads_many(path.read_text())[0][0], 'dlm-session88')
            path.write_bytes(Path(str(path) + '.previous').read_bytes())
            second = maru(f'''(dlm 'open {q})
(dump (list *c88-frame* *s84-control* *dlm-round* *dlm-pair-budget*)) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump (list *c88-frame* *s84-control* *dlm-round* *dlm-pair-budget*)) (print "\\n")
(dlm 'close)''')
            self.assertEqual(loads_many(first), loads_many(second))

    def test_plain_relation_cursor_is_also_checkpointed_in_joint_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'plain.sexp'
            q = json.dumps(str(path))
            first = maru(f'''(dlm 'open {q}) (dlm 'demo) (dlm 'curriculum 'relations)
(dlm 'relation-budget 1) (times-do 3 (dlm 'step))
(assert (= *dlm-cursor* 3) "native incomplete cursor") (dlm 'save)
(dump *c88-frame*) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump *c88-frame*) (print "\\n")''')
            path.write_bytes(Path(str(path) + '.previous').read_bytes())
            second = maru(f'''(dlm 'open {q})
(dump *c88-frame*) (print "\\n")
(dump (dlm 'step)) (print "\\n")
(dump *c88-frame*) (print "\\n") (dlm 'close)''')
            self.assertEqual(loads_many(first), loads_many(second))

    def test_first_joint_transaction_lazily_reconstructs_legacy_controller(self):
        out = maru(f'''(dlm 'demo) (dlm 'search 'nd-ucb)
(set *dlm-pair-budget* 4) (dlm 'step) (dlm 'step)
(define before (list *dlm-model* *s84-control*))
(assert (not (d88-log? *dlm-events*)) "legacy fast path retained")
(dlm 'goal {X})
(assert (equal before (list *dlm-model* *s84-control*)) "controller preserved on migration")
(assert (d77-snapshot? (d77-pack *dlm-model* *dlm-round* *dlm-events*)) "canonical joint replay")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_unknown_budget_is_blocked_not_refutation_and_retries_after_budget_change(self):
        out = maru(f'''(dlm 'goal {X}) (dlm 'curriculum 'contracts)
(dlm 'contract-budget 16 1) (dlm 'step)
(assert (not (dlm-nth *c87-library* 1)) "unknown cannot admit")
(assert (= (dlm-nth (car (dlm 'goals)) 2) 'blocked) "bounded attempt exhausted, not false")
(define log *dlm-events*) (times-do 3 (dlm 'step))
(assert (equal log *dlm-events*) "blocked goal not repeatedly run at idle")
(dlm 'contract-budget 4 2000) (dlm 'step)
(assert (c87-module *c87-library* 'setx) "new verification budget retries from start")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_new_checked_library_reopens_generation_bound_goal(self):
        out = maru('''(dlm 'goal '(contract87 hard (x y z) (bool 1) () (and (var x) (var y)) (x y)))
(dlm 'curriculum 'contracts) (dlm 'contract-budget 16 2000) (dlm 'step)
(assert (= (dlm-nth (car (dlm 'goals)) 2) 'blocked) "finite grammar did not solve goal")
(assert (= (car (contracts 'admit
 '(contract87 helper (x y z) (bool 1) ((assign x (bool 1)) (assign y (bool 1)))
   (and (var x) (var y)) (x y)))) 'admitted87) "explicit independently verified summary")
(dlm 'step)
(assert (c87-module *c87-library* 'hard) "library context change reopens obligation")
(assert (equal (dlm-nth (dlm-nth (c87-module *c87-library* 'hard) 1) 4) '((call helper))) "summary reused")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_empty_precondition_is_terminal_inapplicable_not_a_learned_solution(self):
        out = maru('''(dlm 'goal '(contract87 vacuous (x) (and (var x) (not (var x))) () (bool 0) (x)))
(dlm 'curriculum 'contracts) (dlm 'step)
(assert (= (car *dlm-last*) 'contract-inapplicable) "nonvacuity")
(assert (not (dlm-nth *c87-library* 1)) "no false success")
(define log *dlm-events*) (dlm 'step)
(assert (equal log *dlm-events*) "no repeated unreachable obligations")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_search_tickets_and_theorems_for_another_goal_cannot_admit(self):
        out = maru(f'''(dlm 'goal {X}) (dlm 'curriculum 'contracts)
(define-function forged88 (candidates lib fuel)
  (list 'synthesized87 (car candidates) '(certificate87 forged) '(search87 branches 1 events 1 outcomes ())))
(set c87-search forged88) (dlm 'step)
(assert (not (dlm-nth *c87-library* 1)) "independent final gate rejects bogus proof")
(define weak '(contract87 setx (x y) (bool 1) () (bool 1) (x)))
(define weakproof (dlm-nth (c87-verify weak (c87-empty) 2000) 1))
(define-function wronggoal88 (candidates lib fuel)
  (list 'synthesized87 weak weakproof '(search87 branches 1 events 1 outcomes ())))
(set c87-search wronggoal88) (dlm 'step)
(assert (not (dlm-nth *c87-library* 1)) "valid proof for weaker spec cannot discharge requested goal")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_tampered_goals_libraries_events_and_version_downgrade_are_rejected(self):
        out = maru(f'''(dlm 'goal {X}) (dlm 'curriculum 'contracts)
(define snapshot (d77-pack *dlm-model* *dlm-round* *dlm-events*))
(assert (d77-snapshot? snapshot) "valid joint snapshot")
(define state (dlm-nth snapshot 5))
(define forged-goal (s79-field (car (dlm-nth state 4)) 2 'solved))
(assert (not (d77-snapshot? (s79-field snapshot 5 (s79-field state 4 (list forged-goal))))) "cache is not approval")
(assert (not (d77-snapshot? (list 'dlm-session86 1 *dlm-model* *dlm-round* *dlm-events*))) "no tag downgrade")
(define injected (c88-replay (dlm-append *dlm-events* '((contract-run88 learned)))))
(assert (not (= (car injected) 'replayed)) "no injected result")
(define badlib (c88-replay (dlm-append *dlm-events* '((library88 (library87 ((module87 bad fake))))))))
(assert (not (= (car badlib) 'replayed)) "bad module")
(dlm 'step)
(set snapshot (d77-pack *dlm-model* *dlm-round* *dlm-events*))
(assert (not (d77-snapshot? (s79-field snapshot 5 (s79-field (dlm-nth snapshot 5) 3 (c87-empty))))) "library cannot be erased independently")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_checkpoint_failure_rolls_back_round_library_goal_and_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            q = json.dumps(str(Path(directory) / 'joint.sexp'))
            out = maru(f'''(dlm 'open {q}) (dlm 'goal {X}) (dlm 'curriculum 'contracts)
(define before (list *c88-frame* *dlm-model* *dlm-events* *dlm-round* *s84-control*))
(define original-checkpoint d77-checkpoint)
(define-function refuse88 (path snapshot) false)
(set d77-checkpoint refuse88) (dlm 'step)
(assert (equal before (list *c88-frame* *dlm-model* *dlm-events* *dlm-round* *s84-control*)) "no partial publication")
(assert (not *dlm-running*) "pause on storage failure")
(set d77-checkpoint original-checkpoint) (dlm 'step)
(assert (c87-module *c87-library* 'setx) "retry after repair")
(dlm 'close) (print "passed")''')
            self.assertEqual(out, 'passed')

    def test_manual_contract_learning_is_persisted_by_dlm_save_and_reset_is_joint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'joint.sexp'
            q = json.dumps(str(path))
            self.assertEqual(maru(f'''(dlm 'open {q}) (dlm 'demo)
(contracts 'learn {X}) (dlm 'close) (print "saved")'''), 'saved')
            snapshot = loads_many(path.read_text())[0]
            self.assertEqual(snapshot[0], 'dlm-session88')
            out = maru(f'''(dlm 'open {q})
(assert (c87-module *c87-library* 'setx) "no separate contract load needed")
(assert (= (dlm-length (a77-episodes *dlm-model*)) 2) "same native source model")
(dlm 'goal {Y}) (dlm 'reset)
(assert (not (dlm 'goals)) "reset clears agenda")
(assert (not (dlm-nth *c87-library* 1)) "reset clears procedures")
(assert (not (a77-episodes *dlm-model*)) "reset clears native observations")
(dlm 'close) (print "passed")''')
            self.assertEqual(out, 'passed')

    def test_legacy_open_cannot_silently_discard_live_contract_state(self):
        with tempfile.TemporaryDirectory() as directory:
            q = json.dumps(str(Path(directory) / 'legacy.sexp'))
            maru(f"(dlm 'open {q}) (dlm 'save) (dlm 'close)")
            out = maru(f'''(contracts 'learn {X})
(assert (= (car (dlm 'open {q})) 'rejected) "require reset before overwriting contract state")
(assert (c87-module *c87-library* 'setx) "library preserved")
(dlm 'reset)
(assert (= (car (dlm 'open {q})) 'dlm77) "legacy codec still readable")
(dlm 'close) (print "passed")''')
            self.assertEqual(out, 'passed')

    def test_request_limit_is_preflighted_and_pauses_without_an_event_or_round(self):
        out = maru('''(list-do name '(limit0 limit1 limit2 limit3 limit4 limit5 limit6)
  (dlm 'goal (list 'contract87 name '(x) '(bool 1) () '(bool 0) '(x))))
(dlm 'curriculum 'contracts) (dlm 'contract-budget 16 200000)
(times-do 6 (dlm 'step))
(define before (list *c88-frame* *dlm-model* *dlm-events* *dlm-round*))
(dlm 'start 20) (dlm 'step)
(assert (equal before (list *c88-frame* *dlm-model* *dlm-events* *dlm-round*)) "preflight before seventh work item")
(assert (not *dlm-running*) "idle pause, not repeated refusal")
(assert (equal *dlm-last* '(rejected88 contract-request-limit)) "resource unknown, not refuted")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_finite_shell_joint_store_restart_and_config_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'joint store.sexp'
            run = subprocess.run([str(SCRIPT), '--demo', '--contracts-demo', '--rounds', '12',
                                  '--budget', '4', str(path)], text=True, capture_output=True, timeout=120)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            self.assertIn('Verified procedure both88: ((call setx88) (call sety88))', run.stdout)
            before = loads_many(path.read_text())[0]
            self.assertEqual(before[0], 'dlm-session88')
            self.assertEqual(len(before[2][3]), 3)
            self.assertEqual(len(before[5][3][1]), 3)
            again = subprocess.run([str(SCRIPT), '--demo', '--contracts-demo', '--rounds', '1', str(path)],
                                   text=True, capture_output=True, timeout=120)
            self.assertEqual(again.returncode, 0, again.stderr + again.stdout)
            self.assertIn('Contract demo not injected', again.stdout)
            after = loads_many(path.read_text())[0]
            self.assertEqual(before[4:], after[4:])  # Budget four survives default CLI budget eight.
            self.assertEqual(before[2], after[2])
            for args in (['--contract-batch', '17'], ['--contract-fuel', '0'],
                         ['--contract-fuel', '200001'], ['--curriculum', 'invalid']):
                p = subprocess.run([str(SCRIPT), *args], capture_output=True, timeout=10)
                self.assertEqual(p.returncode, 2)

    def test_original_repl_idle_performs_contract_learning_in_one_process(self):
        with tempfile.TemporaryDirectory() as directory:
            repl = Live([str(SCRIPT), '--contracts-demo', '--interval', '20',
                         str(Path(directory) / 'joint.sexp')])
            try:
                repl.wait(rb'Verified procedure both88:', seconds=30)
                repl.exchange("(dlm 'pause)", rb'paused')
                repl.exchange('(assert (= (dlm-length (dlm-nth *c87-library* 1)) 3) "shared learning")', rb'true')
                repl.exchange("(dlm 'close)", rb'closed')
            finally:
                output = repl.close()
            self.assertEqual(repl.p.returncode, 0, output[-3000:])


if __name__ == '__main__':
    unittest.main()
