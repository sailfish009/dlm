"""Shared-owner typed construction, no-repair admission, source revision, CPU oracles."""
import copy
import itertools
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_sequent import maru
from test_repl import Live
from sexp import Symbol as S, dumps, loads_many
from composition95_experiment import fixture, frame, oracle, run, z

ROOT = Path(__file__).resolve().parents[1]
DATA = fixture(nqueries=1)
QUIET = '(require "experiments/composition95/driver.l")\n(set i95-emit (lambda (x) ()))\n'
PREPARE = QUIET + '(define data95 \'%s)\n(i95-prepare data95)\n' % dumps(DATA)
CTX = dumps(DATA[7][0][2])
CH = dumps(DATA[5][1])
DH = dumps(DATA[6][1])


class Composition95Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = loads_many(maru(PREPARE + "(dump (basis91 'snapshot))"))[0]
        cls.base = "(assert (= (car (basis91 'restore '%s)) 'basis91))\n" % dumps(cls.snapshot)
        events = cls.snapshot[4]
        first = next(i for i, e in enumerate(events) if e[0] == 'compose95')
        cls.before_c = "(assert (= (car (basis91 'restore (b91-pack (b91-replay '(r s) '%s)))) 'basis91))\n" % dumps(events[:first])
        cls.before_d = "(assert (= (car (basis91 'restore (b91-pack (b91-replay '(r s) '%s)))) 'basis91))\n" % dumps(events[:-1])
        cls.cp = events[first][1]
        cls.dp = events[-1][1]

    def checked(self, text, prefix=None):
        out = maru((self.base if prefix is None else prefix) + text + '\n(print "passed")')
        self.assertEqual(out, 'passed')

    def test_same_owner_and_global_prefix_ids_no_numeric_engine_state(self):
        self.checked("""
(assert (= (car *b91-state*) 'basis-state91)) (assert (= (dlm-nth *b91-state* 1) 2))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 6)) (assert (= (dlm-nth *b91-state* 7) 6))
(assert (equal (map car (dlm-nth *b91-state* 4)) '(basis91 numeric95 numeric95 numeric95 composite95 composite95)))
(assert (not *e93-state*) "standalone EML93 owner never initialized")
(assert (equal (a92-basis-ids (dlm-nth *b91-state* 4)) '(1)))
(assert (b91-state? *b91-state*)) (assert (b91-snapshot? (basis91 'snapshot)))
""")

    def test_relation_selects_numeric_pairs_and_new_numeric_and_composite_are_atomic(self):
        p = self.cp
        self.assertEqual([m[0] for m in p[2]], ['numeric95', 'composite95'])
        self.assertEqual(p[2][0][6], ['paired95', DATA[5][1], 1, [['measure95', 0], ['measure95', 2]]])
        self.assertEqual(p[2][1][4], [['measure95', 0], ['measure95', 2]])
        self.assertEqual(len(p[3][4]), 6)
        self.checked("""
(define old *b91-state*)
(assert (= (dlm-length (dlm-nth old 4)) 3))
(define proposal (basis91 'typed-proposal %s 3 200000))
(assert (= (car proposal) 'proposal95)) (assert (equal old *b91-state*))
(assert (= (car (b91-commit (list 'compose95 proposal))) 'committed91))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 5))
(assert (= (dlm-nth *b91-state* 7) 5))
""" % CH, self.before_c)

    def test_compound_output_really_supplies_next_formation_and_is_not_new_support(self):
        self.assertEqual(self.dp[2], [[S('composite95'), 6, 1, 2, [[S('output95'), 5]], DATA[6][1]]])
        self.assertEqual(len(self.dp[3][4]), 6)
        self.assertEqual(len(self.dp[3][5]), 6)
        for proof in self.dp[3][5]:
            self.assertEqual(proof[:2], ['support95', DATA[6][1]])
            self.assertIn(5, proof[6][3])
            self.assertTrue(proof[6][1])
        self.checked("""
(define proposal (basis91 'typed-proposal %s 3 200000))
(assert (= (dlm-length (dlm-nth proposal 2)) 1))
(assert (equal (dlm-nth (car (dlm-nth proposal 2)) 4) '((output95 5))))
(assert (= (dlm-nth (dlm-nth proposal 4) 2) 0) "no new numeric search for D")
""" % DH, self.before_d)

    def test_causal_ablations_and_logical_representation_control(self):
        reports = {arm: run(fixture(0, 'principal93', arm, 1)) for arm in
                   ('shared95', 'logical95', 'no-relational95', 'no-numeric95', 'no-output95')}
        self.assertEqual(len({r['data_sha256'] for r in reports.values()}), 1)
        for arm in ('shared95', 'logical95', 'no-output95'):
            self.assertEqual(reports[arm]['counts']['complete'], 2)
            self.assertEqual(reports[arm]['counts']['mismatches'], 0)
        for arm in ('no-relational95', 'no-numeric95'):
            self.assertEqual(reports[arm]['counts']['complete'], 0)
            self.assertEqual(reports[arm]['counts']['unknown'], 2)
        self.assertEqual(reports['shared95']['profile'][1:4], [1, 3, 2])
        self.assertEqual(reports['no-output95']['profile'][1:4], [1, 4, 2])
        # Re-search can recover, but forms another numeric definition, not output(C).
        self.assertEqual(reports['no-output95']['library'][-1][4], [['measure95', 0], ['measure95', 2]])
        self.assertEqual(reports['shared95']['library'][-1][4], [['output95', 5]])

    def test_core_only_inference_without_observations_learners_replay_or_live_owner(self):
        self.checked("""
(define standalone (s79-field (s79-field (basis91 'model) 2 ()) 4 ()))
(basis91 'reset) (eml93 'reset)
(define-function unavailable95 args (error "training/discovery forbidden"))
(set c95-propose unavailable95) (set c95-build-scopes unavailable95) (set e93-search unavailable95)
(set e93-fit unavailable95) (set b91-replay unavailable95) (set b91-data-patterns unavailable95)
(define answer (basis91 'typed-infer standalone %s '%s 200000))
(assert (equal (dlm-nth answer 1) 'complete)) (assert (= (dlm-length (dlm-nth answer 3)) 9))
(assert (not *b91-state*)) (assert (not *e93-state*))
""" % (DH, CTX))

    def test_missing_measure_unbound_or_unsupported_numeric_domain_is_unknown(self):
        self.checked("""
(define ctx '%s)
(define one-measure (s79-field ctx 4 (list (car (dlm-nth ctx 4)))))
(assert (= (dlm-nth (basis91 'typed-query %s one-measure 200000) 1) 'unknown))
(define tiny (list 'context95 'tiny95 1 '((atom r (a b)) (atom s (b c)))
  '((measure95 a (z93 1000 0)) (measure95 c (z93 2000 0)))))
(assert (= (dlm-nth (basis91 'typed-query %s tiny 200000) 1) 'unknown))
(assert (= (dlm-nth (basis91 'typed-query %s ctx 0) 1) 'unknown))
""" % (CTX, CH, CH, CH))

    def test_object_ids_never_coerce_to_numbers_and_alias_roles_are_preserved(self):
        self.checked("""
(define context '(context95 alias95 1 ((atom r (x x)) (atom s (x c)))
  ((measure95 x (z93 1400000 0)) (measure95 c (z93 400000 0)))))
(define answer (basis91 'typed-query %s context 200000))
(assert (= (dlm-nth answer 1) 'complete))
(assert (equal (dlm-nth (car (dlm-nth answer 3)) 1) '(x x c)))
(assert (e93-close? (dlm-nth (car (dlm-nth answer 3)) 2) '(z93 1000000 0) 1000))
(assert (not (c95-measures? '((measure95 x x)))))
(assert (not (c95-measures? '((measure95 1400000 (z93 1400000 0))))))
""" % CH)

    def test_empty_complete_relation_is_empty_not_numeric_false(self):
        self.checked("""
(define answer (basis91 'typed-query %s '(context95 empty95 1 () ()) 200000))
(assert (equal answer '(typed-answer95 complete empirical95 ())))
""" % CH)

    def test_output_scope_checks_prevent_negative_intermediate_becoming_positive_scope(self):
        self.checked("""
(define context '(context95 negative95 1 ((atom r (a b)) (atom s (b c)))
 ((measure95 a (z93 300000 0)) (measure95 c (z93 1200000 0)))))
(assert (= (dlm-nth (basis91 'typed-query %s context 200000) 1) 'complete))
(assert (= (dlm-nth (basis91 'typed-query %s context 200000) 1) 'unknown))
""" % (CH, DH))

    def test_checker_rejects_omitted_wrong_or_forged_proof_rows_without_reference_repair(self):
        self.checked("""
(define actual-worker c95-worker)
(set c95-worker (lambda (model m context raw fuel) (list 'work95 'complete () fuel)))
(assert (= (car (basis91 'typed-query %s '%s 200000)) 'rejected95))
(set c95-worker (lambda (model m context raw fuel)
 (let* ((v (actual-worker model m context raw fuel)) (rows (dlm-nth v 2)))
  (s79-field v 2 (cons (s79-field (car rows) 2 '(z93 0 0)) (cdr rows))))))
(assert (= (car (basis91 'typed-query %s '%s 200000)) 'rejected95))
(set c95-worker (lambda (model m context raw fuel)
 (let* ((v (actual-worker model m context raw fuel)) (rows (dlm-nth v 2)))
  (s79-field v 2 (cons (s79-field (car rows) 3 '(evidence95 fake95 1 () ())) (cdr rows))))))
(assert (= (car (basis91 'typed-query %s '%s 200000)) 'rejected95))
""" % (CH, CTX, CH, CTX, CH, CTX))

    def test_checker_accepts_only_semantically_equal_row_reordering(self):
        self.checked("""
(define actual-worker c95-worker)
(set c95-worker (lambda (model m context raw fuel)
 (let ((v (actual-worker model m context raw fuel))) (s79-field v 2 (s79-reverse (dlm-nth v 2))))))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'complete))
""" % (CH, CTX))

    def test_forged_numeric_values_support_and_missing_claims_are_rejected_atomically(self):
        variants = []
        for change in ('values', 'rows', 'proofs', 'scope', 'wire'):
            p = copy.deepcopy(self.dp)
            if change == 'values': p[3][6][0] = z(0)
            elif change == 'rows': p[3][4].pop()
            elif change == 'proofs': p[3][5][0][6][1] = []
            elif change == 'scope': p[3][3] = [S('negative93')]
            else: p[2][0][4] = [[S('measure95'), 0]]
            variants.append(p)
        self.checked("""
(define old (basis91 'snapshot))
(list-do p '%s
 (assert (= (car (b91-commit (list 'compose95 p))) 'rejected91))
 (assert (equal old (basis91 'snapshot))))
""" % dumps(variants), self.before_d)

    def test_relation_witness_support_is_not_accepted_from_unmatched_object_tuples(self):
        self.checked("""
(define channel (car (dlm-nth (dlm-nth *b91-state* 8) 3)))
(define targets (dlm-nth channel 6))
(set targets (cons (s79-field (car targets) 2 '(foreign b c)) (cdr targets)))
(assert (= (car (basis91 'observe-values %s (dlm-nth channel 3) (dlm-nth channel 5) targets)) 'committed91))
(define p '%s)
(assert (= (car (b91-commit (list 'compose95 p))) 'rejected91))
""" % (CH, dumps(self.cp)), self.before_c)

    def test_derived_values_cannot_be_ingested_as_observed_support_and_duplicate_ids_rejected(self):
        self.checked("""
(define channel (car (dlm-nth (dlm-nth *b91-state* 8) 3)))
(define targets (dlm-nth channel 6)) (define old (basis91 'snapshot))
(assert (= (car (basis91 'observe-values %s (dlm-nth channel 3) (dlm-nth channel 5)
 (cons (s79-field (car targets) 0 'derived95) (cdr targets)))) 'rejected91))
(assert (= (car (basis91 'observe-values %s (dlm-nth channel 3) (dlm-nth channel 5)
 (cons (car targets) targets))) 'rejected91))
(assert (equal old (basis91 'snapshot)))
""" % (CH, CH))

    def test_counterexample_withdrawal_dependency_propagation_and_restoration(self):
        self.checked("""
(define original (basis91 'snapshot)) (define historical (basis91 'model))
(define f (dlm-nth *b91-state* 8)) (define channel (car (dlm-nth f 3)))
(define targets (dlm-nth channel 6))
(define bad (cons (s79-field (car targets) 3 '(z93 99000000 0)) (cdr targets)))
(assert (= (car (basis91 'observe-values %s (dlm-nth channel 3) (dlm-nth channel 5) bad)) 'committed91))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 6) "definitions remain")
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'unknown))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'unknown))
(assert (= (dlm-nth (basis91 'typed-infer historical %s '%s 200000) 1) 'complete))
(assert (= (car (basis91 'observe-values %s (dlm-nth channel 3) (dlm-nth channel 5) targets)) 'committed91))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'complete))
(assert (not (equal historical (basis91 'model))))
(assert (= (dlm-nth historical 5) (dlm-nth (basis91 'model) 5)))
(assert (b91-snapshot? (basis91 'snapshot)))
""" % (CH, CH, CTX, DH, CTX, DH, CTX, CH, DH, CTX))

    def test_source_fact_version_changes_withdraw_stale_numeric_pairing(self):
        self.checked("""
(define channel (car (dlm-nth (dlm-nth *b91-state* 8) 3)))
(assert (= (car (basis91 'retract (dlm-nth channel 3))) 'committed91))
(assert (= (car (basis91 'observe (dlm-nth channel 3) '((atom r (a b))))) 'committed91))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'unknown))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'unknown))
""" % (CH, CTX, DH, CTX))

    def test_retraction_distinguishes_definitional_prefixes_and_empirical_application(self):
        self.checked("""
(assert (= (car (basis91 'retract-values 'calibration95 "nalpha")) 'committed91))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'complete)
 "C's subtraction program is independently supported by C observations")
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'unknown)
 "D applies the withdrawn empirical exp correspondence directly")
(assert (= (car (basis91 'retract-values 'channel95 %s)) 'committed91))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'unknown))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 6))
""" % (CH, CTX, DH, CTX, CH, CH, CTX))

    def test_common_library_type_edges_forward_calls_wrong_branches_and_cycles_rejected(self):
        lib = copy.deepcopy(self.snapshot[2][3])
        variants = []
        for name in ('numeric-to-object', 'composite-to-number', 'forward', 'branch', 'bad-expansion'):
            v = copy.deepcopy(lib)
            if name == 'numeric-to-object': v[3][3] = [S('call93'), 1, [[S('x93'), 0]]]
            elif name == 'composite-to-number': v[5][4] = [[S('output95'), 4]]
            elif name == 'forward': v[4][4] = [[S('output95'), 6], [S('measure95'), 2]]
            elif name == 'branch': v[3][5] = S('lower93')
            else: v[3][4] = [S('x93'), 0]
            variants.append(v)
        self.checked("""
(list-do lib '%s
 (define model (s79-field (basis91 'model) 3 lib))
 (assert (not (b91-model? model))))
""" % dumps(variants))

    def test_shared_relational_interpretation_and_later_formation_continue_after_typed_learning(self):
        self.checked("""
(assert (= (car (basis91 'observe 'later95 '((atom r (a b)) (atom s (b c)) (atom s (b d))
 (atom r (u v)) (atom s (v w)) (atom s (v z))))) 'committed91))
(assert (= (car (basis91 'interpret-controlled 'later95 200000 'adaptive92)) 'committed91))
(assert (= (car (basis91 'learn)) 'committed91))
(assert (= (dlm-length (dlm-nth *b91-state* 4)) 7))
(assert (b91-relational? (b91-module (dlm-nth *b91-state* 4) 7)))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'complete))
(assert (b91-snapshot? (basis91 'snapshot)))
""" % (DH, CTX))

    def test_three_level_composite_outputs_remain_reusable(self):
        import math
        fr = frame('channel-e', [.71, .93, 1.11], [.17, .36, .53], 5, True)
        for t in fr[5]:
            values = {m[1]: m[2][1] / 1e6 for m in fr[4]}
            t[3] = z(math.exp(math.exp(values[t[2][0]] - values[t[2][2]])))
        self.checked(QUIET + """
(define f '%s) (i95-observe f)
(assert (= (car (basis91 'compose (dlm-nth f 1) 3 200000)) 'committed91))
(assert (equal (dlm-nth (b91-module (dlm-nth *b91-state* 4) 7) 4) '((output95 6))))
(assert (b91-snapshot? (basis91 'snapshot)))
""" % dumps(fr))

    def test_frozen_core_and_encoding_migration_do_not_mutate_inflight_or_scalar_epoch(self):
        data = fixture(0, 'principal93', 'logical95', 1)
        self.checked("""
(define old (basis91 'model)) (define oldepoch (dlm-nth old 5))
(assert (= (car (basis91 'encode 1 'eml94 'principal93)) 'committed91))
(assert (= oldepoch (dlm-nth (basis91 'model) 5))) (assert (not (equal old (basis91 'model))))
(assert (= (dlm-nth (basis91 'typed-infer old %s '%s 200000) 1) 'complete))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'complete))
""" % (DH, CTX, DH, CTX), QUIET + "(i95-prepare '%s)\n" % dumps(data))

    def test_malformed_trees_rejected_without_native_crash(self):
        rng = random.Random(95)
        atoms = [[], 0, -1, 99, S('numeric95'), S('output95'), 'x', S('z93'), S('scope95')]
        def tree(depth):
            if depth == 0 or rng.random() < .5: return copy.deepcopy(rng.choice(atoms))
            return [tree(depth - 1) for _ in range(rng.randrange(8))]
        trees = [tree(4) for _ in range(400)]
        self.checked("""
(list-do x '%s
 (c95-measures? x) (c95-targets? x) (c95-context? x '(r s))
 (c95-core? x (dlm-nth *b91-state* 4)) (b91-model? x) (c95-check-proposal *b91-state* x))
""" % dumps(trees))

    def test_native_query_subsets_both_branches_match_independent_assignment_and_numeric_oracle(self):
        # 64 source subsets x 2 channels x 2 branches = 256 independently checked queries.
        for branch in ('principal93', 'lower93'):
            data = fixture(0, branch, nqueries=0)
            context = fixture(nqueries=1)[7][0][2]
            for mask in range(64):
                q = copy.deepcopy(context)
                q[1] = f'mask-{mask}'
                q[3] = [f for i, f in enumerate(context[3]) if mask & (1 << i)]
                for ch in (data[5][1], data[6][1]):
                    data[7].append([S('typed-query95'), ch, copy.deepcopy(q)])
            report = run(data)
            self.assertEqual(report['counts']['complete'], 128)
            self.assertEqual(report['counts']['mismatches'], 0)
            self.assertEqual(report['counts']['unknown'], 0)
            self.assertEqual(report['counts']['checked_rows'], 288)

    def test_shared_checkpoint_replay_fresh_process_lock_and_failed_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / 'shared.sexp')
            self.checked("""
(assert (= (car (basis91 'open %s)) 'basis91))
(assert (= (car (basis91 'save)) 'saved91))
(define old (basis91 'snapshot)) (define expected *b91-expected*)
(set *b91-expected* '(missing))
(assert (= (car (basis91 'retract-values 'channel95 %s)) 'rejected91))
(assert (equal old (basis91 'snapshot)))
(set *b91-expected* expected)
(assert (= (car (basis91 'close)) 'closed91))
""" % (dumps(path), CH))
            self.checked("""
(assert (= (car (basis91 'open %s)) 'basis91))
(assert (= (dlm-nth (basis91 'typed-query %s '%s 200000) 1) 'complete))
(assert (b91-snapshot? (basis91 'snapshot)))
(assert (= (car (basis91 'close)) 'closed91))
""" % (dumps(path), DH, CTX), '')
            holder = Live()
            try:
                holder.exchange("(basis91 'open %s)\n" % dumps(path), b'basis91 epoch')
                self.checked("(assert (equal (basis91 'open %s) '(rejected91 locked-or-path)))\n" % dumps(path), '')
            finally:
                holder.close()

    def test_snapshot_forged_applicability_or_omitted_raw_history_rejected(self):
        variants = []
        p = copy.deepcopy(self.snapshot)
        p[2][6][2].pop()
        variants.append(p)
        p = copy.deepcopy(self.snapshot)
        p[4].pop()
        variants.append(p)
        p = copy.deepcopy(self.snapshot)
        p[2][6][2][0][3] = 31
        variants.append(p)
        self.checked("""
(list-do x '%s (assert (not (b91-snapshot? x))))
""" % dumps(variants))

    def test_data_only_input_rejects_trailing_datum(self):
        p = subprocess.run([str(ROOT / 'scripts/run.sh'), 'compose95-input'],
                           input=dumps(DATA) + '\n(unsafe-execution)\n', text=True,
                           capture_output=True, timeout=30)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('trailing composition95 input', p.stderr + p.stdout)


if __name__ == '__main__':
    unittest.main()
