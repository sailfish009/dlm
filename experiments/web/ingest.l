;;; -*- mode: lisp; coding: us-ascii -*-
(define *web-input* (read *standard-input*))
(assert (and (= (car *web-input*) 'web-input) (= (dlm-nth *web-input* 1) 74)
             (= (dlm-length *web-input*) 4)) "invalid web input")
(define *web-before* (if (dlm-nth *web-input* 2)
  (web-verify-state (dlm-nth *web-input* 2)) (web-new)))
(define *web-after* (web-ingest *web-before* (dlm-nth *web-input* 3)))
(print *web-after* "\n")
