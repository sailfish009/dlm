;;; -*- mode: lisp; coding: us-ascii -*-
;;; Explicit finite-domain nondeterminism; no implicit evaluator continuations.
(define-function symbolic-nth (xs n)
  (if (= n 0) (car xs) (symbolic-nth (cdr xs) (- n 1))))

(define-function symbolic-length (xs)
  (if xs (+ 1 (symbolic-length (cdr xs))) 0))

(define-function symbolic-append (xs ys)
  (if xs (cons (car xs) (symbolic-append (cdr xs) ys)) ys))

(define-function symbolic-member? (x xs)
  (and xs (or (equal x (car xs)) (symbolic-member? x (cdr xs)))))

(define-function symbolic-add (xs x)
  (if (symbolic-member? x xs) xs (symbolic-append xs (list x))))

(define-function symbolic-union (xs ys)
  (if ys (symbolic-union (symbolic-add xs (car ys)) (cdr ys)) xs))

(define-function symbolic-intersection (xs ys)
  (if xs
      (if (symbolic-member? (car xs) ys)
          (cons (car xs) (symbolic-intersection (cdr xs) ys))
        (symbolic-intersection (cdr xs) ys))
    ()))

(define-function symbolic-difference (xs ys)
  (if xs
      (if (symbolic-member? (car xs) ys)
          (symbolic-difference (cdr xs) ys)
        (cons (car xs) (symbolic-difference (cdr xs) ys)))
    ()))

(define-function symbolic-assoc (key xs)
  (if xs
      (if (equal key (car (car xs))) (car xs)
        (symbolic-assoc key (cdr xs)))
    ()))

;;; -*- mode: lisp; coding: us-ascii -*-
;;; Finite domains: ((NAME (VALUE ...)) ...).
;;; Constraint: (neq LEFT RIGHT), or (table LEFT RIGHT ((VALUE VALUE) ...)).
;;; No external Screamer code/dependency. Branch domains are immutable lists.
(define-function csp-domain (domains name)
  (symbolic-nth (symbolic-assoc name domains) 1))

(define-function csp-relation? (constraint left right)
  (if (= (car constraint) 'neq) (not (equal left right))
    (if (= (car constraint) 'table)
        (symbolic-member? (list left right) (symbolic-nth constraint 3))
      (error "CSP: unknown relation"))))

;;; Arc support for one value. Return (SUPPORTED RELATION-CHECKS).
(define-function csp-supported (name value domains constraints)
  (let ((valid true) (checks 0))
    (list-do c constraints
      (let ((left (symbolic-nth c 1)) (right (symbolic-nth c 2)))
        (when (or (equal name left) (equal name right))
          (let ((supported false)
                (other (if (equal name left) right left)))
            (list-do v (csp-domain domains other)
              (set checks (+ checks 1))
              (if (and (or (not (equal left right)) (equal value v))
                       (if (equal name left) (csp-relation? c value v)
                         (csp-relation? c v value)))
                  (set supported true)))
            (if (not supported) (set valid false))))))
    (list valid checks)))

(define-function csp-empty? (domains)
  (and domains (or (not (symbolic-nth (car domains) 1)) (csp-empty? (cdr domains)))))

;;; Arc-consistency fixpoint. No assertion of a solution from local consistency.
;;; Result: (DOMAINS CHECKS REMOVED).
(define-function csp-propagate (domains constraints)
  (let ((current domains) (changed true) (checks 0) (removed 0))
    (while (and changed (not (csp-empty? current)))
      (let ((next ()))
        (list-do entry current
          (let ((kept ()))
            (list-do value (symbolic-nth entry 1)
              (let ((support (csp-supported (car entry) value current constraints)))
                (set checks (+ checks (symbolic-nth support 1)))
                (if (car support) (set kept (symbolic-append kept (list value)))
                  (set removed (+ removed 1)))))
            (set next (symbolic-append next (list (list (car entry) kept))))))
        (set changed (not (equal next current)))
        (set current next)))
    (list current checks removed)))

(define-function csp-variable (domains mrv)
  (let ((best ()) (size 0))
    (list-do entry domains
      (let ((n (symbolic-length (symbolic-nth entry 1))))
        (when (> n 1)
          (if (or (not best) (and mrv (< n size)))
              (begin (set best (car entry)) (set size n))))))
    best))

(define-function csp-bind (domains name value)
  (if domains
      (cons (if (equal name (car (car domains))) (list name (list value)) (car domains))
            (csp-bind (cdr domains) name value))
    ()))

(define-function csp-valid? (domains constraints)
  (let ((valid true))
    (list-do c constraints
      (if (not (csp-relation? c (car (csp-domain domains (symbolic-nth c 1)))
                              (car (csp-domain domains (symbolic-nth c 2)))))
          (set valid false)))
    valid))

;;; Enumerate ALL solutions for an honest same-answer-set comparison.
;;; Budget counts agenda expansions, not propagation relation checks.
;;; Result: (csp-result STATUS SOLUTIONS NODES RELATION-CHECKS PRUNED-VALUES).
;;; complete with no solutions means unsatisfiable within this finite model;
;;; incomplete with no solutions does NOT mean unsatisfiable.
(define-function symbolic-choose (domains name)
  (let ((branches ()))
    (list-do value (csp-domain domains name)
      (set branches (symbolic-append branches (list (csp-bind domains name value)))))
    branches))

(define-function csp-solve (domains constraints budget mode)
  (let ((agenda (list domains)) (solutions ()) (nodes 0) (checks 0) (pruned 0))
    (while (and agenda (< nodes budget))
      (let* ((raw (car agenda))
             (prop (if (= mode 'dfs) (list raw 0 0)
                     (csp-propagate raw constraints)))
             (current (car prop)))
        (set agenda (cdr agenda))
        (set nodes (+ nodes 1))
        (set checks (+ checks (symbolic-nth prop 1)))
        (set pruned (+ pruned (symbolic-nth prop 2)))
        (unless (csp-empty? current)
          (let ((name (csp-variable current (= mode 'propagate-mrv))))
            (if name
                (set agenda (symbolic-append (symbolic-choose current name) agenda))
              (begin
                (set checks (+ checks (symbolic-length constraints)))
                (if (csp-valid? current constraints)
                    (set solutions (symbolic-add solutions current)))))))))
    (list 'csp-result (if agenda 'incomplete 'complete) solutions nodes checks pruned)))

(define-function symbolic-solutions (domains constraints budget)
  (csp-solve domains constraints budget 'propagate-mrv))
