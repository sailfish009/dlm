;;; oracle.l — independent proof-count probe over all test-entity pairs.
(define *ents* (list 'x0 'x1 'x2 'x3 'x4 'x5))
(define-function pairs (xs out)
  (if (not xs) out
      (list-do y (cdr xs)
        (set out (l-append out (list (l-atom *schema-p* (list (car xs) y))))))
      (pairs (cdr xs) out)))
(define *all-goals* (pairs *ents* ()))
(define *oracle* (c3 test-facts learned *all-goals* 0 0))
(define *oracle-neg* (p3 test-facts learned (l-atom *schema-p* (list 'x5 'x0))))
(print "ORACLE PROVED " (car (cdr *oracle*)) "/" (car *oracle*) " NEG " *oracle-neg* " (want 0)\n")
(print "done-oracle\n")
