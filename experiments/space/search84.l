;;; Original REPL learning path; optional controller, no neural components.
(dlm 'demo)
(dump (dlm 'search 'ucb)) (print "\n")
(set *dlm-pair-budget* 2)
(times-do 5
  (dump (dlm 'step)) (print "\n")
  (dump (dlm 'search)) (print "\n"))
(dump (dlm 'query 'demo-a '(atom "c77-0" (a c)))) (print "\n")
