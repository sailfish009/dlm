;;; -*- mode: lisp; coding: us-ascii -*-
;;; State: (symbolic-state VERSION EPISODES THEORY EVENTS GRAPH).
;;; Input episodes are observations, never generated closure labels.
;;; Role categories are structural (predicate, argument position), not world types.
(define-function sl-role-categories (episodes)
  (let ((roles ()))
    (list-do e episodes
      (list-do partition '(2 3)
        (list-do a (dlm-nth e partition)
          (let ((position 0))
            (list-do term (dlm-args a)
              (let* ((key (list (dlm-pred a) position))
                     (prior (dlm-assoc key roles))
                     (members (dlm-add (dlm-nth prior 1) term)))
                (set roles (cons (list key members)
                  (dlm-difference roles (if prior (list prior) ())))))
              (set position (+ position 1)))))))
    roles))

(define-function sl-graph (episodes)
  (let ((nodes ()) (claims ()))
    (list-do e episodes
      (list-do partition '(2 3 4)
        (list-do a (dlm-nth e partition)
          (set nodes (dlm-add nodes (list 'predicate (dlm-pred a) (dlm-length (dlm-args a)))))
          (list-do term (dlm-args a)
            (set nodes (dlm-add nodes (list 'entity term))))
          (set claims (dlm-add claims
            (list 'observation (dlm-nth e 1) partition a))))))
    (let ((index ()))
      (list-do claim claims
        (let* ((pred (dlm-pred (dlm-nth claim 3)))
               (prior (dlm-assoc pred index)))
          (set index (cons (list pred (dlm-add (dlm-nth prior 1) claim))
                            (dlm-difference index (if prior (list prior) ()))))))
      (list 'graph nodes claims index (sl-role-categories episodes)))))

(define-function sl-new (episodes)
  (list 'symbolic-state 73 episodes () () (sl-graph episodes)))

(define-function sl-candidates (episodes)
  (let ((facts ()) (goals ()))
    (list-do e episodes
      (set facts (dlm-union facts (dlm-nth e 2)))
      (set goals (dlm-union goals (dlm-nth e 3))))
    (dlm-execute-programs facts goals)))

;;; Positive matching is inductive support, not universal proof of a rule.
;;; Recheck every retained rule against all explicit counterobservations.
(define-function sl-consistent? (episodes theory)
  (let ((ok true))
    (list-do e episodes
      (if (dlm-intersection (dlm-nth e 4) (dlm-closure (dlm-nth e 2) theory))
          (set ok false)))
    ok))

;;; Legal action alternatives are executed through Maru's finite choice engine.
(define-function sl-actions (episodes)
  (let* ((pool (sl-candidates episodes))
         (search (symbolic-solutions (list (list 'candidate pool)) ()
                                     (+ 1 (dlm-length pool))))
         (actions ()))
    (assert (= (dlm-nth search 1) 'complete) "candidate enumeration incomplete")
    (list-do solution (dlm-nth search 2)
      (set actions (dlm-append actions (list (car (csp-domain solution 'candidate))))))
    actions))

(define-function sl-search (episodes theory actions budget)
  (let ((chosen ()) (best ()) (checks 0) (assessments ()))
    (list-do rule actions
      (when (and (< checks budget) (not (dlm-member? rule theory)))
        (let ((verdict (dlm-evaluate rule episodes theory)))
          (set checks (+ checks 1))
          (set assessments (dlm-append assessments (list (list rule verdict))))
          (when (and (dlm-nth verdict 6)
                     (or (not best) (> (dlm-nth verdict 5) (dlm-nth best 5))))
            (set chosen rule)
            (set best verdict)))))
    (list (list 'learning-result (if chosen (dlm-append theory (list chosen)) theory)
                chosen best checks) assessments)))

(define-function sl-step (state budget)
  (let* ((episodes (dlm-nth state 2)) (theory (dlm-nth state 3))
         (search (sl-search episodes theory (sl-actions episodes) budget))
         (result (car search))
         (next (dlm-nth result 1))
         (event (list 'step budget theory result (dlm-nth search 1))))
    (assert (sl-consistent? episodes next) "counterevidence gate")
    (list 'symbolic-state 73 episodes next
          (dlm-append (dlm-nth state 4) (list event)) (dlm-nth state 5))))

;;; Conservative batch retraction: a conflicting theory is reset, not declared true.
;;; Old evidence and history remain in the rebase event for replay.
(define-function sl-observe (state episode)
  (let* ((episodes (dlm-append (dlm-nth state 2) (list episode)))
         (theory (dlm-nth state 3))
         (next (if (sl-consistent? episodes theory) theory ())))
    (list 'symbolic-state 73 episodes next
      (dlm-append (dlm-nth state 4)
        (list (list 'observe episode theory next))) (sl-graph episodes))))

;;; Replay from initial evidence, with the same candidate grammar and evaluator.
;;; No saved derived facts are admitted as observations.
(define-function sl-replay (initial events)
  (let ((state (sl-new initial)))
    (list-do event events
      (let ((next (if (= (car event) 'step)
                      (sl-step state (dlm-nth event 1))
                    (if (= (car event) 'observe)
                        (sl-observe state (dlm-nth event 1))
                      (error "unknown symbolic event")))))
        (assert (equal event (dlm-nth (dlm-nth next 4) (- (dlm-length (dlm-nth next 4)) 1))) "event replay mismatch")
        (set state next)))
    state))

(define-function sl-coverage (state episodes)
  (let ((proved 0) (total 0) (bad 0))
    (list-do e episodes
      (let* ((facts (dlm-nth e 2)) (rules (dlm-nth state 3))
             (closure (dlm-closure facts rules)))
        (list-do goal (dlm-nth e 3)
          (set total (+ total 1))
          (when (dlm-member? goal closure)
            (let ((proof (dlm-prove facts rules goal)))
              (assert (and proof (dlm-verify-proof proof facts rules)) "independent proof check")
              (set proved (+ proved 1)))))
        (set bad (+ bad (dlm-length (dlm-intersection (dlm-nth e 4) closure))))))
    (list 'coverage proved total bad)))
