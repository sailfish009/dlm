;;; fxtest.l — exact Q16 kernel checks.
(define-function fx-check (name got want)
  (print (if (equal got want) "PASS " "FAIL ") name " got=" got " want=" want "\n"))

(fx-check "mul" (fx-mul 98304 147456) 221184)
(fx-check "div" (fx-div 98304 32768) 196608)
(fx-check "sqrt4" (fx-sqrt (* 4 65536)) 131072)
(fx-check "sqrt2" (fx-sqrt (* 2 65536)) 92681)
(fx-check "exp-1" (fx-exp (- 0 65536)) 24109)
(fx-check "softmax-uniform" (v-softmax (list 0 0)) (list 32768 32768))
(fx-check "softmax-ln2" (v-softmax (list 0 45426)) (list 21846 43689))
(print "FX-TEST-DONE\n")
