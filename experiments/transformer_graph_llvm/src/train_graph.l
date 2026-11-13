;;; train_graph.l — explicit forward/backward/update graph (structural probe).
(define tx (mg-value "tx" "tokens" "tinput"))
(define ty (mg-value "ty" "labels" "tinput"))
(define tf (mg-value "tf" "logits" "forward"))
(define tl (mg-value "tl" "loss" "loss"))
(define tg (mg-value "tg" "grads" "backward"))
(define tu (mg-value "tu" "params" "adam"))
(define g
  (mg-graph
    (list tx ty tf tl tg tu)
    (list
      (mg-node "tinput" "input" () (list "tx" "ty") (list))
      (mg-node "forward" "transformer" (list "tx") (list "tf") (list))
      (mg-node "loss" "bce" (list "tf" "ty") (list "tl") (list))
      (mg-node "backward" "autodiff" (list "tf" "tl") (list "tg") (list))
      (mg-node "adam" "update" (list "tg") (list "tu") (list)))
    (list (mg-edge "tx" "forward" 0) (mg-edge "tf" "loss" 0) (mg-edge "ty" "loss" 1)
          (mg-edge "tf" "backward" 0) (mg-edge "tl" "backward" 1)
          (mg-edge "tg" "adam" 0))))
(print "TRAIN-GRAPH " (mg-check g) " NODES " (l-len (mg-nodes g)) " EDGES " (l-len (mg-edges g)) "\n")
(print "TRAIN-TOPO " (mg-topo g) "\n")
(print "done-train-graph\n")
