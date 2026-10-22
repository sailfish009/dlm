"""Regression contracts for the v0.0079 review findings fixed in v0.0080."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'adapters'))
from sexp import loads_many
from test_sequent import maru


class Review80Tests(unittest.TestCase):
    def test_malformed_signature_is_rejected_not_a_crash(self):
        out = maru('''(dump (d79-define (s79-new) 'd 42 '(top))) (print "\\n")
(dump (e79-transition (s79-new) (list 'define 'd "abc" '(top)))) (print "\\n")
(dump (d79-define (s79-new) 'd (cons 'a 'b) '(top))) (print "\\n")''')
        self.assertEqual(out.strip().splitlines(), ['(rejected definition)'] * 3)

    def test_check_failure_finishes_the_purpose_job(self):
        out = maru('''(define s (s79-new))
(set s (s79-job-put s (list 'job79 'j 'proof 'checking () () ())))
(define r (s79-check-create s '((p 0)) (sq-sequent '() '((pred p ())))
  '(certificate classical-prop-v1 99 ()) (list 'job 'j)))
(set s (s79-run (car r) 50))
(dump (list 'job-status (dlm-nth (s79-job s 'j) 3)
            'result (dlm-nth (s79-job s 'j) 5)
            'check-status (dlm-nth (s79-unit s (car (dlm-nth r 1))) 4)
            'remaining (+ (dlm-length (dlm-nth s 5)) (dlm-length (dlm-nth s 6)))))''')
        self.assertEqual(loads_many(out)[0],
            ['job-status', 'done', 'result', ['result', 'failed', ['invalid-root']],
             'check-status', 'failed', 'remaining', 0])

    def test_alternative_exhaustion_is_terminal(self):
        out = maru('''(define s (s79-run (s79-program-job (s79-new) 'enumerate
 '((choose (((accept first)) ((fail no-more)))))) 100))
(set s (s79-run (s79-program-resume s 'enumerate true) 100))
(dump (list 'exhaustion-status (dlm-nth (s79-job s 'enumerate) 3)
 'remaining-events (+ (dlm-length (dlm-nth s 5)) (dlm-length (dlm-nth s 6)))))''')
        self.assertEqual(loads_many(out)[0],
            ['exhaustion-status', 'exhausted', 'remaining-events', 0])

    def test_child_job_rejection_and_beth_capacity_are_explicit(self):
        out = maru('''(define t (s79-new))
(times-do 63 (set t (e79-transition t (list 'define
 (concat-strings "d" (number->string (dlm-length (dlm-nth t 12)))) '((p 0)) '(pred p ())))))
(set t (e79-transition t '(beth b1 ((p 0)) (pred p ()) (pred p ()))))
(set t (e79-transition t '(beth b2 ((p 0)) (pred p ()) (pred p ()))))
(set t (e79-transition t '(run 1000)))
(dump (list 'count (dlm-length (dlm-nth t 12))
 'b1 (dlm-nth (s79-job t 'b1) 3) 'b2 (dlm-nth (s79-job t 'b2) 3)
 'b2-result (dlm-nth (s79-job t 'b2) 5))) (print "\\n")
(define u (d79-define (s79-new) 'd '((p 0)) '(pred p ())))
(define premises ())
(times-do 256 (set premises (cons '(pred p ()) premises)))
(set u (s79-run (d79-use u 'use 'd premises) 1000))
(dump (list 'job-status (dlm-nth (s79-job u 'use) 3)
 'result (dlm-nth (s79-job u 'use) 5)
 'unit-status (dlm-nth (s79-unit u (dlm-nth (s79-job u 'use) 4)) 4)))''')
        rows = loads_many(out)
        self.assertEqual(rows[0][0:6], ['count', 64, 'b1', 'done', 'b2', 'done'])
        self.assertEqual(rows[0][6], 'b2-result')
        self.assertEqual(rows[0][7][0:2], ['beth79', 'incomplete'])
        self.assertEqual(rows[0][7][2], 'capacity')
        self.assertEqual(rows[1][0:4], ['job-status', 'done', 'result',
            ['internal79', 'rejected', ['rejected', 'proof-job']]])
        self.assertEqual(rows[1][4:6], ['unit-status', 'failed'])

    def test_annotation_traversal_is_linear_in_certificate_dag(self):
        code = (ROOT / 'docs/review-evidence/annotation.l').read_text()
        rows = loads_many(maru(code))
        self.assertEqual([r[1] for r in rows], [2, 4, 6, 8, 10])
        self.assertEqual([r[5] for r in rows], [7, 13, 19, 25, 31])

if __name__ == '__main__':
    unittest.main()
