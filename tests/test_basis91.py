"""Data-led logical interpretation, checked basis formation and actual reuse.
Python is an independent development oracle, never a native policy/learner.
"""
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

ROOT = Path(__file__).resolve().parents[1]
SETUP = '(require "experiments/basis91/setup.l")\n'
TRAINED = SETUP + "(basis91 'learn) (basis91 'learn)\n"
CHAIN = "'((r 0 1) (s 1 2) (t 2 3))"


def reference(pattern, facts):
    """Truth under all finite role assignments, independent of join/planning code."""
    nodes = sorted({v for f in facts for v in f[2]}, key=str)
    arity = 1 + max(v for atom in pattern for v in atom[1:])
    available = {(f[1], *f[2]) for f in facts}
    return {values for values in itertools.product(nodes, repeat=arity)
            if all((p, values[x], values[y]) in available for p, x, y in pattern)}


def bindings(result, facts=None):
    if result[0] != 'execution91' or result[1] != 'complete':
        raise AssertionError(result)
    p, rows = result[2:4]
    if facts is not None:
        for _, values, ids in rows:
            if len(ids) != len(p):
                raise AssertionError(rows)
            for (pred, x, y), i in zip(p, ids):
                if facts[i] != [S('atom'), pred, [values[x], values[y]]]:
                    raise AssertionError((p, values, ids, facts))
    return {tuple(row[1]) for row in rows}


