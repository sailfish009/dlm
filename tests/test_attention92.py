"""CPU-native declarative control, independent finite answer/witness oracle."""
import itertools
import json
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

from test_sequent import maru
from test_repl import Live
from sexp import Symbol as S, dumps, loads_many
from test_basis91 import reference

ROOT = Path(__file__).resolve().parents[1]
SETUP = '(require "experiments/attention92/setup.l")\n'
START = "(attention92 'start (basis91 'model) 'train '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)\n"
POLICIES = ('ordered92', 'indexed92', 'adaptive92', 'narrow92')


def answers(result, facts):
    if result[0] != 'attention-result92' or result[1] != 'complete':
        raise AssertionError(result)
    pattern, rows = result[2:4]
    found = set()
    for tag, values, ids in rows:
        if tag != 'match91' or len(ids) != len(pattern):
            raise AssertionError(rows)
        for (pred, a, b), i in zip(pattern, ids):
            if facts[i] != [S('atom'), pred, [values[a], values[b]]]:
                raise AssertionError((values, ids, facts))
        found.add(tuple(values))
    if len(found) != len(rows):
        raise AssertionError('duplicate bindings')
    return found


class Attention92Tests(unittest.TestCase):
    def test_hierarchical_basis_dispatch_and_no_training_archive_dependency(self):
        out = maru(SETUP + """
(define model (basis91 'model)) (basis91 'init '(edge))
(define-function disabled92 args (error "no archive/discovery needed"))
(set b91-replay disabled92) (set b91-state? disabled92) (set b91-evidence disabled92)
(set b91-propose disabled92) (set b91-data-patterns disabled92)
(define r (attention92 'query model 'train '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000))
(assert (= (dlm-nth r 1) 'complete)) (assert (= (dlm-length (dlm-nth r 3)) 2))
(assert (equal (dlm-nth r 5) '((call91 2 (0 1 2 3)))))
(assert (equal (dlm-nth (dlm-nth r 4) 12) '(2 1)) "actual nested dispatch")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_data_context_changes_plan_and_intermediate_bindings_route_it(self):
        rows = loads_many(maru(SETUP + """
(list-do ep '(train dense)
 (dump (attention92 'query (basis91 'model) ep '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)) (print "\n"))
"""))
        self.assertEqual(rows[0][5], [[S('call91'), 2, [0, 1, 2, 3]]])
        self.assertEqual(rows[1][5], [[S('fact91'), S('t'), [2, 3]], [S('fact91'), S('s'), [1, 2]], [S('fact91'), S('r'), [0, 1]]])
        choices = [t for t in rows[1][6] if t[1] == [S('choose92')]]
        self.assertEqual([t[5][1] for t in choices], [[7], [4], [0]])
        self.assertEqual(rows[1][4][5], 3)

    def test_all_controls_same_witnesses_but_actual_read_counts_differ(self):
        rows = loads_many(maru(SETUP + """
(list-do policy '(ordered92 indexed92 adaptive92 narrow92)
 (dump (attention92 'query (basis91 'model) 'dense '((r 0 1) (s 1 2) (t 2 3)) policy 200000)) (print "\n"))
"""))
        for r in rows:
            self.assertEqual(r[1], 'complete')
            self.assertEqual(r[3], rows[0][3])
        self.assertLess(rows[2][4][5], rows[0][4][5])
        self.assertLess(rows[2][4][5], rows[1][4][5])
        self.assertGreater(rows[2][4][8], 0)  # verification is NOT free

    def test_partial_empty_is_pending_then_widen_not_global_negative(self):
        out = maru(SETUP + START + """
(attention92 'step '(focus92 train 1 2 (0) (2) (call91 2 (0 1 2 3))))
(attention92 'tick)
(assert (= (dlm-nth (attention92 'result) 1) 'pending))
(assert (not (dlm-nth (attention92 'result) 3)) "no provisional publication")
(attention92 'tick)
(assert (= (dlm-nth (a92-work *a92-state*) 7) 'need-widen))
(assert (equal (dlm-nth (a92-work *a92-state*) 3) '(())) "old workspace retained")
(define r (attention92 'run 64))
(assert (= (dlm-nth r 1) 'complete)) (assert (= (dlm-length (dlm-nth r 3)) 2))
(assert (= (dlm-nth (dlm-nth r 4) 9) 1)) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_poisoned_index_cannot_hide_missing_premises_from_checker(self):
        out = maru(SETUP + """
(define-function empty92 (index atom env) ()) (set a92-lookup empty92)
(define r (attention92 'query (basis91 'model) 'train '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000))
(assert (= (dlm-nth r 1) 'complete)) (assert (= (dlm-length (dlm-nth r 3)) 2))
(assert (> (dlm-nth (dlm-nth r 4) 9) 0)) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_independent_local_gate_uses_neither_policy_index_nor_new_worker(self):
        out = maru(SETUP + START + """
(attention92 'run 2)
(define-function disabled92 args (error "independent checker must not call this"))
(set a92-choice disabled92) (set a92-options disabled92) (set a92-index disabled92)
(set a92-lookup disabled92) (set a92-execute disabled92)
(assert (= (car (attention92 'step '(local92))) 'attention92))
(assert (= (dlm-nth (a92-work *a92-state*) 7) 'local)) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_wrong_and_omitted_worker_rows_cannot_be_admitted(self):
        for value in (
                "'(((0 a) (1 c) (2 b) (3 d)))", "'()",
                "'(((0 a) (1 b) (2 c) (3 d) (99 foreign)) ((0 p) (1 q) (2 z) (3 w)))",
                "'(((0 a) (0 fake) (1 b) (2 c) (3 d)) ((0 p) (1 q) (2 z) (3 w)))"):
            with self.subTest(value=value):
                out = maru(SETUP + START + f"""
(attention92 'tick)
(define-function liar92 (op ep lib scope envs r) (a92-computed 'complete {value} r))
(set a92-execute liar92) (attention92 'tick)
(define before *a92-state*)
(assert (= (car (attention92 'tick)) 'rejected92) "wrong/omitted answers")
(assert (equal before *a92-state*) "no local publication")
(assert (= (dlm-nth (attention92 'result) 1) 'pending)) (print "passed")""")
                self.assertEqual(out, 'passed')

    def test_typed_commands_reject_unknown_negative_duplicate_and_stale_ids(self):
        out = maru(SETUP + START + """
(define valid '(focus92 train 1 2 (0 1 2 3 4 5) (2) (call91 2 (0 1 2 3))))
(define before *a92-state*)
(list-do cmd (list (s79-field valid 1 'missing) (s79-field valid 2 99) (s79-field valid 3 99)
 (s79-field valid 4 '(99)) (s79-field valid 4 '(-1)) (s79-field valid 4 '(0 0))
 (s79-field valid 4 '("1")) (s79-field valid 5 '(99)) (s79-field valid 5 ())
 (s79-field valid 6 '(fact91 s (0 2))) '(apply92) '(local92) '(restore92) '(finish92))
 (assert (= (car (attention92 'step cmd)) 'rejected92)) (assert (equal before *a92-state*)))
(attention92 'step valid)
(assert (equal (dlm-nth (dlm-nth (a92-work *a92-state*) 4) 2) '(1 2)) "dependency closure")
(assert (not (a92-envs? '(((0 a) (0 a) (1 b))))))
(assert (not (a92-envs? '(((0 a) (99 b))))))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_nested_scopes_restore_pending_intent_not_discard_verified_bindings(self):
        out = maru(SETUP + """
(attention92 'start (basis91 'model) 'train '((r 0 1) (s 1 2)) 'adaptive92 200000)
(attention92 'step '(focus92 train 1 2 (0 3) () (fact91 r (0 1))))
(attention92 'step '(focus92 train 1 2 (1 4) () (fact91 s (1 2))))
(attention92 'tick) (attention92 'tick)
(assert (a92-snapshot? (attention92 'snapshot)) "noncontiguous partial variable roles")
(attention92 'step '(restore92))
(assert (= (dlm-nth (a92-work *a92-state*) 7) 'focused))
(assert (equal (a92-pending-op (a92-work *a92-state*)) '(fact91 r (0 1))))
(assert (= (dlm-length (dlm-nth (a92-work *a92-state*) 3)) 2))
(define r (attention92 'run 64))
(assert (= (dlm-nth r 1) 'complete)) (assert (= (dlm-length (dlm-nth r 3)) 2))
(assert (not (dlm-nth (a92-work *a92-state*) 5))) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_aborted_provisional_work_does_not_mutate_workspace(self):
        out = maru(SETUP + START + """
(define old (dlm-nth (a92-work *a92-state*) 3))
(attention92 'run 2) (attention92 'step '(restore92))
(assert (equal old (dlm-nth (a92-work *a92-state*) 3)))
(assert (= (dlm-nth (a92-work *a92-state*) 7) 'ready))
(assert (= (dlm-nth (attention92 'run 64) 1) 'complete)) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_budget_exhaustion_in_worker_or_checker_never_publishes_answers(self):
        out = maru(SETUP + """
(list-do fuel '(0 6 20 60)
 (define r (attention92 'query (basis91 'model) 'train '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 fuel))
 (assert (= (dlm-nth r 1) 'unknown)) (assert (not (dlm-nth r 3))))
(attention92 'start (basis91 'model) 'train '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 60)
(attention92 'run 64)
(assert (> (dlm-nth (dlm-nth (a92-work *a92-state*) 9) 8) 0) "checker exhausted")
(assert (not (dlm-nth (a92-work *a92-state*) 2)) "no partial commit")
(assert (a92-snapshot? (attention92 'snapshot))) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_goal_and_role_changes_no_transitivity_or_silent_projection(self):
        out = maru("""
(basis91 'init '(r s))
(basis91 'observe 'g '((atom r (a b)) (atom r (b c)) (atom s (b a)) (atom s (a d))))
(list-do p '(((r 0 1)) ((r 0 1) (s 1 0)) ((r 0 1) (s 0 2)) ((r 0 0)))
 (dump (attention92 'query (basis91 'model) 'g p 'adaptive92 200000)) (print "\n"))
""")
        results = loads_many(out)
        self.assertEqual({tuple(r[1]) for r in results[0][3]}, {('a', 'b'), ('b', 'c')})
        self.assertEqual({tuple(r[1]) for r in results[1][3]}, {('a', 'b')})
        self.assertEqual({tuple(r[1]) for r in results[2][3]}, {('a', 'b', 'd'), ('b', 'c', 'a')})
        self.assertFalse(results[3][3])

    def test_query_and_inspection_cannot_modify_learner_or_other_models(self):
        out = maru(SETUP + START + """
(define old (list *b91-state* *b90-state* *dlm-model* *dlm-events* *s79-space* *c87-library* *a92-state*))
(attention92 'proposal)
(attention92 'query (basis91 'model) 'dense '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)
(assert (equal old (list *b91-state* *b90-state* *dlm-model* *dlm-events* *s79-space* *c87-library* *a92-state*)))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_retraction_new_context_rejects_old_commands_no_stale_table(self):
        out = maru(SETUP + START + """
(define old-command (attention92 'proposal)) (define historical (basis91 'model))
(basis91 'retract 'train) (basis91 'observe 'train '((atom r (a b))))
(attention92 'start (basis91 'model) 'train '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)
(assert (= (car (attention92 'step old-command)) 'rejected92))
(define r (attention92 'run 64)) (assert (= (dlm-nth r 1) 'complete)) (assert (not (dlm-nth r 3)))
; Explicit frozen models support historical inference, NOT automatic revocation.
(assert (= (dlm-length (dlm-nth (attention92 'query historical 'train '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000) 3)) 2))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_snapshot_replay_detects_forged_rows_plan_scope_metrics_and_history(self):
        out = maru(SETUP + START + """
(attention92 'run 3) (define x (attention92 'snapshot)) (define w (dlm-nth x 3))
(assert (a92-snapshot? x))
(list-do bad (list (s79-field w 1 '((r 0 1))) (s79-field w 2 '((fact91 r (0 1))))
 (s79-field w 3 '(((0 fake)))) (s79-field w 4 '(scope92 (99) ()))
 (s79-field w 8 200000) (s79-field w 9 ()) (s79-field w 10 ()))
 (assert (not (a92-snapshot? (s79-field x 3 bad)))))
(assert (not (a92-snapshot? (s79-field x 4 (cdr (dlm-nth x 4))))))
(define before *a92-state*)
(assert (= (car (attention92 'restore (s79-field x 3 (s79-field w 3 ())))) 'rejected92))
(assert (equal before *a92-state*)) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_same_next_choice_and_complete_state_after_fresh_process_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            q = json.dumps(str(Path(directory) / 'attention.sexp'))
            first = maru(SETUP + START + f"(attention92 'run 2) (attention92 'open {q}) (attention92 'save) (attention92 'close)\n" + """
(dump (attention92 'snapshot)) (print "\n") (dump (attention92 'proposal)) (print "\n")
(dump (attention92 'run 64)) (print "\n") (dump (attention92 'snapshot)) (print "\n")
""")
            second = maru(f"(attention92 'open {q})\n" + """
(dump (attention92 'snapshot)) (print "\n") (dump (attention92 'proposal)) (print "\n")
(dump (attention92 'run 64)) (print "\n") (dump (attention92 'snapshot)) (print "\n") (attention92 'close)
""")
            self.assertEqual(loads_many(first), loads_many(second))

    def test_checkpoint_failure_external_change_atomicity_and_failed_close(self):
        with tempfile.TemporaryDirectory() as directory:
            q = json.dumps(str(Path(directory) / 'attention.sexp'))
            out = maru(SETUP + START + f"(attention92 'open {q}) (attention92 'save)\n" + """
(define before (list *a92-state* *a92-expected*)) (define original92 a92-checkpoint)
(define-function no92 (p s e) false) (set a92-checkpoint no92)
(assert (= (car (attention92 'tick)) 'rejected92))
(assert (equal before (list *a92-state* *a92-expected*)))
(assert (= (car (attention92 'close)) 'rejected92)) (assert *a92-path*)
(set a92-checkpoint original92) (attention92 'tick)
(d77-write *a92-path* '(corrupt92)) (set before *a92-state*)
(assert (= (car (attention92 'tick)) 'rejected92)) (assert (equal before *a92-state*))
(print "passed")""")
            self.assertEqual(out, 'passed')
            before = Path(json.loads(q)).read_bytes()
            self.assertEqual(maru(f"(assert (= (car (attention92 'open {q})) 'rejected92)) (print \"passed\")"), 'passed')
            self.assertEqual(Path(json.loads(q)).read_bytes(), before)

    def test_two_process_lock_failed_close_retention_and_release(self):
        with tempfile.TemporaryDirectory() as directory:
            q = json.dumps(str(Path(directory) / 'attention.sexp'))
            live = Live()
            try:
                live.exchange(f'(begin {SETUP} {START} (attention92 \'open {q}))', rb'\(attention92 phase ready')
                live.exchange("(attention92 'save)", rb'\(saved92\)')
                blocked = f"(assert (equal (attention92 'open {q}) '(rejected92 locked-or-path))) (print \"passed\")"
                self.assertEqual(maru(blocked), 'passed')
                live.send('(define original92 a92-checkpoint)\n(define-function no92 (p s e) false)\n(set a92-checkpoint no92)\n')
                live.exchange("(attention92 'close)", rb'\(rejected92 checkpoint\)')
                self.assertEqual(maru(blocked), 'passed')
                live.send('(set a92-checkpoint original92)\n')
                live.exchange("(attention92 'close)", rb'\(closed92\)')
                self.assertEqual(maru(f"(assert (= (car (attention92 'open {q})) 'attention92)) (attention92 'close) (print \"passed\")"), 'passed')
            finally:
                output = live.close()
            self.assertEqual(live.p.returncode, 0, output[-4000:])

    def test_scope_depth_and_event_limits_fail_closed(self):
        out = maru(SETUP + START + """
(define cmd '(focus92 train 1 2 (0 1 2 3 4 5) (2) (call91 2 (0 1 2 3))))
(times-do 4 (attention92 'step cmd)) (define before *a92-state*)
(assert (= (car (attention92 'step cmd)) 'rejected92)) (assert (equal before *a92-state*))
(times-do 4 (attention92 'step '(restore92)))
(times-do 56 (attention92 'step '(global92)))
(set before *a92-state*)
(assert (= (car (attention92 'step '(global92))) 'rejected92))
(assert (equal before *a92-state*)) (assert (a92-snapshot? (attention92 'snapshot))) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_seeded_malformed_trees_do_not_crash_or_mutate(self):
        rng = random.Random(92)
        atoms = [42, -1, 'not executable (error)', []] + list(map(S, ('attention-session92', 'context92', 'focus92', 'call91', 'r', 'work92')))
        def tree(depth):
            if depth == 0 or rng.random() < .55:
                return rng.choice(atoms)
            return [tree(depth - 1) for _ in range(rng.randrange(9))]
        out = maru(SETUP + START + """
(define before *a92-state*)
(list-do x (read *standard-input*)
 (a92-context? x) (a92-snapshot? x) (a92-envs? x) (a92-focus? x *a92-state*)
 (attention92 'step x) (attention92 'restore x))
(assert (equal before *a92-state*)) (print "passed")""", dumps([tree(4) for _ in range(500)]))
        self.assertEqual(out, 'passed')

    def test_data_input_is_not_code_and_rejects_trailing_data(self):
        data = (ROOT / 'experiments/attention92/input-example.sexp').read_text()
        for payload, success in ((data, True), (data + '(error "never execute")', False), ('(error "never execute")', False)):
            p = subprocess.run([str(ROOT / 'scripts/run.sh'), 'attention92-input'], input=payload,
                               text=True, capture_output=True, timeout=30)
            self.assertEqual(p.returncode == 0, success, p.stderr)
            if success:
                rows = loads_many(p.stdout)
                self.assertEqual(rows[0][0], 'frozen-model92')
                self.assertEqual(len(rows), 4)
                self.assertTrue(all(r[1] == 'complete' for r in rows[1:]))

    def test_invalid_context_and_command_arities(self):
        out = maru(SETUP + """
(define model (basis91 'model))
(list-do r (list (attention92 'start model 'missing '((r 0 1)) 'adaptive92 10)
 (attention92 'start model 'train '((r 0 9)) 'adaptive92 10)
 (attention92 'start model 'train '((r 0 1)) 'unknown 10)
 (attention92 'start model 'train '((r 0 1)) 'adaptive92 -1)
 (attention92 'start model 'train '((r 0 1)) 'adaptive92 200001)
 (attention92 'start) (attention92 'run 0) (attention92 'restore 42))
 (assert (= (car r) 'rejected92))) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_large_binding_workspace_keeps_all_roles_and_witnesses(self):
        facts = [[S('atom'), S('r'), [S('a'), S(f'b{i}')]] for i in range(7)]
        pattern = [[S('r'), 0, 1], [S('r'), 0, 2], [S('r'), 0, 3]]
        rows = loads_many(maru("""
(basis91 'init '(r)) (basis91 'observe 'g (read *standard-input*))
(list-do policy '(ordered92 indexed92 adaptive92 narrow92)
 (dump (attention92 'query (basis91 'model) 'g '((r 0 1) (r 0 2) (r 0 3)) policy 200000)) (print "\\n"))
""", dumps(facts)))
        expected = reference(pattern, facts)
        self.assertEqual(len(expected), 343)
        for row in rows:
            self.assertEqual(answers(row, facts), expected)

    def test_empirical_answer_coincidence_cannot_change_logical_roles(self):
        facts = [[S('atom'), S(p), [S(a), S(b)]] for p in ('r', 's') for a in ('a', 'b') for b in ('a', 'b')]
        out = maru("""
(basis91 'init '(r s)) (basis91 'observe 'g (read *standard-input*))
(attention92 'start (basis91 'model) 'g '((r 0 1) (s 1 2)) 'adaptive92 200000)
(define before *a92-state*)
(assert (= (car (attention92 'step '(focus92 g 1 0 (0 1 2 3 4 5 6 7) () (fact91 s (0 2))))) 'rejected92))
(assert (equal before *a92-state*)) (print "passed")""", dumps(facts))
        self.assertEqual(out, 'passed')

    def test_measurement_all_arms_independent_oracle(self):
        from attention92_experiment import run_experiment
        result = run_experiment(repeats=1, batches=1, seeds=(92,), cases=('selective-tail',))
        self.assertEqual(len(result['records']), 7)
        self.assertEqual(sum(r['oracle_queries'] for r in result['records']), 112)
        self.assertEqual(sum(r['mismatches'] for r in result['records']), 0)
        self.assertGreater(result['summaries']['selective-tail']['adaptive92']['peak_serialized_control_bytes'], 0)
        raw = next(r for r in result['records'] if r['arm'] == 'raw')['profiles'][1]['metrics']
        memo = next(r for r in result['records'] if r['arm'] == 'memo')['profiles'][1]['metrics']
        self.assertEqual(raw[2], 0)  # full-source relation tables shared, not forced cold
        self.assertEqual(memo[2], 0)
        self.assertGreater(memo[5], 0)  # cached r-s structural prefix from r-s-t
        self.assertLess(memo[1], raw[1])

    def test_exhaustive_two_node_graphs_roles_and_scopes(self):
        edges = [(p, a, b) for p in ('r', 's') for a in ('a', 'b') for b in ('a', 'b')]
        facts = [[S('atom'), S(p), [S(a), S(b)]] for p, a, b in edges]
        graphs = [[f for bit, f in enumerate(facts) if mask & (1 << bit)] for mask in range(256)]
        patterns = [[[S(p), a, b] for p, a, b in atoms] for atoms in [
            [('r', 0, 1), ('s', 1, 2)], [('r', 0, 1), ('s', 0, 2)],
            [('r', 0, 1), ('s', 2, 1)], [('r', 0, 1), ('s', 1, 0)],
            [('r', 0, 0), ('s', 0, 1)], [('r', 0, 1), ('s', 1, 2), ('r', 2, 3)],
            [('r', 0, 1), ('s', 0, 2), ('r', 2, 3)], [('r', 0, 0)]]]
        code = """
(basis91 'init '(r s))
(basis91 'observe 'train '((atom r (a b)) (atom s (b c)) (atom r (c d))
                         (atom r (p q)) (atom s (q z)) (atom r (z w))))
(basis91 'interpret 'train 200000) (basis91 'learn) (basis91 'learn)
(define base (basis91 'model)) (define request (read *standard-input*))
(list-do facts (car request)
 (define core (list 'execution-core91 '(r s) (list (list 'episode91 'oracle 1 facts false)) (dlm-nth base 3) () (dlm-nth base 5)))
 (list-do p (dlm-nth request 1)
  (list-do policy '(ordered92 indexed92 adaptive92 narrow92)
   (define r (attention92 'query core 'oracle p policy 200000))
   (dump (list (car r) (dlm-nth r 1) (dlm-nth r 2) (dlm-nth r 3))) (print "\n"))))
"""
        checks = 0
        for offset in range(0, 256, 32):
            chunk = graphs[offset:offset + 32]
            results = loads_many(maru(code, dumps([chunk, patterns])))
            self.assertEqual(len(results), len(chunk) * len(patterns) * 4)
            for i, graph in enumerate(chunk):
                for j, pattern in enumerate(patterns):
                    expected = reference(pattern, graph)
                    for r in results[(i * 8 + j) * 4:(i * 8 + j + 1) * 4]:
                        self.assertEqual(answers(r, graph), expected, (offset + i, pattern, r))
                        checks += 1
        self.assertEqual(checks, 8192)
        print('ATTENTION92-ORACLE 256 graphs x 8 patterns x 4 policies = 8192 complete answer/witness checks, zero mismatches')


if __name__ == '__main__':
    unittest.main()
