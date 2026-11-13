;;; graph_control.l — invalid/cyclic graph controls.
(define v1 (mg-value "v1" "t" "n1"))
(define bad (mg-graph
  (list v1)
  (list (mg-node "n1" "input" () (list "v1") (list)))
  (list (mg-edge "v1" "missing" 0))))
(define a (mg-value "a" "t" "na"))
(define b (mg-value "b" "t" "nb"))
(define cyc (mg-graph
  (list a b)
  (list (mg-node "na" "x" (list "b") (list "a") (list))
        (mg-node "nb" "x" (list "a") (list "b") (list)))
  (list (mg-edge "a" "na" 0) (mg-edge "b" "nb" 0))))
(print "BAD-EDGE " (mg-check bad) "\n")
(print "CYCLE " (mg-topo cyc) "\n")
(print "done-graph-control\n")
