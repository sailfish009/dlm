(dlm 'open "/tmp/review84-capacity.sexp")
(dump (list 'restored-saturated *dlm-saturated* 'next (dlm 'step))) (print "\n")
(dlm 'close)
