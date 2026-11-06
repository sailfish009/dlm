;;; 0.0107 — the transition that was missing: observations stay, the basis moves.
;;; Three records share a structure: one owner makes three distinct calls.
;;; The core learns a 2-atom unit, then a 3-atom unit that CALLS it. The 3-atom
;;; query plan drops 3 -> 2 steps while every answer and witness stays the same.

(set *p107-edb* '(calls))
(dlm 'rules ())

(define-function ns-obs (id owner a b c)
  (dlm 'observe id "fixture" id 'demo
    (list (p107-atom 'calls (list owner a))
          (p107-atom 'calls (list owner b))
          (p107-atom 'calls (list owner c)))))
(ns-obs 'r1 "m1" "open" "read" "close")
(ns-obs 'r2 "m2" "open" "write" "close")
(ns-obs 'r3 "m3" "open" "read" "log")

(define v0 (p107-var 'v0)) (define v1 (p107-var 'v1))
(define v2 (p107-var 'v2)) (define v3 (p107-var 'v3))
(define q2 (list (p107-atom 'calls (list v0 v1)) (p107-atom 'calls (list v0 v2))))
(define q3 (list (p107-atom 'calls (list v0 v1)) (p107-atom 'calls (list v0 v2))
                 (p107-atom 'calls (list v0 v3))))

(dlm 'run 3 200000)
(print "before defs=" (p107-len (p107-defs-of *p107-state*)) "\n")
(dump (dlm 'plan q3)) (print "\n")
(define answer-before (dlm 'answer 'demo q3))
(print "before rows=" (p107-len (p107-nth answer-before 4)) " calls=" (p107-nth answer-before 5) "\n")

(dlm 'run 4 200000)
(print "after defs=" (p107-len (p107-defs-of *p107-state*)) "\n")
(dump (dlm 'defs)) (print "\n")
(dump (dlm 'plan q3)) (print "\n")
(dump (dlm 'plan q2)) (print "\n")
(define answer-after (dlm 'answer 'demo q3))
(print "after rows=" (p107-len (p107-nth answer-after 4)) "\n")
(print "plan-calls-after=" (p107-nth answer-after 5) " plan-steps=" (p107-nth answer-after 6) "\n")
(define raw-after (dlm 'answer-raw 'demo q3))
(print "raw-calls-after=" (p107-nth raw-after 5) "\n")
(print "answers-identical=" (equal (p107-nth answer-before 4) (p107-nth answer-after 4)) "\n")

;;; retract two records: the data changes, the units stay, support decides activity
(dlm 'retract 'r2) (dlm 'retract 'r3)
(dump (dlm 'defs)) (print "\n")
(dump (dlm 'plan q3)) (print "\n")
(print "answers-after-retract=" (p107-len (p107-nth (dlm 'answer 'demo q3) 4)) "\n")
(print "done-learn\n")
