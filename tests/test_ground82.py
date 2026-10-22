"""Ground graph validity is independent of its spatial candidate index."""
import unittest
from test_sequent import maru
from sexp import loads_many

BASE = '''(define s (g82-new '((p 0))))
(set s (g82-evidence s 'e1 "source-1" 'observed "digest-1" "t1"))
(set s (g82-evidence s 'e2 "source-2" 'observed "digest-2" "t2"))
(set s (g82-observe s 'a '(pred p ()) 'e1))
(set s (g82-observe s 'a '(pred p ()) 'e2))
(define cert (dlm-nth (sq-search '(problem classical-prop-v1 ((p 0))
 (sequent classical-prop-v1 ((pred p ())) ((pred p ())))) 100 'fixed) 2))
(set s (g82-derive s 'b '(pred p ()) '(a) cert))
(set s (g82-place s 'a '(0 0 0)))
(set s (g82-place s 'b '(20 0 0)))
'''


class Ground82Tests(unittest.TestCase):
    def test_independent_support_and_retraction(self):
        out = maru(BASE + '''(set s (g82-retract s 'e1))
(assert (g82-active? s 'b) "independent evidence survives")
(set s (g82-retract s 'e2))
(assert (not (g82-active? s 'a)) "observation unsupported")
(assert (not (g82-active? s 'b)) "dependent unsupported")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_alternative_derivations_and_unsupported_cycle(self):
        out = maru(BASE + '''(set s (g82-observe s 'c '(pred p ()) 'e2))
(set s (g82-derive s 'b '(pred p ()) '(c) cert))
(set s (g82-derive s 'a '(pred p ()) '(b) cert))
(set s (g82-retract s 'e1))
(assert (g82-active? s 'b) "alternate support")
(set s (g82-retract s 'e2))
(assert (not (g82-active? s 'a)) "cycle cannot support itself")
(assert (not (g82-active? s 'b)) "least fixed point")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_coordinate_invariance_and_fallback(self):
        out = maru(BASE + '''(define old s)
(set s (g82-place s 'b '(63 63 63)))
(assert (equal (dlm-nth old 3) (dlm-nth s 3)) "semantic graph unchanged")
(assert (= (dlm-nth old 6) (dlm-nth s 6)) "semantic revision unchanged")
(assert (equal (g82-reindex s) s) "index rebuild exact")
(dump (g82-query s '(pred p ()) '(0 0 0) 0 false)) (print "\\n")
(dump (g82-query s '(pred p ()) '(0 0 0) 0 true))''')
        local, full = loads_many(out)
        self.assertEqual(local[1:4], ['incomplete', ['a'], 1])
        self.assertEqual(full[1:4], ['complete', ['a', 'b'], 2])

    def test_local_relaxation_preserves_graph(self):
        out = maru(BASE + '''(define old s)
(define before (g82-cost s 'b '(20 0 0)))
(set s (g82-relax s 'b 12))
(assert (equal (dlm-nth old 3) (dlm-nth s 3)) "placement cannot change proof")
(assert (< (g82-cost s 'b (s79-at (dlm-nth s 4) 'b)) before) "dependency distance reduced")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_invalid_inputs_and_forged_proofs(self):
        out = maru(BASE + '''(dump (g82-place s 'a '(64 0 0))) (print "\\n")
(dump (g82-place s 'a 42)) (print "\\n")
(dump (g82-derive s 'evil '(bottom) '(a) cert)) (print "\\n")
(dump (g82-observe s 'a '(top) 'e1)) (print "\\n")
(dump (g82-evidence s 'e1 "other" 'observed "changed" "t3"))''')
        self.assertTrue(all(r[0] == 'rejected' for r in loads_many(out)))

    def test_snapshot_replay_rejects_forged_layout(self):
        out = maru('''(define log '((evidence e "source" observed "digest" "t")
 (observe a (pred p ()) e) (place a (3 4 5)) (relax a 1)))
(define snap (g82-snapshot '((p 0)) log))
(assert (equal (g82-restore snap) (dlm-nth snap 4)) "restore exact")
(define forged (s79-field snap 4 (g82-place (dlm-nth snap 4) 'a '(0 0 0))))
(dump (g82-restore forged)) (print "\\n")
(dump (g82-replay '((p 0)) '((eval malicious))))''')
        self.assertEqual(loads_many(out), [['rejected', 'snapshot'], ['rejected', 'replay']])


if __name__ == '__main__':
    unittest.main()
