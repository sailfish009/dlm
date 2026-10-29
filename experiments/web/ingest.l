;;; -*- mode: lisp; coding: us-ascii -*-
(define *web-input* (read *standard-input*))
(assert (= (read *standard-input*) +end+) "trailing web input")
(assert (and (web-shape? *web-input* 4) (= (car *web-input*) 'web-input)
             (= (dlm-nth *web-input* 1) 74)) "invalid web input")
(define *web-before* (if (dlm-nth *web-input* 2)
  (web-verify-state (dlm-nth *web-input* 2)) (web-new)))
(define *web-after* (web-ingest *web-before* (dlm-nth *web-input* 3)))
(print *web-after* "\n")
