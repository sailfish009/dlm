;;; main.l — run all 8 reference sentences in Maru.
(define-function tt-print-cases (ids ens exps n)
  (if ids
      (let ((out (tt-translate (car ids))) (exp (car exps)))
        (print "CASE " n "\n")
        (print "SRC " (car ens) "\n")
        (print "MARU " out "\n")
        (print "REF " exp "\n")
        (print "MATCH " (if (equal out exp) 1 0) "\n")
        (tt-print-cases (cdr ids) (cdr ens) (cdr exps) (+ n 1)))
      ()))
(tt-print-cases case-ids case-en case-expected 0)
