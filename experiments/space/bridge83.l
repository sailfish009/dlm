;;; Existing REPL learning step, now with optional accumulated spatial routing.
(dlm 'demo)
(dlm 'ground 'on)
(times-do 3
  (dump (dlm 'step)) (print "\n")
  (dump (dlm 'ground)) (print "\n"))
(dump (dlm 'query 'demo-a '(atom "c77-0" (a c)))) (print "\n")
