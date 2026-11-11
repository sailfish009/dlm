;;; Dead-node elimination on an explicit graph.
(define x (list 'var 'x)) (define z (list 'var 'z))
(define head (l-atom 'R (list x z)))
(define seed (l-atom 'P (list x z)))
(define module
  (ml-module "dce-graph"
    (list
      (ml-op 'fragment (list "unused" head (list seed)))
      (ml-op 'fragment (list "fseed" head (list seed)))
      (ml-op 'template (list "seed" head (list seed)))
      (ml-op 'program (list "p" (list "seed")))
      (ml-op 'task (list "t"
        (list (l-atom 'parent (list "a" "b")))
        (list (l-atom 'ancestor (list "a" "b")))
        (list (l-atom 'ancestor (list "b" "a")))
        (list (list 'R 'ancestor) (list 'P 'parent)))))))
(define g (mg-from-module module))
(define d (mg-dce g (list "p" "t")))
(print "BEFORE nodes=" (l-len (mg-nodes g)) " edges=" (l-len (mg-edges g)) "\n")
(print "AFTER nodes=" (l-len (mg-nodes d)) " edges=" (l-len (mg-edges d)) " check=" (mg-check d) " topo=" (mg-topo d) "\n")
(define base (mg-to-module "base" g))
(define dce (mg-to-module "dce" d))
(define r1 (ml-run base))
(define r2 (ml-run dce))
(print "BASE RUN " (l-nth r1 12) "\n")
(print "DCE RUN " (l-nth r2 12) "\n")
(print "SAME " (if (equal (l-nth r1 12) (l-nth r2 12)) "yes" "no") "\n")
(print "done-dce\n")
