;;; -*- mode: lisp; coding: us-ascii -*-
;;; Reverse target arguments; preserve fixed inputs and explicit negatives.
(define-function sl-scramble (episodes)
  (let ((result ()))
    (list-do e episodes
      (let ((changed ()))
        (list-do a (dlm-nth e 3)
          (set changed (dlm-add changed
            (dlm-atom (dlm-pred a) (dlm-nth (dlm-args a) 1) (car (dlm-args a))))))
        (set result (dlm-append result
          (list (dlm-episode (dlm-nth e 1) (dlm-nth e 2) changed
            (dlm-difference (dlm-union (dlm-nth e 4) (dlm-nth e 3)) changed)))))))
    result))
(define *sl-scrambled0* (sl-new (sl-scramble *sl-training*)))
(define *sl-scrambled1* (sl-step *sl-scrambled0* *sl-budget*))
(define *sl-scrambled2* (sl-step *sl-scrambled1* *sl-budget*))
(print "SYMBOLIC scrambled " (sl-coverage *sl-scrambled2* *sl-heldout*) "\n")
(sl-check (= (dlm-nth (sl-coverage *sl-scrambled2* *sl-heldout*) 1) 0)
          "scrambled observations do not reproduce transfer")
(sl-check (= (dlm-length (dlm-nth (dlm-nth *sl-round2* 5) 4)) 10)
          "argument-role categories are induced from observation signatures")
(sl-check (dlm-assoc 'q (dlm-nth (dlm-nth *sl-round2* 5) 3))
          "predicate index retains source observation records")
(sl-check (= (dlm-length (dlm-nth (car (dlm-nth *sl-round1* 4)) 4)) 60)
          "failed and successful candidate verdicts are retained")
