(require "experiments/eml93/driver.l")
(define data93 (read *standard-input*))
(assert (= (read *standard-input*) +end+) "trailing EML93 input")
(e93-input-run data93)
