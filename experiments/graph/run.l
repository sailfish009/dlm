;;; -*- mode: lisp; coding: us-ascii -*-
(define *gr-x* (dlm-var 'x))
(define *gr-y* (dlm-var 'y))
(define *gr-z* (dlm-var 'z))
(define *gr-edge-rule*
  (dlm-rule (dlm-atom 'reach *gr-x* *gr-y*) (dlm-atom 'edge *gr-x* *gr-y*)))
(define *gr-chain-rule*
  (dlm-rule (dlm-atom 'reach *gr-x* *gr-z*)
    (dlm-atom 'reach *gr-x* *gr-y*) (dlm-atom 'edge *gr-y* *gr-z*)))
(define *gr-episode*
  (dlm-episode 'diamond
    (list (dlm-atom 'edge 'a 'b) (dlm-atom 'edge 'b 'd)
          (dlm-atom 'edge 'a 'c) (dlm-atom 'edge 'c 'd)
          (dlm-atom 'likes 'a 'b) (dlm-atom 'likes 'b 'd)) () ()))
(define *gr-demo* (gr-from-episode *gr-episode* (list *gr-edge-rule* *gr-chain-rule*) 20))
(print "GRAPH query " (gr-query *gr-demo* (dlm-atom 'reach 'a 'd)) "\n")
(print "GRAPH alternative-supports " (dlm-length (gr-supports-for *gr-demo* (dlm-atom 'reach 'a 'd))) "\n")
(print "GRAPH paths " (gr-paths *gr-demo* 'a 'd '(edge) 4 100 10) "\n")
(print "GRAPH metrics " (dlm-nth *gr-demo* 10) "\n")
