;;; -*- mode: lisp; coding: us-ascii -*-
(print "DLM 0.0079 legacy relation learner in the existing Maru REPL. No training labels or domain axioms.\n")
(dlm 'help)
(define *d77-open-result* (dlm 'open *dlm-session-path*))
(dump *d77-open-result*) (print "\n")
(if *dlm-store*
    (begin
      (if *dlm-demo-mode*
          (if (not (a77-episodes *dlm-model*)) (dlm 'demo)
            (print "Demo not injected: existing observations are preserved.\n")))
      (dlm 'start 1000)))
