(define *proof-hash* (read *standard-input*))
(assert (= (read *standard-input*) +end+) "trailing proof data")
(assert (sq-store? *proof-hash*) "invalid proof store evidence")
(print (dlm-nth *proof-hash* 6) "\n")
