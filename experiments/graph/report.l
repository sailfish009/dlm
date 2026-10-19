;;; -*- mode: lisp; coding: us-ascii -*-
(define *graph-report-state* (gr-verify-state (read *standard-input*)))
(print (list 'graph-report
  (list 'status (dlm-nth *graph-report-state* 9))
  (list 'active-claims (dlm-length (dlm-nth *graph-report-state* 5)))
  (list 'catalog-nodes (dlm-length (dlm-nth *graph-report-state* 4)))
  (list 'supports (dlm-length (dlm-nth *graph-report-state* 6)))
  (list 'events (dlm-length (dlm-nth *graph-report-state* 11)))
  (list 'conflict (gr-conflict? *graph-report-state*))
  (dlm-nth *graph-report-state* 10)) "\n")
