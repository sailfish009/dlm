(require "experiments/integration94/driver.l")
(define input94 (read *standard-input*))
(assert (= (read *standard-input*) +end+) "trailing integration94 input")
(i94-run input94)