class Basis91Tests(unittest.TestCase):
    def test_data_only_interpretation_then_recursive_basis_and_replacement(self):
        out = maru(SETUP + """
(assert (= (dlm-length (dlm-nth *b91-state* 5)) 3) "data produced readings without task programs")
(assert (= (b91-work-size (dlm-nth *b91-state* 5)) 7) "primitive views")
(assert (= (car (basis91 'learn)) 'committed91) "first basis")
(assert (= (car (basis91 'learn)) 'committed91) "second basis")
(assert (equal (dlm-nth (dlm-nth (dlm-nth *b91-state* 4) 1) 3)
 '((call91 1 (0 1 2)) (fact91 t (2 3)))) "second basis contains first")
(assert (= (b91-work-size (dlm-nth *b91-state* 5)) 4) "active replacement")
(basis91 'learn) ; the independent s-t reading still admits a third valid basis
(define before *b91-state*) (basis91 'learn) (basis91 'learn)
(assert (equal before *b91-state*) "no fabricated progress after remaining candidate is learned")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_chain_fork_and_shared_target_are_distinct_readings(self):
        out = maru("""
(basis91 'init '(r s))
(basis91 'observe 'g '((atom r (a b)) (atom s (b c)) (atom s (a d)) (atom s (e b))))
(basis91 'interpret 'g 200000)
(dump (basis91 'query 'g '((r 0 1) (s 1 2)) 200000)) (print "\\n")
(dump (basis91 'query 'g '((r 0 1) (s 0 2)) 200000)) (print "\\n")
(dump (basis91 'query 'g '((r 0 1) (s 2 1)) 200000)) (print "\\n")
""")
        rows = loads_many(out)
        self.assertEqual(bindings(rows[0]), {('a', 'b', 'c')})
        self.assertEqual(bindings(rows[1]), {('a', 'b', 'd')})
        self.assertEqual(bindings(rows[2]), {('a', 'b', 'e')})

    def test_fork_and_target_can_form_checked_bases_not_just_path_words(self):
        for facts, expected in [
            ("'((atom r (a b)) (atom s (a c)) (atom r (p q)) (atom s (p z)))", "'((r 0 1) (s 0 2))"),
            ("'((atom r (a c)) (atom s (b c)) (atom r (p z)) (atom s (q z)))", "'((r 0 1) (s 2 1))")]:
            with self.subTest(expected=expected):
                out = maru(f"""
(basis91 'init '(r s)) (basis91 'observe 'g {facts}) (basis91 'interpret 'g 200000)
(assert (= (car (basis91 'learn)) 'committed91) "non-path basis")
(assert (equal (dlm-nth (car (dlm-nth *b91-state* 4)) 2) {expected}) "role structure")
(assert (b91-snapshot? (basis91 'snapshot)) "restore non-path basis")
(print "passed")""")
                self.assertEqual(out, 'passed')

    def test_one_source_application_and_automorphism_do_not_inflate_support(self):
        out = maru("""
(basis91 'init '(r))
(basis91 'observe 'g '((atom r (a b)) (atom r (b a))))
(basis91 'interpret 'g 200000)
(assert (= (car (basis91 'learn)) 'waiting91) "two orientations of same fact pair are one application")
(define before *b91-state*)
(assert (= (car (basis91 'interpret 'g 200000)) 'rejected91) "repeat reading")
(assert (= (car (basis91 'observe 'g '((atom r (a b))))) 'rejected91) "repeat source")
(assert (equal before *b91-state*) "no duplicate feedback")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_renaming_and_atom_order_preserve_structure_and_bindings(self):
        out = maru(TRAINED + """
(assert (equal (b91-data-patterns '((atom r (aa bb)) (atom s (bb cc))) '(r s))
 (b91-data-patterns '((atom s (zz xx)) (atom r (yy zz))) '(r s))) "canonical roles ignore names/order")
(dump (basis91 'query 'train '((t 2 3) (s 1 2) (r 0 1)) 200000))
""")
        self.assertEqual(bindings(loads_many(out)[0]), {('a', 'b', 'c', 'd'), ('p', 'q', 'z', 'w')})

    def test_new_data_not_training_answer_lookup_and_no_heldout_feedback(self):
        out = maru(TRAINED + """
(define before *b91-state*)
(define-function disabled91 args (error "must not discover or replay on query"))
(set b91-data-patterns disabled91) (set b91-propose disabled91) (set b91-replay disabled91)
(define result (basis91 'probe '((atom r (aa bb)) (atom s (bb cc)) (atom t (cc dd)))
 '((r 0 1) (s 1 2) (t 2 3)) 200000))
(assert (equal (dlm-nth (car (dlm-nth result 3)) 1) '(aa bb cc dd)) "fresh binding")
(assert (dlm-member? 2 (dlm-nth (dlm-nth result 4) 6)) "basis2 used")
(assert (dlm-member? 1 (dlm-nth (dlm-nth result 4) 6)) "basis1 used")
(assert (equal before *b91-state*) "heldout cannot train")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_stored_active_plans_execute_without_rerouting_or_raw_fallback(self):
        out = maru(TRAINED + """
(define-function disabled91 args (error "stored execution should not call this"))
(set b91-plan disabled91) (set b91-primitive disabled91) (set b91-propose disabled91) (set b91-replay disabled91)
(define result (basis91 'run 'train 200000))
(assert (= (dlm-nth result 1) 'complete) "active plans")
(assert (> (dlm-nth (dlm-nth result 3) 4) 0) "actual dispatch")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_all_four_controls_agree_including_intermediate_witnesses(self):
        rows = loads_many(maru(TRAINED + """
(list-do arm '(raw memo append basis)
 (dump (list arm (basis91 'run 'train 200000 arm))) (print "\\n"))
"""))
        def values(batch):
            return {dumps(row[1]): {tuple(match[1]) for match in row[2]} for row in batch[2]}
        for _, row in rows:
            self.assertEqual(row[1], 'complete')
            self.assertEqual(values(row), values(rows[0][1]))
        self.assertLess(rows[3][1][3][3], rows[0][1][3][3])  # join attempts
        self.assertEqual(rows[0][1][3], rows[2][1][3])
        self.assertGreater(rows[3][1][3][4], 0)

    def test_checker_independent_of_matcher_discovery_and_planner(self):
        out = maru(SETUP + """
(define p (basis91 'proposal))
(define-function disabled91 args (error "independent gate must not call this"))
(set b91-plan disabled91) (set b91-cover disabled91) (set b91-eval-plan disabled91)
(set b91-data-patterns disabled91) (set b91-propose disabled91) (set b91-interpret disabled91)
(assert (= (car (b91-check-learn *b91-state* (dlm-nth p 1) (dlm-nth p 2))) 'checked91) "independent")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_forged_roles_definition_projection_and_rewrite_rejected(self):
        out = maru(SETUP + """
(define p (basis91 'proposal)) (define m (dlm-nth p 1)) (define rs (dlm-nth p 2))
(assert (= (car (b91-check-learn *b91-state* (s79-field m 3 '((fact91 r (0 1)) (fact91 s (0 2)))) rs)) 'rejected91) "fork is not chain")
(assert (= (car (b91-check-learn *b91-state* (s79-field m 3 '((call91 1 (0 1 2)) (fact91 r (0 1)))) rs)) 'rejected91) "cycle")
(assert (= (car (b91-check-learn *b91-state* (s79-field m 3 '((call91 2 (0 1 2)) (fact91 r (0 1)))) rs)) 'rejected91) "forward ref")
(define bad (s79-field (car rs) 5 '((call91 1 (0 2)))))
(assert (= (car (b91-check-learn *b91-state* m (cons bad (cdr rs)))) 'rejected91) "dropping intermediate role")
(assert (= (car (b91-check-learn *b91-state* m (cdr rs))) 'rejected91) "missing reading")
(define before *b91-state*)
(define-function forged91 (s) '(learn91 (basis91 1 ((r 0 1) (s 1 2)) ((fact91 s (0 1)))) ()))
(set b91-propose forged91)
(assert (= (car (basis91 'learn)) 'rejected91) "selection not authority")
(assert (equal before *b91-state*) "atomic rejection")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_witness_forgery_and_source_version_mismatch(self):
        out = maru(SETUP + """
(define v (car (dlm-nth *b91-state* 5)))
(define ep (car (dlm-nth *b91-state* 3)))
(assert (not (b91-witness? (dlm-nth v 3) '(match91 (a b c) (0 2)) ep)) "wrong supporting fact")
(assert (not (b91-witness? (dlm-nth v 3) '(match91 (a c b) (0 1)) ep)) "wrong role binding")
(assert (not (b91-witness? (dlm-nth v 3) '(match91 (a b c) (0 99)) ep)) "invalid reference")
(assert (not (b91-state? (s79-field *b91-state* 5 (cons (s79-field v 2 22) (cdr (dlm-nth *b91-state* 5)))))) "stale version")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_initial_router_and_false_matcher_cannot_publish_interpretation(self):
        out = maru("""
(basis91 'init '(r s))
(basis91 'observe 'g '((atom r (a b)) (atom s (b c))))
(define before *b91-state*)
(define original b91-plan)
(define-function wrong91 (p sig lib) '((fact91 r (0 1)) (fact91 s (0 2))))
(set b91-plan wrong91)
(assert (= (car (basis91 'interpret 'g 200000)) 'rejected91) "false route")
(assert (equal before *b91-state*) "route rejection atomic")
(set b91-plan original)
(define-function liar91 (plan facts lib r memo) (b91-value 'complete '(((0 a) (1 c) (2 b))) r))
(set b91-eval-plan liar91)
(assert (= (car (basis91 'interpret 'g 200000)) 'rejected91) "false result fails independent witness check")
(assert (equal before *b91-state*) "matcher rejection atomic")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_unknown_partial_and_no_unlicensed_transitivity(self):
        out = maru(TRAINED + """
(assert (= (dlm-nth (basis91 'query 'train '((r 0 1) (s 1 2)) 0) 1) 'unknown) "not empty")
(assert (not (dlm-nth (basis91 'probe '((atom r (a b))) '((r 0 1) (s 1 2)) 1000) 3)) "partial pattern not a proof")
(define result (basis91 'probe '((atom r (a b)) (atom r (b c))) '((r 0 1)) 1000))
(assert (= (dlm-length (dlm-nth result 3)) 2) "no invented r(a,c)")
(basis91 'observe 'budget '((atom r (aa bb)) (atom s (bb cc))))
(define before *b91-state*)
(assert (= (car (basis91 'interpret 'budget 0)) 'rejected91) "unfinished batch not committed")
(assert (equal before *b91-state*) "no partial training update")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_retraction_removes_readings_not_conservative_definitions_or_stale_cache(self):
        out = maru(TRAINED + """
(basis91 'run 'train 200000)
(basis91 'retract 'train)
(assert (not (dlm-nth *b91-state* 5)) "training support removed")
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 2) "definitions remain definitions")
(assert (= (car (basis91 'query 'train '((r 0 1)) 1000)) 'rejected91) "old source unavailable")
(basis91 'observe 'train '((atom r (a b))))
(assert (not (dlm-nth (basis91 'query 'train '((r 0 1) (s 1 2)) 1000) 3)) "no stale binding")
(assert (> (dlm-nth (car (dlm-nth *b91-state* 3)) 2) 1) "new version")
(assert (= (car (basis91 'learn)) 'waiting91) "removed support not recycled")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_model_excludes_training_answers_and_saved_evidence_is_checked(self):
        out = maru(TRAINED + """
(assert (= (car (basis91 'model)) 'execution-core91) "executable projection")
(list-do v (dlm-nth (basis91 'model) 4) (assert (= (dlm-length v) 5) "no answer table in model"))
(define snapshot (basis91 'snapshot))
(assert (b91-snapshot? snapshot) "valid")
(assert (not (b91-snapshot? (s79-field snapshot 3 ()))))
(assert (not (b91-snapshot? (s79-field snapshot 4 (cdr (dlm-nth snapshot 4))))))
(assert (not (b91-snapshot? (s79-field snapshot 2 (s79-field (dlm-nth snapshot 2) 3 ())))))
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_executable_model_runs_without_training_answers_or_audit(self):
        out = maru(TRAINED + """
(define model (basis91 'model))
(basis91 'init '(edge))
(define-function disabled91 args (error "execution must not read the training archive"))
(set b91-replay disabled91) (set b91-state? disabled91) (set b91-evidence disabled91) (set b91-rows? disabled91)
(define result (basis91 'infer model 'train '((r 0 1) (s 1 2) (t 2 3)) 200000))
(assert (= (dlm-nth result 1) 'complete) "standalone core")
(assert (= (dlm-length (dlm-nth result 3)) 2) "fresh execution, no saved answer table")
(assert (dlm-member? 2 (dlm-nth (dlm-nth result 4) 6)) "real basis dispatch")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_fresh_process_same_pending_proposal_and_next_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'basis.sexp'
            q = json.dumps(str(path))
            first = maru(SETUP + f"(basis91 'learn) (basis91 'open {q}) (basis91 'save)\n" + """
(dump (basis91 'snapshot)) (print "\\n")
(dump (basis91 'proposal)) (print "\\n")
(dump (basis91 'run 'train 200000)) (print "\\n")
(basis91 'learn)
(dump (basis91 'snapshot)) (print "\\n")
""")
            path.write_bytes(Path(str(path) + '.previous').read_bytes())
            second = maru(f"(basis91 'open {q})\n" + """
(dump (basis91 'snapshot)) (print "\\n")
(dump (basis91 'proposal)) (print "\\n")
(dump (basis91 'run 'train 200000)) (print "\\n")
(basis91 'learn)
(dump (basis91 'snapshot)) (print "\\n")
(basis91 'close)
""")
            self.assertEqual(loads_many(first), loads_many(second))

    def test_checkpoint_failure_external_change_and_corrupt_load_do_not_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'basis.sexp'
            q = json.dumps(str(path))
            out = maru(SETUP + f"(basis91 'open {q}) (basis91 'save)\n" + """
(define before (list *b91-state* *b91-expected*))
(define original b91-checkpoint)
(define-function refuse91 (path snapshot expected) false)
(set b91-checkpoint refuse91)
(assert (= (car (basis91 'learn)) 'rejected91) "checkpoint refusal")
(assert (equal before (list *b91-state* *b91-expected*)) "no staged publication")
(set b91-checkpoint original)
(assert (= (car (basis91 'learn)) 'committed91) "retry")
(d77-write *b91-path* '(corrupt91))
(set before *b91-state*)
(assert (= (car (basis91 'observe 'extra ())) 'rejected91) "external change")
(assert (equal before *b91-state*) "no mutation")
(print "passed")""")
            self.assertEqual(out, 'passed')
            before = path.read_bytes()
            out = maru(f"(assert (= (car (basis91 'open {q})) 'rejected91)) (print \"passed\")")
            self.assertEqual(out, 'passed')
            self.assertEqual(path.read_bytes(), before)

    def test_two_process_lock_and_failed_close_retains_attachment(self):
        with tempfile.TemporaryDirectory() as directory:
            q = json.dumps(str(Path(directory) / 'basis.sexp'))
            live = Live()
            try:
                live.exchange(f"(basis91 'open {q})", rb'\(basis91 epoch 0')
                live.exchange("(basis91 'save)", rb'\(saved91\)')
                blocked = f"(assert (equal (basis91 'open {q}) '(rejected91 locked-or-path))) (print \"passed\")"
                self.assertEqual(maru(blocked), 'passed')
                live.send('(define original91 b91-checkpoint)\n(define-function no91 (p s e) false)\n(set b91-checkpoint no91)\n')
                live.exchange("(basis91 'close)", rb'\(rejected91 checkpoint\)')
                self.assertEqual(maru(blocked), 'passed')
                live.send('(set b91-checkpoint original91)\n')
                live.exchange("(basis91 'close)", rb'\(closed91\)')
                self.assertEqual(maru(f"(assert (= (car (basis91 'open {q})) 'basis91)) (basis91 'close) (print \"passed\")"), 'passed')
            finally:
                output = live.close()
            self.assertEqual(live.p.returncode, 0, output[-4000:])

    def test_malformed_input_limits_and_event_cap(self):
        out = maru("""
(basis91 'init '(r s))
(list-do p (list 42 (cons 'bad 42) '((r 0 9)) '((r 0 1) (s 2 3)) '((r 0 1) (r 0 1)))
 (assert (= (car (basis91 'probe () p 100)) 'rejected91) "bad pattern"))
(assert (= (car (basis91 'observe 'bad '((atom r (a b c))))) 'rejected91))
(assert (= (car (basis91 'observe 'bad '((atom r (a b)) (atom r (a b))))) 'rejected91))
(assert (= (car (basis91 'probe () '((r 0 1)) 200001)) 'rejected91))
(times-do 16 (basis91 'observe 'e ()) (basis91 'retract 'e))
(define before *b91-state*)
(assert (= (car (basis91 'learn)) 'rejected91) "event cap")
(assert (equal before *b91-state*) "no mutation")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_seeded_malformed_trees_fail_closed_without_native_crashes(self):
        rng = random.Random(91)
        atoms = [42, -1, 1, 'not executable (error)', []] + list(map(S,
                 ('basis-session91', 'execution-core91', 'basis91', 'reading91', 'observe91',
                  'interpret91', 'learn91', 'call91', 'fact91', 'r', 's', 'match91')))
        def tree(depth):
            if depth == 0 or rng.random() < .6:
                return rng.choice(atoms)
            return [tree(depth - 1) for _ in range(rng.randrange(8))]
        out = maru("""
(list-do x (read *standard-input*)
 (b91-pattern? x '(r s)) (b91-facts? x '(r s)) (b91-library? x '(r s))
 (b91-core? x) (b91-model? x) (b91-snapshot? x) (b91-state? x)
 (b91-infer x 'missing '((r 0 1)) 100 'basis)
 (b91-apply (b91-new '(r s)) x)
 (b91-snapshot? (cons 'basis-session91 x)))
(print "passed")""", dumps([tree(4) for _ in range(500)]))
        self.assertEqual(out, 'passed')

    def test_other_native_models_are_untouched(self):
        out = maru("(define old91 (list *dlm-model* *dlm-events* *s79-space* *c87-library* *b90-state*))\n" + TRAINED + """
(basis91 'run 'train 200000)
(assert (equal old91 (list *dlm-model* *dlm-events* *s79-space* *c87-library* *b90-state*)) "isolated")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_existing_basis_is_tried_and_can_fail_without_training_or_hallucination(self):
        out = maru(TRAINED + """
(basis91 'observe 'partial '((atom r (aa bb))))
(define before *b91-state*)
(define attempts (basis91 'inspect 'partial 200000))
(assert (= (car attempts) 'interpreted91) "completed trial")
(assert (not (dlm-nth attempts 1)) "no false positive reading")
(assert (= (dlm-length (dlm-nth attempts 3)) 2) "both existing schemas tried")
(list-do attempt (dlm-nth attempts 3) (assert (= (dlm-nth attempt 3) 0) "not applicable"))
(assert (equal before *b91-state*) "inspection does not learn")
(basis91 'interpret 'partial 200000)
(define coverage (basis91 'coverage 'partial))
(assert (not (dlm-nth coverage 4)) "no covered fact")
(assert (= (dlm-length (dlm-nth coverage 5)) 1) "isolated source retained")
(print "passed")""")
        self.assertEqual(out, 'passed')

    def test_empirical_coincidence_cannot_license_false_role_rewrite(self):
        facts = [[S('atom'), S(p), [S(a), S(b)]] for p in ('r', 's') for a in ('a', 'b') for b in ('a', 'b')]
        code = """
(basis91 'init '(r s))
(define facts (read *standard-input*))
(dump (basis91 'probe facts '((r 0 1) (s 1 2)) 200000)) (print "\\n")
(dump (basis91 'probe facts '((r 0 1) (s 0 2)) 200000)) (print "\\n")
(assert (not (b91-plan? '((r 0 1) (s 1 2)) '((fact91 r (0 1)) (fact91 s (0 2))) '(r s) ())))
"""
        rows = loads_many(maru(code, dumps(facts)))
        self.assertEqual(bindings(rows[0], facts), bindings(rows[1], facts))

    def test_data_only_input_driver_and_reject_trailing_or_executable_input(self):
        request = (ROOT / 'experiments/basis91/input-example.sexp').read_text()
        for suffix, success in [('', True), (' (error "not data")', False)]:
            p = subprocess.run([str(ROOT / 'scripts/run.sh'), 'basis91-input'], input=request + suffix,
                               text=True, capture_output=True, timeout=30)
            self.assertEqual(p.returncode == 0, success, p.stderr)
            if success:
                rows = loads_many(p.stdout)
                self.assertEqual(rows[-1][0], 'basis-session91')
                self.assertEqual(len([r for r in rows if r[0] == 'basis-result91']), 4)

    def test_measurement_driver_all_controls_with_independent_answer_oracle(self):
        import sys
        sys.path.insert(0, str(ROOT / 'adapters'))
        from basis91_experiment import run_experiment
        result = run_experiment(repeats=1, batches=1, seeds=(91,))
        self.assertEqual(len(result['records']), 16)
        self.assertEqual(sum(r['mismatches'] for r in result['records']), 0)
        self.assertEqual(result['summaries']['no-repeat']['basis']['basis_count'], 0)
        self.assertGreater(result['summaries']['fork-overhead']['basis']['model_bytes'],
                           result['summaries']['fork-overhead']['raw']['model_bytes'])

    def test_exhaustive_two_relation_graphs_all_roles_and_witness_ids(self):
        edges = [(p, a, b) for p in ('r', 's') for a in ('a', 'b') for b in ('a', 'b')]
        facts = [[S('atom'), S(p), [S(a), S(b)]] for p, a, b in edges]
        graphs = [[f for bit, f in enumerate(facts) if mask & (1 << bit)] for mask in range(256)]
        patterns = [[[S(p), x, y] for p, x, y in atoms] for atoms in [
            [('r', 0, 1), ('s', 1, 2)], [('r', 0, 1), ('s', 0, 2)],
            [('r', 0, 1), ('s', 2, 1)], [('r', 0, 1), ('s', 1, 0)],
            [('r', 0, 0), ('s', 0, 1)], [('r', 0, 1), ('s', 1, 2), ('r', 2, 3)],
            [('r', 0, 1), ('s', 0, 2), ('r', 2, 3)], [('r', 0, 0)]]]
        code = """
(basis91 'init '(r s))
(basis91 'observe 'train '((atom r (a b)) (atom s (b c)) (atom r (c d))
                         (atom r (p q)) (atom s (q z)) (atom r (z w))))
(basis91 'interpret 'train 200000) (basis91 'learn) (basis91 'learn)
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 2) "oracle basis depth")
(define request (read *standard-input*))
(list-do facts (car request)
 (assert (b91-facts? facts '(r s)) "oracle input")
 (list-do p (dlm-nth request 1)
  (list-do arm '(raw memo append basis)
   (dump (b91-query-on *b91-state* (list 'episode91 'oracle 0 facts false) p 200000 arm)) (print "\\n"))))
"""
        results = loads_many(maru(code, dumps([graphs, patterns])))
        self.assertEqual(len(results), 256 * 8 * 4)
        for i, graph in enumerate(graphs):
            for j, p in enumerate(patterns):
                expected = reference(p, graph)
                for result in results[(i * 8 + j) * 4:(i * 8 + j + 1) * 4]:
                    self.assertEqual(bindings(result, graph), expected, (i, p, result))
        print('BASIS91-ORACLE 256 graphs, 8 patterns, 4 arms, 8192 answer/witness checks, zero mismatches')


if __name__ == '__main__':
    unittest.main()
