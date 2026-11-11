;;; Explicit graph IR: verify, topo-sort, lower back, compare with linear module.
(define x (list 'var 'x)) (define z (list 'var 'z))
(define head (l-atom 'R (list x z)))
(define seed (l-atom 'P (list x z)))
(define module
  (ml-module "graph-linear"
    (list
      (ml-op 'fragment (list "fseed" head (list seed)))
      (ml-op 'template (list "seed" head (list seed)))
      (ml-op 'program (list "p" (list "seed")))
      (ml-op 'task (list "t"
        (list (l-atom 'parent (list "a" "b")))
        (list (l-atom 'ancestor (list "a" "b")))
        (list (l-atom 'ancestor (list "b" "a")))
        (list (list 'R 'ancestor) (list 'P 'parent)))))))
(define g (mg-from-module module))
(print "GRAPH check=" (mg-check g) " topo=" (mg-topo g) " values=" (l-len (mg-values g)) " nodes=" (l-len (mg-nodes g)) " edges=" (l-len (mg-edges g)) "\n")
(define rebuilt (mg-to-module "graph-rebuilt" g))
(define r1 (ml-run module))
(define r2 (ml-run rebuilt))
(print "LINEAR run=" (l-nth r1 12) " rebuilt=" (l-nth r2 12) " same=" (if (equal (l-nth r1 12) (l-nth r2 12)) "yes" "no") "\n")
(define dup (mg-graph (mg-values g) (cons (car (mg-nodes g)) (mg-nodes g)) (mg-edges g)))
(print "DUP " (mg-check dup) "\n")
(define badedge (mg-graph (mg-values g) (mg-nodes g)
  (cons (mg-edge "v0" "p" 0) (mg-edges g))))
(print "BADEDGE " (mg-check badedge) "\n")
(print "done-graph-ir\n")
