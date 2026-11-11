;;; Advisory NumPy embedding attached to the explicit graph.
(define x (list 'var 'x)) (define z (list 'var 'z))
(define head (l-atom 'R (list x z)))
(define seed (l-atom 'P (list x z)))
(define module
  (ml-module "embed-graph"
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
(print "GRAPH " (mg-check g) "\n")
(print "EMBED " (mg-check-embeddings g *graph-embeddings*) "\n")
(print "EMBEDDINGS " (l-len *graph-embeddings*) "\n")
(print "RANK " (mg-rank-query g *graph-embeddings* "p") "\n")
(define egbad (mg-embedding "p" 4 (list 1 2) "hbad"))
(print "BADDIM " (mg-check-embeddings g (list egbad)) "\n")
(define egbadnode (mg-embedding "missing" 8 (mg-embedding-vec (mg-embedding-node "p" *graph-embeddings*)) "hbad"))
(print "BADNODE " (mg-check-embeddings g (list egbadnode)) "\n")
(define r1 (ml-run module))
(print "RUN " (l-nth r1 12) "\n")
(print "done-embed\n")
