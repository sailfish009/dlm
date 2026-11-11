;;; CSE merges duplicate fragment/template nodes and rewrites references.
(define x (list 'var 'x)) (define z (list 'var 'z))
(define head (l-atom 'R (list x z)))
(define seed (l-atom 'P (list x z)))
(define module
  (ml-module "cse-graph"
    (list
      (ml-op 'fragment (list "f1" head (list seed)))
      (ml-op 'fragment (list "f2" head (list seed)))
      (ml-op 'template (list "s1" head (list seed)))
      (ml-op 'template (list "s2" head (list seed)))
      (ml-op 'program (list "p" (list "s1" "s2")))
      (ml-op 'task (list "t"
        (list (l-atom 'parent (list "a" "b")))
        (list (l-atom 'ancestor (list "a" "b")))
        (list (l-atom 'ancestor (list "b" "a")))
        (list (list 'R 'ancestor) (list 'P 'parent)))))))
(define g (mg-from-module module))
(define c (mg-cse g))
(print "BEFORE nodes=" (l-len (mg-nodes g)) " values=" (l-len (mg-values g)) "\n")
(print "AFTER nodes=" (l-len (mg-nodes c)) " values=" (l-len (mg-values c)) " check=" (mg-check c) "\n")
(print "OPS " (ml-ops (mg-to-module "cse" c)) "\n")
(define r1 (ml-run (mg-to-module "base" g)))
(define r2 (ml-run (mg-to-module "cse" c)))
(print "BASE RUN " (l-nth r1 12) "\n")
(print "CSE RUN " (l-nth r2 12) "\n")
(print "SAME " (if (equal (l-nth r1 12) (l-nth r2 12)) "yes" "no") "\n")
(print "done-cse\n")
