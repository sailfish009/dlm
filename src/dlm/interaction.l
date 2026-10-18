;;; -*- mode: lisp; coding: us-ascii -*-
;;; Tiny expert-iteration controller. No arbitrary eval or assertion capability.
;;; Model: (decider WEIGHTS EXPERIENCE UPDATES).
(define *interaction-actions* '(head tail abstain))
(define-function interaction-model () (list 'decider () () 0))

;;; Each selected ID executes an actual Maru primitive. Goal check is exact and
;;; independent of the scorer. No action can return the goal argument directly.
(define-function interaction-execute (state goal action)
  (if (= action 'abstain) (list 'failed 'abstained)
    (if (not (pair? state)) (list 'failed 'empty)
      (if (= action 'head)
          (let ((value (car state)))
            (list (if (equal value goal) 'success 'failed) value))
        (if (= action 'tail)
            (if (cdr state) (list 'running (cdr state)) (list 'failed 'empty))
          (list 'failed 'forbidden-action))))))

;;; Deliberately small observations: no position-of-goal or successful-action
;;; label in the features. Head/goal equality is an explicit task affordance.
(define-function interaction-features (state goal)
  (dlm-append '(bias)
    (dlm-append (if (and state (equal (car state) goal)) '(head-match) ())
                (if (and state (not (cdr state))) '(singleton) ()))))

(define-function interaction-weight (model action feature)
  (let ((entry (dlm-assoc (list action feature) (dlm-nth model 1))))
    (if entry (dlm-nth entry 1) 0)))

(define-function interaction-score (model state goal action)
  (let ((score 0))
    (list-do feature (interaction-features state goal)
      (set score (+ score (interaction-weight model action feature))))
    score))

(define-function interaction-choice (model state goal)
  (let ((best 'head) (score (interaction-score model state goal 'head)))
    (list-do action '(tail abstain)
      (let ((candidate (interaction-score model state goal action)))
        (if (> candidate score) (begin (set best action) (set score candidate)))))
    best))

;;; Bounded BFS discovers successful trajectories from execution, not handwritten
;;; head/tail labels. Search budget counts primitive calls, including failures.
;;; Result: (search STATUS TRACE CALLS).
(define-function interaction-search (state goal budget)
  (let ((agenda (list (list state ()))) (calls 0) (answer ()))
    (while (and agenda (not answer) (< calls budget))
      (let* ((node (car agenda)) (current (car node)) (trace (dlm-nth node 1)))
        (set agenda (cdr agenda))
        (list-do action *interaction-actions*
          (if (and (not answer) (< calls budget))
              (let* ((result (interaction-execute current goal action))
                     (path (dlm-append trace (list (list current action result)))))
                (set calls (+ calls 1))
                (if (= (car result) 'success) (set answer path)
                  (if (= (car result) 'running)
                      (set agenda (dlm-append agenda
                        (list (list (dlm-nth result 1) path)))))))))))
    (list 'search (if answer 'success (if agenda 'incomplete 'failed)) answer calls)))

(define-function interaction-adjust (weights key delta)
  (let ((entry (dlm-assoc key weights)) (rest ()))
    (list-do item weights
      (if (not (equal key (car item))) (set rest (cons item rest))))
    (cons (list key (+ (if entry (dlm-nth entry 1) 0) delta)) rest)))

;;; Pairwise margin update, integer arithmetic only. Successful trace comes from
;;; independent bounded search. Experience is explicit model data, not Ground.
(define-function interaction-contrast (model state goal positive negative)
  (let ((weights (dlm-nth model 1)) (updates (dlm-nth model 3))
        (gap (- (interaction-score model state goal positive)
                (interaction-score model state goal negative))))
    (if (and (not (= positive negative)) (< gap 1))
        (begin
          (list-do feature (interaction-features state goal)
            (set weights (interaction-adjust weights (list positive feature) 1))
            (set weights (interaction-adjust weights (list negative feature) -1)))
          (set updates (+ updates 1))))
    (list 'decider weights (dlm-nth model 2) updates)))

(define-function interaction-train (model state goal budget)
  (let ((search (interaction-search state goal budget)) (work model))
    (when (= (dlm-nth search 1) 'success)
      (list-do step (dlm-nth search 2)
        (list-do negative *interaction-actions*
          (set work (interaction-contrast work (car step) goal
                                          (dlm-nth step 1) negative)))))
    (list 'decider (dlm-nth work 1)
      (dlm-append (dlm-nth model 2) (list (list 'experience state goal search)))
      (dlm-nth work 3))))

(define-function interaction-remainder (n modulus)
  (- n (* (/ n modulus) modulus)))

;;; Result: (rollout STATUS TRACE CALLS). The state returned by Maru is the next
;;; input. Random is a seeded, nonlearned comparison; scrambled swaps two IDs.
(define-function interaction-rollout (model state goal budget mode seed)
  (let ((current state) (trace ()) (calls 0) (status 'running))
    (while (and (= status 'running) (< calls budget))
      (set seed (interaction-remainder (+ (* seed 25173) 13849) 65536))
      (let* ((chosen (if (= mode 'random)
                         (dlm-nth *interaction-actions* (interaction-remainder seed 3))
                       (interaction-choice model current goal)))
             (action (if (= mode 'scrambled)
                         (if (= chosen 'head) 'tail (if (= chosen 'tail) 'head chosen))
                       chosen))
             (result (interaction-execute current goal action)))
        (set trace (dlm-append trace (list (list current action result))))
        (set calls (+ calls 1))
        (set status (car result))
        (if (= status 'running) (set current (dlm-nth result 1)))))
    (list 'rollout (if (= status 'running) 'incomplete status) trace calls)))
