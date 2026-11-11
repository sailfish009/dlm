;;; synth_fallback.l — abductive fallback when the head readout has no valid rule.
;;; If predicted head h is absent from the unifier-valid set, synthesize a rule
;;; h :- all on-bits of the image, then require p-prove/p-proof-check.

(define-function synth-body (bits i)
  (if (>= i 196) ()
      (l-append (if (= (l-nth bits i) 1)
                    (list (l-atom 'on (list (number->string i))))
                    ())
                (synth-body bits (+ i 1)))))

(define-function head-in-valid? (h valid)
  (if valid (if (= h (l-nth rule-heads (car valid))) 1
                (head-in-valid? h (cdr valid)))
      0))

(define-function pick-head-in-valid (h valid)
  (if valid (if (= h (l-nth rule-heads (car valid))) (car valid)
                (pick-head-in-valid h (cdr valid)))
      -1))

(define-function synth-case (c)
  (let* ((bits (l-nth case-bits c))
         (p (head-pred bits))
         (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
         (in? (head-in-valid? p valid))
         (pick (if (= in? 1) (pick-head-in-valid p valid)
                   (head-rule-score bits valid 0 -999999999 -1)))
         (head p)
         (synth (if (= in? 1) 0 1))
         (rules2 (if (= synth 1)
                     (l-append rules218
                       (list (l-rule (l-atom 'digit (list (number->string p)))
                                     (synth-body bits 0))))
                     rules218))
         (goal (l-atom 'digit (list (number->string head))))
         (facts (l-nth (l-nth *mnist-cases* c) 1))
         (pr (p-prove facts rules2 goal 50000))
         (pok (if (and pr (equal (l-nth pr 1) 'proof))
                  (if (p-proof-check facts rules2 goal (l-nth pr 2)) 1 0) 0))
         (lab (string->number (car (l-nth *mnist-cases* c)))))
    (print "CASE " c " HEAD " head " LABEL " lab " SYNTH " synth
           " PROOF " pok " CORRECT " (if (= head lab) 1 0) "\n")))

(define-function synth-run (c)
  (if (< c 10) (begin (synth-case c) (synth-run (+ c 1))) ()))

(head-train 10)
(synth-run 0)
