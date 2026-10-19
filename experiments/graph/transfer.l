;;; -*- mode: lisp; coding: us-ascii -*-
(require "experiments/symbolic/data.l")
(define *gr-learner0* (sl-new *sl-training*))
(define *gr-learning-budget* (dlm-length (sl-candidates *sl-training*)))
(define *gr-learner1* (sl-step *gr-learner0* *gr-learning-budget*))
(define *gr-learner2* (sl-step *gr-learner1* *gr-learning-budget*))
(define *gr-transfer-proved* 0)
(define *gr-transfer-false* 0)
(list-do episode *sl-heldout*
  (let ((graph (gr-from-episode episode (dlm-nth *gr-learner2* 3) 20)))
    (list-do target (dlm-nth episode 3)
      (when (= (dlm-nth (gr-query graph target) 1) 'entailed)
        (set *gr-transfer-proved* (+ *gr-transfer-proved* 1))))
    (set *gr-transfer-false* (+ *gr-transfer-false*
      (dlm-length (dlm-intersection (dlm-nth episode 4) (gr-closure graph)))))))
(gr-check (= *gr-transfer-proved* 14) "learned rules execute in graph engine on heldout structures")
(gr-check (= *gr-transfer-false* 0) "graph transfer derives no heldout explicit counterobservations")
(print "GRAPH learned-transfer " (list 'proved *gr-transfer-proved* 'false *gr-transfer-false*) "\n")
