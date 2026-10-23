(times-do 256 (dlm 'search 'cache))
(dlm 'start 20)
(define first (dlm 'step))
(define second (dlm 'step))
(dump (list 'first first 'second second 'running *dlm-running*
 'saturated *dlm-saturated* 'events (dlm-length *dlm-events*))) (print "\n")
(dlm 'pause)
