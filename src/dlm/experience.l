;;; -*- mode: lisp; coding: us-ascii -*-
;;; State: (model VERSION ROUND EPISODES GROUND EXPERIENCE HISTORY).
;;; Pure list values; host-side mutation is outside this trust boundary.

(define-function dlm-new-state (episodes ground)
  (list 'model "0.0.75" 0 episodes ground () ()))
(define-function dlm-theory (state)
  (dlm-append (dlm-nth state 4) (dlm-nth state 5)))

(define-function dlm-conflicts? (episodes theory)
  (let ((bad false))
    (list-do e episodes
      (if (dlm-intersection (dlm-nth e 4)
                            (dlm-closure (dlm-nth e 2) theory))
          (set bad true)))
    bad))

(define-function dlm-state-candidates (episodes)
  (let ((pool ()))
    (list-do e episodes
      (set pool (dlm-union pool
        (dlm-execute-programs (dlm-nth e 2) (dlm-nth e 3)))))
    pool))

;;; Transition: (transition BEFORE AFTER OUTCOME).
;;; Ground contradictions abstain; learned rules can be retracted.
(define-function dlm-step (state budget)
  (let ((episodes (dlm-nth state 3)) (ground (dlm-nth state 4))
        (kept ()) (history (dlm-nth state 6))
        (round (+ 1 (dlm-nth state 2))))
    (if (dlm-conflicts? episodes ground)
        (list 'transition state state 'ground-conflict)
      (begin
        (list-do r (dlm-nth state 5)
          (if (dlm-conflicts? episodes (dlm-append ground (dlm-append kept (list r))))
              (set history (dlm-append history (list (list 'retracted round r))))
            (set kept (dlm-append kept (list r)))))
        (let* ((result (dlm-learn-round episodes (dlm-append ground kept)
                                       (dlm-state-candidates episodes) budget))
               (chosen (dlm-nth result 2)))
          (if chosen
              (begin
                (set kept (dlm-append kept (list chosen)))
                (set history (dlm-append history (list (list 'admitted round chosen))))))
          (list 'transition state
                (list 'model "0.0.75" round episodes ground kept history)
                (if chosen 'learned 'no-progress)))))))

(define-function dlm-learning-transition (state budget)
  (list 'proposal (list 'step budget) (dlm-step state budget)))

(define-function dlm-observe-transition (state episodes)
  (let ((ground (dlm-nth state 4)))
    (if (dlm-conflicts? episodes ground)
        (list 'proposal (list 'observe episodes)
              (list 'transition state state 'ground-conflict))
      (let* ((work (list 'model "0.0.75" (dlm-nth state 2) episodes ground
                         (dlm-nth state 5) (dlm-nth state 6)))
             (revised (dlm-nth (dlm-step work 0) 2)))
        (list 'proposal (list 'observe episodes)
          (list 'transition state
            (list 'model "0.0.75" (dlm-nth state 2) episodes ground
                  (dlm-nth revised 5) (dlm-nth revised 6))
            'observed))))))

;;; Recompute rather than trust a supplied AFTER value.
(define-function dlm-commit (state proposal)
  (let* ((action (dlm-nth proposal 1))
         (expected
           (if (= (car action) 'step)
               (dlm-learning-transition state (dlm-nth action 1))
             (if (= (car action) 'observe)
                 (dlm-observe-transition state (dlm-nth action 1))
               (error "DLM: unknown action")))))
    (if (not (equal expected proposal)) (error "DLM: forged or stale transition"))
    (dlm-nth (dlm-nth expected 2) 2)))
