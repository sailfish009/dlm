;;; -*- mode: lisp; coding: us-ascii -*-
(print "DLM 0.0079: connected computational units in the original Maru REPL.\n")
(space 'help)
(dump (space 'open *dlm-session-path*)) (print "\n")
(if *s79-path*
    (if (or (dlm-nth *s79-space* 5) (dlm-nth *s79-space* 6)) (space 'start 1000)
      (print "Space is empty or quiescent. Submit prove/study/program/interpolate/beth, then start.\n")))
