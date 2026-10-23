;;; Explicit observations and genuine generated choose branches. No seed axioms.
(dlm 'demo)
(dlm 'search 'nd-ucb)
(set *dlm-pair-budget* 4)
(times-do 4
  (dump (dlm 'step)) (print "\n")
  (dump (dlm 'search)) (print "\n"))
(dump (dlm 'query 'demo-a '(atom "c77-2" (a e)))) (print "\n")
