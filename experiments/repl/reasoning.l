;;; -*- mode: lisp; coding: us-ascii -*-
(print "DLM 0.0079 legacy nondeterministic reasoning in the original Maru REPL.\n")
(dlm 'nd-help)
(dump (dlm 'nd-open *dlm-session-path*)) (print "\n")
(if *r78-path*
    (let ((m (dlm-nth *r78-state* 2)))
      (if (and m (n78-ready? m) (not (dlm-nth m 4))) (dlm 'nd-start 1000)
        (print "No ready reasoning job. Submit (dlm 'think 'PROBLEM), then (dlm 'nd-start 1000).\n"))))
