;;; -*- mode: lisp; coding: us-ascii -*-
;;; Run: maru boot.l dlm.l dlm-tests.l

(define-function dlm-check (condition name)
  (if condition (println "PASS: " name) (error "FAIL: " name)))

(let* ((x (dlm-var 'x)) (y (dlm-var 'y)) (z (dlm-var 'z))
       (facts (list (dlm-atom 'edge 'a 'b) (dlm-atom 'edge 'b 'c)
                    (dlm-atom 'edge 'c 'd)))
       (base (dlm-rule (dlm-atom 'reach x y) (dlm-atom 'edge x y)))
       (rec (dlm-rule (dlm-atom 'reach x z)
                      (dlm-atom 'reach x y) (dlm-atom 'edge y z)))
       (rules (list base rec))
       (target (dlm-atom 'reach 'a 'd))
       (proof (dlm-prove facts rules target)))
  (dlm-check (dlm-match (dlm-atom 'p 'a) (dlm-atom 'p 'a) ())
             "constant match with empty environment")
  (dlm-check (not (dlm-match (dlm-atom 'p x x) (dlm-atom 'p 'a 'b) ()))
             "repeated variable conflict")
  (dlm-check (not (dlm-safe? (dlm-rule (dlm-atom 'q x) (dlm-atom 'p y))))
             "unsafe rule recognized")
  (dlm-check (dlm-member? target (dlm-closure facts rules)) "recursive closure")
  (dlm-check (not (dlm-member? (dlm-atom 'reach 'd 'a) (dlm-closure facts rules)))
             "no reversed derivation")
  (dlm-check (dlm-verify-proof proof facts rules) "proof verified")
  (dlm-check (not (dlm-verify-proof proof facts ())) "absent rule rejected")
  (dlm-check (not (dlm-verify-proof
                    (dlm-rule-proof (dlm-atom 'reach 'd 'a) rec
                                     (dlm-nth proof 4)) facts rules))
             "forged conclusion rejected")
  (let* ((e (dlm-episode 'test facts (list target) (list target)))
         (v (dlm-evaluate rec (list e) (list base))))
    (dlm-check (not (dlm-nth v 6)) "explicit contradiction blocks admission")))

(dlm-demo)
(println "DLM tests complete")
