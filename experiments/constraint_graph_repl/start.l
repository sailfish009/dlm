;;; Hard/soft graph constraints: hard rejects, soft is report-only.
(define x (list 'var 'x)) (define z (list 'var 'z))
(define head (l-atom 'R (list x z)))
(define seed (l-atom 'P (list x z)))
(define module
  (ml-module "constraint-graph"
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
(define c1 (mc-constraint "c-node" 'hard (list 'node-exists "p") 'graph 'active (list "test")))
(define c2 (mc-constraint "c-kind" 'hard (list 'node-kind "t" 'task) 'node 'active (list "test")))
(define c3 (mc-constraint "c-not" 'hard (list 'not (list 'node-exists "missing")) 'graph 'active (list "test")))
(define c4 (mc-constraint "c-acyclic" 'hard (list 'acyclic) 'graph 'active (list "test")))
(define c5 (mc-constraint "c-soft" 'soft (list 'node-exists "optional") 'graph 'active (list "test")))
(define cg (mg-attach g (list c1 c2 c3 c4 c5)))
(print "HARD " (mg-check-cgraph cg) "\n")
(print "REPORT " (mg-constraint-report cg) "\n")
(define bad (mg-attach g (list (mc-constraint "c-missing" 'hard (list 'node-exists "missing") 'graph 'active (list "test")))))
(print "BAD " (mg-check-cgraph bad) "\n")
(define badx (mg-attach g (list (mc-constraint "c-expr" 'hard (list 'unknown-op "x") 'graph 'active (list "test")))))
(print "BADEXPR " (mg-check-cgraph badx) "\n")
(print "done-constraints\n")
