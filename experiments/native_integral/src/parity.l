;;; parity.l — Maru ground-closure oracle for the native C kernel (icredit.c).
;;; Same explicit 6-atom theory as C PARITY2: facts {0,3}; rules 0->1,1->2,
;;; 3->4,4->5; goals {2,5}. Unbounded closure must derive 6 atoms, reach 2 goals.
;;; Atoms encoded as 'at' with string labels (Maru constants are strings/symbols).
(define pfacts (list (l-fact "p0" (l-atom 'at (list "0")))
                     (l-fact "p3" (l-atom 'at (list "3")))))
(define prules (list (l-rule (l-atom 'at (list "1")) (list (l-atom 'at (list "0"))))
                     (l-rule (l-atom 'at (list "2")) (list (l-atom 'at (list "1"))))
                     (l-rule (l-atom 'at (list "4")) (list (l-atom 'at (list "3"))))
                     (l-rule (l-atom 'at (list "5")) (list (l-atom 'at (list "4"))))))
(define ptable (p-close pfacts prules 20000))
(define derived (l-len ptable))
(define g2 (l-lookup (l-atom 'at (list "2")) ptable))
(define g5 (l-lookup (l-atom 'at (list "5")) ptable))
(define reached (+ (if g2 1 0) (if g5 1 0)))
(print "PARITY2 derived=" derived " reached=" reached "\n")
(if (and (= derived 6) (= reached 2))
    (print "MARU-PARITY-PASS\n")
    (print "MARU-PARITY-FAIL\n"))