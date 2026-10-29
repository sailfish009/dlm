"""CPU/file-only basis discovery, replacement, execution and adversarial restore.
No HTTP server or external dataset. Python is an independent development oracle.
"""
import json
import random
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_sequent import maru
from sexp import Symbol as S, dumps, loads_many

ROOT = Path(__file__).resolve().parents[1]
SETUP = '(require "experiments/basis90/setup.l")\n'
ROUND2 = """
(basis90 'task 'rstu '(join90 (join90 (join90 (rel90 r) (rel90 s)) (rel90 t)) (rel90 u)))
(basis90 'task 'vrst '(join90 (rel90 v) (join90 (join90 (rel90 r) (rel90 s)) (rel90 t))))
"""
TRAINED = SETUP + "(basis90 'learn)\n" + ROUND2 + "(basis90 'learn)\n"


def answers(result):
    if result[0] != 'execution90' or result[1] != 'complete':
        raise AssertionError(result)
    return {str(row[1]): set(map(tuple, row[2])) for row in result[2]}


class Basis90Tests(unittest.TestCase):
    def test_discover_replace_and_second_round_uses_first_basis(self):
        out = maru(SETUP + """
(define before (b90-work-size (dlm-nth *b90-state* 5)))
(assert (= (car (basis90 'learn)) 'committed90) "first basis")
(assert (< (b90-work-size (dlm-nth *b90-state* 5)) before) "actual plan replacement")
(assert (equal (dlm-nth (car (dlm-nth *b90-state* 4)) 2) '(join90 (rel90 r) (rel90 s))) "not supplied by user")
""" + ROUND2 + """
(assert (= (car (basis90 'learn)) 'committed90) "second basis")
(assert (equal (dlm-nth (dlm-nth (dlm-nth *b90-state* 4) 1) 2) '(join90 (use90 1) (rel90 t))) "recursive dependency")
(assert (equal (dlm-nth (b90-find (dlm-nth *b90-state* 5) 'rst) 3) '(use90 2)) "public query mapped to basis")
(define event-log (dlm-nth *b90-state* 6))
(basis90 'learn) (basis90 'learn)
(assert (equal event-log (dlm-nth *b90-state* 6)) "saturation adds no synthetic feedback")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_active_executor_is_not_a_replay_or_raw_fallback(self):
        out = maru(TRAINED + """
(define-function disabled90 args (error "hot execution must not call this"))
(set b90-propose disabled90) (set b90-plan disabled90) (set b90-cover disabled90) (set b90-replay disabled90)
(define result (basis90 'run 'train () 200000))
(assert (= (dlm-nth result 1) 'complete) "active execution")
(assert (> (dlm-nth (dlm-nth result 3) 2) 0) "basis dispatches really execute")
(assert (dlm-member? 2 (dlm-nth (dlm-nth result 3) 6)) "recursive basis activated")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_four_controls_agree_but_account_for_different_work(self):
        results = loads_many(maru(TRAINED + """
(list-do arm '(raw append basis memo)
 (dump (list arm (basis90 'run 'train () 200000 arm))) (print "\\n"))"""))
        baseline = answers(results[0][1])
        for _, result in results:
            self.assertEqual(answers(result), baseline)
        self.assertEqual(results[0][1][3], results[1][1][3])
        self.assertLess(results[2][1][3][4], results[0][1][3][4])  # pair comparisons, not wall time
        self.assertEqual(baseline['rst'], {('a', 'd'), ('p', 'w')})

    def test_checker_does_not_call_proposer_planner_or_executor(self):
        out = maru(SETUP + """
(define proposal (basis90 'proposal))
(define-function disabled90 args (error "independent gate"))
(set b90-propose disabled90) (set b90-plan disabled90) (set b90-cover disabled90) (set b90-evaluate disabled90)
(assert (= (car (b90-check-learn *b90-state* (dlm-nth proposal 1) (dlm-nth proposal 2))) 'checked90) "independent gate")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_forged_definition_rewrite_certificate_and_cyclic_dependencies(self):
        out = maru(SETUP + """
(define p (basis90 'proposal))
(define m (dlm-nth p 1)) (define rows (dlm-nth p 2))
(assert (= (car (b90-check-learn *b90-state* (s79-field m 3 '(s r)) rows)) 'rejected90) "claimed word cannot lie")
(assert (= (car (b90-check-learn *b90-state* (s79-field m 2 '(join90 (use90 1) (rel90 r))) rows)) 'rejected90) "cycle")
(assert (= (car (b90-check-learn *b90-state* (s79-field m 2 '(join90 (use90 2) (rel90 r))) rows)) 'rejected90) "forward ref")
(define bad (s79-field (car rows) 3 '(join90 (rel90 s) (join90 (rel90 r) (rel90 t)))))
(assert (= (car (b90-check-learn *b90-state* m (cons bad (cdr rows)))) 'rejected90) "order matters")
(set bad (s79-field (car rows) 4 '(same-word90 (r s))))
(assert (= (car (b90-check-learn *b90-state* m (cons bad (cdr rows)))) 'rejected90) "certificate binds complete word")
(assert (= (car (b90-check-learn *b90-state* m (cdr rows))) 'rejected90) "coverage")
(define old *b90-state*)
(define-function forged90 (s) '(learn90 (basis90 1 (rel90 r) (r s)) ()))
(set b90-propose forged90)
(assert (= (car (basis90 'learn)) 'rejected90) "provisional success is not authority")
(assert (equal old *b90-state*) "no mutation")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_forged_initial_router_cannot_publish_false_task_plans(self):
        out = maru("""
(basis90 'init '(r s))
(define before *b90-state*)
(define-function wrong-route90 (e sig lib) '(rel90 s))
(set b90-plan wrong-route90)
(assert (= (car (basis90 'task 'q '(rel90 r))) 'rejected90) "router is not a semantic authority")
(assert (equal before *b90-state*) "no task or event publication")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_arbitrary_regrouping_is_checked_without_assuming_commutativity(self):
        out = maru("""
(assert (b90-equivalent? '(join90 (join90 (rel90 r) (rel90 s)) (rel90 t))
 '(join90 (rel90 r) (join90 (rel90 s) (rel90 t))) '(r s t) () '(same-word90 (r s t))) "associativity")
(assert (not (b90-equivalent? '(join90 (rel90 r) (rel90 s))
 '(join90 (rel90 s) (rel90 r)) '(r s) () '(same-word90 (r s)))) "not commutative")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_unknown_not_empty_and_heldout_query_does_not_train(self):
        out = maru(TRAINED + """
(define before *b90-state*)
(assert (= (dlm-nth (basis90 'run 'train () 0) 1) 'unknown) "zero budget is not negative answer")
(assert (= (dlm-nth (basis90 'query 'train '(join90 (rel90 r) (rel90 s)) 200000) 1) 'complete) "transient query")
(assert (equal before *b90-state*) "no eval feedback, cursor or library mutation")
(assert (= (car (basis90 'query 'train '(not90 (rel90 r)) 200)) 'rejected90) "unsupported grammar")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_cache_is_scoped_to_current_episode_and_retraction(self):
        out = maru(TRAINED + """
(basis90 'observe 'empty ())
(assert (not (dlm-nth (car (dlm-nth (basis90 'run 'empty '(rst) 200000) 2)) 2)) "no cross episode cache")
(basis90 'run 'train () 200000)
(basis90 'retract 'train)
(assert (= (car (basis90 'run 'train () 200000)) 'rejected90) "retracted source unavailable")
(basis90 'observe 'train ())
(assert (not (dlm-nth (car (dlm-nth (basis90 'run 'train '(rst) 200000) 2)) 2)) "no stale answer after replacement")
(assert (= (dlm-length (dlm-nth *b90-state* 4)) 2) "conservative definitions survive evidence retraction")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_no_repetition_is_waiting_and_limits_preserve_state(self):
        out = maru("""
(basis90 'init '(r s))
(basis90 'task 'one '(join90 (rel90 r) (rel90 s)))
(define before *b90-state*)
(assert (= (car (basis90 'learn)) 'waiting90) "no fake discovery")
(assert (= (car (basis90 'task 'one '(rel90 r))) 'rejected90) "immutable identity")
(assert (= (car (basis90 'task 'long '(join90 (join90 (rel90 r) (rel90 r)) (join90 (rel90 r) (join90 (rel90 r) (rel90 r)))))) 'rejected90) "word cap")
(assert (equal before *b90-state*) "rejections atomic")
(basis90 'init '(r))
(times-do 32 (basis90 'observe 'e ()) (basis90 'retract 'e))
(set before *b90-state*)
(assert (= (car (basis90 'learn)) 'rejected90) "event cap preflight")
(assert (equal before *b90-state*) "no cap mutation")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_malformed_input_and_snapshot_fail_closed(self):
        out = maru(SETUP + """
(list-do x (list 42 'bad (cons 'basis-session90 42) '(basis-session90 1 42 ())
 '(basis-session90 1 (basis-core90 (r) () ((basis90 1 (use90 1) (r r))) () 1) ()))
 (assert (not (b90-snapshot? x)) "bad snapshot"))
(list-do e (list 42 (cons 'join90 42) '(rel90 unknown) '(use90 1) '(join90 42 (rel90 r)))
 (assert (= (car (basis90 'task 'invalid e)) 'rejected90) "bad expression"))
(assert (= (car (basis90 'observe 'bad (list 42))) 'rejected90) "bad facts")
(assert (= (car (basis90 'observe 'bad '((atom r (a b c))))) 'rejected90) "arity")
(assert (= (car (basis90 'run 'train 42 100)) 'rejected90) "bad names")
(assert (= (car (basis90 'run 'train () 200001)) 'rejected90) "fuel")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_fresh_process_restores_pending_discovery_and_same_next_step(self):
        with tempfile.TemporaryDirectory() as directory:
            path = json.dumps(str(Path(directory) / 'basis.sexp'))
            first = maru(SETUP + f"(basis90 'open {path}) (basis90 'learn)\n" + ROUND2 + """
(basis90 'save)
(dump (basis90 'snapshot)) (print "\\n")
(dump (basis90 'proposal)) (print "\\n")
(dump (basis90 'run 'train () 200000)) (print "\\n")
(basis90 'learn)
(dump (basis90 'snapshot)) (print "\\n")
""")
            # Last complete generation before the second discovery.
            p = Path(json.loads(path))
            p.write_bytes(Path(str(p) + '.previous').read_bytes())
            second = maru(f"(basis90 'open {path})\n" + """
(dump (basis90 'snapshot)) (print "\\n")
(dump (basis90 'proposal)) (print "\\n")
(dump (basis90 'run 'train () 200000)) (print "\\n")
(basis90 'learn)
(dump (basis90 'snapshot)) (print "\\n")
(basis90 'close)
""")
            self.assertEqual(loads_many(first), loads_many(second))

    def test_checkpoint_failure_and_external_change_do_not_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            path = json.dumps(str(Path(directory) / 'basis.sexp'))
            out = maru(SETUP + f"(basis90 'open {path}) (basis90 'save)\n" + """
(define before (list *b90-state* *b90-expected*))
(define original b90-checkpoint)
(define-function refuse90 (path snapshot expected) false)
(set b90-checkpoint refuse90)
(assert (= (car (basis90 'learn)) 'rejected90) "failed checkpoint")
(assert (equal before (list *b90-state* *b90-expected*)) "no published basis, plan, epoch or audit")
(set b90-checkpoint original)
(assert (= (car (basis90 'learn)) 'committed90) "retry")
(d77-write *b90-path* '(corrupt90))
(set before *b90-state*)
(assert (= (car (basis90 'task 'extra '(rel90 r))) 'rejected90) "changed file")
(assert (equal before *b90-state*) "no mutation")
(print "passed")""")
            self.assertEqual(out, 'passed')
            self.assertIn('corrupt90', Path(json.loads(path)).read_text())

    def test_serialized_core_or_audit_cannot_forge_approval(self):
        out = maru(TRAINED + """
(define x (basis90 'snapshot))
(assert (b90-snapshot? x) "valid snapshot")
(define core (dlm-nth x 2))
(assert (not (b90-snapshot? (s79-field x 2 (s79-field core 3 ())))) "library erasure")
(assert (not (b90-snapshot? (s79-field x 2 (s79-field core 5 77)))) "epoch")
(assert (not (b90-snapshot? (s79-field x 3 (cdr (dlm-nth x 3))))) "source deletion")
(assert (not (b90-snapshot? (s79-field x 3 (dlm-append (dlm-nth x 3) '((learn90 (basis90 3 (use90 3) (r s)) ())))))) "forged event")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_existing_learners_are_not_mutated(self):
        out = maru("(define before (list *dlm-model* *dlm-events* *c87-library* *s79-space*))\n" + TRAINED + """
(basis90 'run 'train () 200000)
(assert (equal before (list *dlm-model* *dlm-events* *c87-library* *s79-space*)) "experimental ownership isolated")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_seeded_malformed_tree_fuzz_at_native_boundaries(self):
        rng = random.Random(90)
        atoms = [None, 42, -1, 1, 'untrusted (error)'] + list(map(S,
                 ('basis-session90', 'basis-core90', 'basis-state90', 'basis90', 'task90',
                  'observe90', 'learn90', 'rel90', 'join90', 'r', 'use90', 'document', 'url')))

        def tree(depth):
            if depth == 0 or rng.random() < .5:
                value = rng.choice(atoms)
                return [] if value is None else value
            return [tree(depth - 1) for _ in range(rng.randrange(9))]

        values = [tree(4) for _ in range(500)]
        out = maru("""
(define inputs (read *standard-input*))
(list-do x inputs
 (b90-word x '(r s) () 8) (b90-core? x) (b90-snapshot? x)
 (b90-signature? x) (b90-facts? x '(r s)) (web-document? x)
 (b90-apply (b90-new '(r s)) x) (b90-execute x 'none () 1 'basis)
 (b90-snapshot? (cons 'basis-session90 x)))
(print "passed")""", dumps(values))
        self.assertEqual(out, 'passed')

    def test_offline_input_driver_and_trailing_data_rejection(self):
        request = [S('basis-input90'), 1, [S('r'), S('s')],
                   [[S('e'), [[S('atom'), S('r'), [S('a'), S('b')]],
                              [S('atom'), S('s'), [S('b'), S('c')]]]]],
                   [[S('q1'), [S('join90'), [S('rel90'), S('r')], [S('rel90'), S('s')]]],
                    [S('q2'), [S('join90'), [S('rel90'), S('r')], [S('rel90'), S('s')]]]], 2, 2000]
        for suffix, success in [('', True), (' (extra90)', False)]:
            p = subprocess.run([str(ROOT / 'scripts/run.sh'), 'basis90-input'],
                               input=dumps(request) + suffix, text=True, capture_output=True, timeout=30)
            self.assertEqual(p.returncode == 0, success, p.stderr)
            if success:
                rows = loads_many(p.stdout)
                results = [r for r in rows if r[0] == 'basis-result90']
                self.assertEqual(len(results), 4)
                self.assertEqual(answers(results[2][3])['q1'], {('a', 'c')})
                self.assertEqual(rows[-1][0], 'basis-session90')

    def test_measurement_driver_uses_independent_oracle_and_all_controls(self):
        # Smoke the exact production experiment driver; no statistical timing claim.
        import sys
        sys.path.insert(0, str(ROOT / 'adapters'))
        from basis90_experiment import run_experiment
        result = run_experiment(repeats=1, query_batches=1)
        self.assertEqual(len(result['records']), 48)
        self.assertEqual(sum(row['mismatches'] for row in result['records']), 0)
        self.assertEqual(result['summaries']['no-repeat']['basis']['basis_body_nodes'], 0)
        self.assertGreater(result['summaries']['small-overhead']['basis']['execution_core_bytes'],
                           result['summaries']['small-overhead']['raw']['execution_core_bytes'])

    def test_exhaustive_two_relation_graph_oracle(self):
        # 2^(2 predicates * 2 nodes * 2 nodes) = all 256 source graphs.
        edges = [(p, a, b) for p in ('r', 's') for a in ('a', 'b') for b in ('a', 'b')]
        cases = [[S('atom'), S(p), [S(a), S(b)]] for p, a, b in edges]
        graphs = [[f for bit, f in enumerate(cases) if mask & (1 << bit)] for mask in range(256)]
        setup = """
(basis90 'init '(r s))
(basis90 'task 'rsr '(join90 (join90 (rel90 r) (rel90 s)) (rel90 r)))
(basis90 'task 'rsrs '(join90 (join90 (rel90 r) (rel90 s)) (join90 (rel90 r) (rel90 s))))
(basis90 'task 'srs '(join90 (rel90 s) (join90 (rel90 r) (rel90 s))))
(basis90 'learn)
(basis90 'task 'rsrr '(join90 (join90 (join90 (rel90 r) (rel90 s)) (rel90 r)) (rel90 r)))
(basis90 'task 'rrsr '(join90 (rel90 r) (join90 (join90 (rel90 r) (rel90 s)) (rel90 r))))
(basis90 'learn)
(assert (= (dlm-length (dlm-nth *b90-state* 4)) 2) "two oracle bases")
(list-do facts (read *standard-input*)
 (let ((view (s79-field *b90-state* 3 (list (list 'episode90 'oracle facts)))))
   (list-do arm '(raw basis memo)
     (dump (b90-execute view 'oracle () 200000 arm)) (print "\\n"))))
"""
        results = loads_many(maru(setup, dumps(graphs)))
        self.assertEqual(len(results), 256 * 3)
        words = dict(rsr='rsr', rsrs='rsrs', srs='srs', rsrr='rsrr', rrsr='rrsr')
        for index, graph in enumerate(graphs):
            relations = {p: {tuple(f[2]) for f in graph if f[1] == p} for p in ('r', 's')}
            expected = {}
            for name, word in words.items():
                value = relations[word[0]]
                for p in word[1:]:
                    value = {(a, d) for a, b in value for c, d in relations[p] if b == c}
                expected[name] = value
            for result in results[index * 3:index * 3 + 3]:
                self.assertEqual(answers(result), expected, (index, result))
        print('BASIS90-ORACLE 256 exhaustive graphs, 5 queries, 3 execution arms, zero mismatches')


if __name__ == '__main__':
    unittest.main()
