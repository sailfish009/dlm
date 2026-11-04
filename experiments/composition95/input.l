(require "experiments/composition95/driver.l")
(define input95 (read *standard-input*))
(assert (= (read *standard-input*) +end+) "trailing composition95 input")
(i95-run input95)
