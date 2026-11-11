;;; repl.l — tiny REPL helpers for the fresh deductive experiment.
(define *deduce-active* ())
(define-function d-repl-status ()
  (list 'deduce 'active *deduce-active*))
