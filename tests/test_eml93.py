"""EML-foundational formation: native learner, independent CPU numeric oracle."""
import cmath
import copy
import json
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

from test_sequent import maru
from test_repl import Live
from sexp import Symbol as S, dumps, loads_many
from eml93_experiment import (ROOT, POINTS, REFERENCES, curriculum, evaluate,
                              fixture, native, rows, unz, z)

SETUP = '(require "experiments/eml93/setup.l")\n'
DEMO = SETUP + "(set *e93-state* (e93-demo-state 'lower93))\n"


class Eml93Tests(unittest.TestCase):
    def test_formation_from_observations_and_hierarchical_active_replacement(self):
        data, _ = fixture(count=1)
        output, _ = native(data)
        transitions = [r for r in output if r[0] == 'transition93']
        self.assertEqual([len(r[4][3]) for r in transitions], [0, 1, 1, 2, 2, 3, 3, 4])
        core = transitions[-1][4]
        self.assertIn(S('call93'), str(core[3][1][3]))
        self.assertEqual(core[3][2][3], [S('eml93'), [S('call93'), 2, [[S('x93'), 0]]],
                                               [S('call93'), 1, [[S('x93'), 1]]]])
        self.assertEqual(core[3][3][3], [S('call93'), 1, [[S('call93'), 3, [[S('x93'), 0], [S('x93'), 1]]]]])
        self.assertEqual(len(core[4]), 7)
        self.assertTrue(all(v[5][0] == 'call93' for v in core[4]))

    def test_independent_heldout_numeric_oracle_both_branches(self):
        for branch in ('principal93', 'lower93'):
            result = evaluate(2, branch, False)
            self.assertEqual(result['complete'], 64)
            self.assertEqual(result['mismatches'], 0)
            self.assertEqual(result['unknown'], 0)

    def test_branch_experience_persistently_changes_applicability(self):
        for branch, negative_answers in [('principal93', 0), ('lower93', 8)]:
            result = evaluate(1, branch, True)
            self.assertEqual(result['mismatches'], 0)
            self.assertEqual(result['by_source']['u2']['complete'], 8 + negative_answers)
            self.assertEqual(result['by_source']['u2']['unknown'], 8 - negative_answers)
            views = [v for v in result['core'][4] if v[1] == 'u2']
            self.assertTrue(all(v[2] == 2 for v in views))
            self.assertEqual(len(views), 1 + bool(negative_answers))

    def test_prefix_reuse_changes_reachable_formation_not_merely_query_order(self):
        out = maru(DEMO + f"""
(define observed '{dumps(rows('u3'))})
(define raw (e93-search 2 observed () 'lower93 3 200000))
(define prefix (list (car (e93-lib *e93-state*)) (dlm-nth (e93-lib *e93-state*) 1)))
(define learned (e93-search 2 observed prefix 'lower93 3 200000))
(assert (= (dlm-nth raw 1) 'no-fit))
(assert (= (dlm-nth learned 1) 'found))
(assert (= (e93-size (car (dlm-nth learned 2))) 3))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_standalone_core_inference_without_source_archive_or_learner(self):
        out = maru(DEMO + """
(define frozen (eml93 'model)) (eml93 'reset) (set fixture93 ())
(define-function no93 args (error "archive/search must not be needed"))
(set e93-replay no93) (set e93-propose no93) (set e93-search no93) (set e93-fit no93)
(set e93-build-views no93)
(define a (eml93 'infer frozen 'u4 '((z93 1200000 0) (z93 300000 0)) 200000))
(assert (= (dlm-nth a 1) 'complete))
(assert (equal (dlm-nth (dlm-nth a 5) 4) '(1 1 1 2 3 4)) "real hierarchical execution")
(assert (= (dlm-nth a 3) 'empirical93)) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_scope_missing_zero_and_budget_return_unknown_never_false(self):
        out = maru(DEMO + """
(list-do args '(((z93 0 0)) ((z93 -1000000 0)) ((z93 1000000 1000)))
 (assert (= (dlm-nth (eml93 'query 'u2 args 200000) 1) 'unknown)))
(assert (= (dlm-nth (eml93 'query 'u4 '((z93 1000000 0) (z93 500000 0)) 0) 1) 'unknown))
(assert (= (car (e93-eml '(z93 0 0) '(z93 0 0) 'lower93)) 'undefined93))
(assert (= (car (e93-eml '(z93 7000000 0) '(z93 1000000 0) 'lower93)) 'undefined93))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_numeric_backend_against_independent_cmath(self):
        rng = random.Random(9301)
        cases = []
        for branch in ('principal93', 'lower93'):
            for i in range(100):
                a = z(complex(rng.uniform(-2, 3), rng.uniform(-3.1, 3.1)))
                b = z(complex(rng.uniform(-4, 4), 0 if i % 3 == 0 else rng.uniform(-3, 3)))
                cases.append((branch, a, b))
        code = ''.join(f"(dump (e93-eml '{dumps(a)} '{dumps(b)} '{branch})) (print \"\\n\")\n"
                       for branch, a, b in cases)
        values = loads_many(maru(code))
        self.assertEqual(len(values), 200)
        for (branch, a, b), value in zip(cases, values):
            aa, bb = unz(a), unz(b)
            logb = cmath.log(bb)
            if branch == 'lower93' and bb.imag == 0 and bb.real < 0:
                logb -= 2j * cmath.pi
            self.assertLess(abs(unz(value) - (cmath.exp(aa) - logb)), .002)

    def test_tiny_complex_log_norm_does_not_round_away_before_log(self):
        cases = [(a, b) for a in (z(0), z(1)) for b in
                 (z(complex(.000001, .000001)), z(complex(-.000001, .000002)),
                  z(complex(999, 999)))]
        code = '\n'.join(f"(dump (e93-eml '{dumps(a)} '{dumps(b)} 'principal93))"
                         for a, b in cases)
        values = loads_many(maru(code))
        for (a, b), value in zip(cases, values):
            self.assertLess(abs(unz(value) - (cmath.exp(unz(a)) - cmath.log(unz(b)))), .002)
        self.assertEqual(len(values), len(cases))

    def test_negative_axis_log_identity_branch_difference_is_retained(self):
        output = loads_many(maru("""
(list-do branch '(principal93 lower93)
 (dump (e93-raw '(eml93 one93 (eml93 (eml93 one93 (x93 0)) one93))
   '((z93 -1000000 0)) branch)) (print "\n"))
"""))
        self.assertLess(abs(unz(output[0]) + 1j * cmath.pi), .0001)
        self.assertLess(abs(unz(output[1]) - 1j * cmath.pi), .0001)

    def test_observations_do_not_contain_programs_or_target_function_names(self):
        data, _ = fixture(count=1)
        for command in data[3]:
            if command[0] == 'observe93':
                self.assertTrue(all(r[0] == 'row93' and r[3][0] == 'z93' for r in command[3]))
        text = dumps(data)
        for forbidden in ('call93', '(eml93 ', 'basis93', 'exp', 'log', 'subtract'):
            self.assertNotIn(forbidden, text)

    def test_duplicate_inputs_and_bad_shapes_cannot_inflate_support(self):
        good = rows('u1')[:3]
        bad = copy.deepcopy(good)
        bad[1][2] = copy.deepcopy(bad[0][2])
        out = maru(f"""
(eml93 'init 'lower93) (define before (eml93 'snapshot))
(assert (= (car (eml93 'observe 'bad 1 '{dumps(bad)})) 'rejected93))
(assert (= (car (eml93 'observe 'bad 3 '{dumps(good)})) 'rejected93))
(assert (equal before (eml93 'snapshot))) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_insufficient_data_can_be_completed_by_human_without_providing_basis(self):
        good = rows('u2')[:3]
        out = maru(f"""
(eml93 'init 'lower93)
(eml93 'observe 'human 1 '{dumps(good[:2])})
(assert (= (dlm-nth (eml93 'learn 'human 3 200000) 1) 'distinct-observations))
(assert (not (e93-lib *e93-state*)))
(eml93 'observe 'human 1 '{dumps(good)})
(assert (= (car (eml93 'learn 'human 3 200000)) 'eml93))
(assert (= (dlm-length (e93-lib *e93-state*)) 1))
(assert (= (dlm-nth (eml93 'query 'human '((z93 1700000 0)) 200000) 1) 'complete))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_thin_first_cell_does_not_block_supported_cell(self):
        good = rows('u1', [(-.1,), (.2,), (.7,), (1.2,)])
        out = maru(f"""
(eml93 'init 'lower93) (eml93 'observe 'mixed 1 '{dumps(good)})
(assert (= (car (eml93 'learn 'mixed 3 200000)) 'eml93))
(assert (= (dlm-nth (eml93 'query 'mixed '((z93 -400000 0)) 200000) 1) 'unknown))
(assert (= (dlm-nth (eml93 'query 'mixed '((z93 400000 0)) 200000) 1) 'complete))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_counterexample_removes_active_scope_not_definitions_or_other_sources(self):
        bad = rows('u2')
        bad[0][3] = z(99)
        good = rows('u2')
        out = maru(DEMO + f"""
(define old (eml93 'model)) (define lib (e93-lib *e93-state*))
(eml93 'observe 'u2 1 '{dumps(bad)})
(assert (equal lib (e93-lib *e93-state*)))
(assert (= (dlm-nth (eml93 'query 'u2 '((z93 1700000 0)) 200000) 1) 'unknown))
(assert (= (dlm-nth (eml93 'query 'u1 '((z93 1700000 0)) 200000) 1) 'complete))
(eml93 'observe 'u2 1 '{dumps(good)})
(assert (= (dlm-nth (eml93 'query 'u2 '((z93 1700000 0)) 200000) 1) 'complete))
(assert (= (dlm-nth (eml93 'infer old 'u2 '((z93 1700000 0)) 200000) 1) 'complete))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_search_budget_does_not_publish_partial_learning(self):
        observed = rows('u2')
        out = maru(f"""
(eml93 'init 'lower93) (eml93 'observe 'x 1 '{dumps(observed)})
(define before (eml93 'snapshot))
(assert (= (dlm-nth (eml93 'learn 'x 3 0) 1) 'unknown))
(assert (equal before (eml93 'snapshot))) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_poisoned_worker_and_omitted_proposal_values_are_rejected(self):
        observed = rows('u1')[:4]
        out = maru(f"""
(eml93 'init 'lower93) (eml93 'observe 'p 1 '{dumps(observed)})
(define p (eml93 'proposal 'p 3 200000))
(assert (e93-check-learn *e93-state* p))
(assert (not (e93-check-learn *e93-state* (s79-field p 4 ()))))
(assert (not (e93-check-learn *e93-state* (s79-field p 5 ()))))
(define-function liar93 (t rows lib branch tolerance r)
 (list 'fit93 'matched '((z93 0 0)) r))
(set e93-fit liar93) (define before (eml93 'snapshot))
(assert (= (car (eml93 'learn 'p 3 200000)) 'rejected93))
(assert (equal before (eml93 'snapshot))) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_wrong_inference_worker_is_not_repaired_by_checker(self):
        out = maru(DEMO + """
(define-function liar93 (t xs lib branch r) (e93-value 'complete '(z93 0 0) r))
(set e93-eval liar93)
(assert (= (car (eml93 'query 'u1 '((z93 800000 0)) 200000)) 'rejected93))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_invalid_roles_forward_calls_and_forged_expansions(self):
        out = maru(DEMO + """
(define core (eml93 'model)) (define lib (dlm-nth core 3)) (define b (car lib))
(list-do bad (list (s79-field b 3 '(x93 2)) (s79-field b 3 '(call93 1 ((x93 0))))
 (s79-field b 4 '(x93 0)) (s79-field b 1 2))
 (assert (not (e93-library? (cons bad (cdr lib))))))
(assert (not (e93-core? (s79-field core 2 'unknown-branch))))
(assert (not (e93-core? (s79-field core 5 -1))))
(assert (not (e93-node (dlm-nth (dlm-nth lib 3) 4) ())))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_retraction_and_query_do_not_learn_or_change_legacy_models(self):
        out = maru(DEMO + """
(define legacy (list *b91-state* *b90-state* *dlm-model* *a92-state*))
(define before (eml93 'snapshot))
(eml93 'query 'u1 '((z93 1000000 0)) 200000)
(eml93 'proposal 'u1 3 200000)
(assert (equal before (eml93 'snapshot)))
(eml93 'retract 'u1)
(assert (= (dlm-nth (eml93 'query 'u1 '((z93 1000000 0)) 200000) 1) 'unknown))
(assert (equal legacy (list *b91-state* *b90-state* *dlm-model* *a92-state*)))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_replay_restore_and_forged_snapshot_rejection(self):
        out = maru(DEMO + """
(define snapshot (eml93 'snapshot)) (define before (eml93 'model))
(assert (e93-snapshot? snapshot))
(assert (not (e93-snapshot? (s79-field snapshot 2 'principal93))))
(assert (not (e93-snapshot? (s79-field snapshot 4 ()))))
(define core (dlm-nth snapshot 3))
(assert (not (e93-snapshot? (s79-field snapshot 3 (s79-field core 5 0)))))
(eml93 'reset) (eml93 'restore snapshot)
(assert (equal before (eml93 'model))) (print "passed")""")
        self.assertEqual(out, 'passed')

    def test_checkpoint_fresh_process_continuation_and_lock(self):
        with tempfile.TemporaryDirectory() as td:
            path = str(Path(td) / 'eml.sexp')
            literal = json.dumps(path)
            self.assertEqual(maru(DEMO + f"(eml93 'open {literal}) (eml93 'save) (eml93 'close) (print \"saved\")"), 'saved')
            result = maru(f"""
(eml93 'open {literal})
(assert (= (dlm-nth (eml93 'query 'u4 '((z93 1200000 0) (z93 300000 0)) 200000) 1) 'complete))
(eml93 'retract 'u1) (eml93 'close) (print "restored")""")
            self.assertEqual(result, 'restored')
            live = Live()
            try:
                live.exchange(f"(eml93 'open {literal})", rb'eml93 branch')
                self.assertEqual(maru(f"(dump (eml93 'open {literal}))"), '(rejected93 locked-or-path)')
                live.exchange("(eml93 'close)", rb'closed93')
            finally:
                live.close()

    def test_checkpoint_failure_does_not_publish_and_failed_close_retains_attachment(self):
        with tempfile.TemporaryDirectory() as td:
            literal = json.dumps(str(Path(td) / 'state'))
            out = maru(DEMO + f"""
(eml93 'open {literal}) (eml93 'save) (define before *e93-state*)
(define-function fail93 (path snapshot expected) false) (set e93-checkpoint fail93)
(assert (= (car (eml93 'retract 'u1)) 'rejected93))
(assert (equal before *e93-state*))
(assert (= (car (eml93 'close)) 'rejected93)) (assert *e93-path*)
(assert (= (car (eml93 'init 'principal93)) 'rejected93)) (print "passed")""")
            self.assertEqual(out, 'passed')

    def test_fuzz_external_shapes_do_not_crash(self):
        rng = random.Random(9393)
        atoms = [0, -1, 999, [], S('eml93'), S('x93'), 'foreign']
        def tree(depth):
            if depth == 0 or rng.random() < .4:
                return rng.choice(atoms)
            return [tree(depth - 1) for _ in range(rng.randrange(5))]
        data = [tree(3) for _ in range(400)]
        out = maru("""
(eml93 'init 'lower93)
(list-do x (read *standard-input*)
 (e93-core? x) (e93-snapshot? x) (e93-library? x) (e93-rows? x 1)
 (eml93 'observe 'fuzz 1 x))
(print "passed")""", dumps(data))
        self.assertEqual(out, 'passed')

    def test_source_renaming_does_not_supply_function_semantics(self):
        data, expected = fixture(count=3)
        names = {S(f'u{i}'): S(f'opaque-{17 * i}') for i in range(1, 5)}
        for command in data[3]:
            command[1] = names[command[1]]
        for query in data[4]:
            query[1] = names[query[1]]
        output, _ = native(data)
        answers = [v for v in output if v[0] == 'answer93']
        self.assertEqual(len(answers), len(expected))
        for answer, target in zip(answers, expected):
            self.assertEqual(answer[1], 'complete')
            self.assertLess(abs(unz(answer[2]) - target), .002)

    def test_finite_fit_is_empirical_and_new_counterexample_withdraws_scope(self):
        observed = rows('u1', [(.2,), (.7,), (1.1,)])
        # An alternative law exp(x)+(x-.2)(x-.7)(x-1.1) agrees at all training
        # points, but differs elsewhere. Native receives ONLY those observations.
        contradicted = observed + [[S('row93'), S('counterexample'), [z(2)],
                                   z(cmath.exp(2) + 1.8 * 1.3 * .9)]]
        out = maru(f"""
(eml93 'init 'lower93) (eml93 'observe 'ambiguous 1 '{dumps(observed)})
(eml93 'learn 'ambiguous 3 200000)
(define a (eml93 'query 'ambiguous '((z93 2000000 0)) 200000))
(assert (= (dlm-nth a 1) 'complete)) (assert (= (dlm-nth a 3) 'empirical93))
(eml93 'observe 'ambiguous 1 '{dumps(contradicted)})
(assert (= (dlm-nth (eml93 'query 'ambiguous '((z93 2000000 0)) 200000) 1) 'unknown))
(assert (e93-lib *e93-state*) "definition remains, asserted applicability removed")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_mixed_source_versions_and_unused_view_roles_rejected(self):
        out = maru(DEMO + """
(define core (eml93 'model)) (define views (dlm-nth core 4))
(assert (not (e93-core? (s79-field core 4 (cons (s79-field (car views) 2 2) (cdr views))))))
(assert (not (e93-core? (s79-field core 4 (cons (s79-field (car views) 5 'one93) (cdr views))))))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_data_input_is_not_evaluated_and_trailing_data_rejected(self):
        data, _ = fixture(count=1)
        for text in (dumps(data) + ' ()', '(print "EXECUTED")'):
            child = subprocess.run([str(ROOT / 'scripts/run.sh'), 'eml93-input'], input=text,
                                   text=True, capture_output=True, timeout=30)
            self.assertNotEqual(child.returncode, 0)
            self.assertNotIn('EXECUTED\n', child.stdout)


if __name__ == '__main__':
    unittest.main()
