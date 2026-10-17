;;; -*- mode: lisp; coding: us-ascii -*-
;;; Maru provides the REPL. These are model operations, not another evaluator.
(define *dlm-state* (dlm-new-state () ()))

(define-function dlm-status ()
  (list 'status (list 'round (dlm-nth *dlm-state* 2))
        (list 'episodes (dlm-length (dlm-nth *dlm-state* 3)))
        (list 'ground (dlm-length (dlm-nth *dlm-state* 4)))
        (list 'experience (dlm-length (dlm-nth *dlm-state* 5)))))

(define-function dlm-ask (target)
  (let ((answer ()))
    (list-do e (dlm-nth *dlm-state* 3)
      (let ((p (dlm-prove (dlm-nth e 2) (dlm-theory *dlm-state*) target)))
        (if (and p (dlm-verify-proof p (dlm-nth e 2) (dlm-theory *dlm-state*)))
            (set answer (dlm-append answer (list (list 'support (dlm-nth e 1) p)))))))
    (if answer (list 'answer 'proved answer) (list 'answer 'unknown ()))))

(define-function dlm-observe (episodes)
  (set *dlm-state* (dlm-commit *dlm-state*
                             (dlm-observe-transition *dlm-state* episodes)))
  (dlm-status))

(define-function dlm-learn (budget)
  (set *dlm-state* (dlm-commit *dlm-state*
                             (dlm-learning-transition *dlm-state* budget)))
  (dlm-status))
