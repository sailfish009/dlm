;;; main.l — run the native deductive transformer over 10 MNIST cases.
(define-function dt-run-case (c)
  (let* ((bits (l-nth case-bits c))
         (model (l-nth models c))
         (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
         (scores (dt-selector-scores bits valid model))
         (pick (dt-pick-scores bits valid scores))
         (head (if (< pick 0) -1 (l-nth rule-heads pick)))
         (facts (l-nth (l-nth *mnist-cases* c) 1))
         (goal (l-atom 'digit (list (number->string head))))
         (pr (if (< head 0) () (p-prove facts rules218 goal 50000)))
         (pok (if (and pr (equal (l-nth pr 1) 'proof))
                  (if (p-proof-check facts rules218 goal (l-nth pr 2)) 1 0)
                  0)))
    (print "CASE " c " VALID " valid " PICK " pick " HEAD " head
           " LABEL " (car (l-nth *mnist-cases* c)) " PROOF " pok
           " SCORES " scores "\n")))

(define-function dt-run (c)
  (if (< c 10) (begin (dt-run-case c) (dt-run (+ c 1))) ()))

(dt-run 0)
