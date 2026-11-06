;;; d107-close.l — closed-world negation is evaluated AFTER all positive
;;; literals are bound (so literal order cannot change the answer), and a proof
;;; is accepted only if every child's own proof checks recursively.
;;;
;;; Fixes from the 0.0104 review:
;;;  - negated literals were solved in body order, so `not p(x), q(x)` never fired
;;;    and a complete-empty result was wrong;
;;;  - a fact with an invalid proof still received a rank, and later conclusions
;;;    built on it were accepted (rank is not justification). Ranks are gone;
;;;    validation walks the derivation DAG with cycle and depth guards;
;;;  - proof structure and rule indices were not validated, so a negative index
;;;    recursed forever.

(define-function p107-positives (body) (p107-filter (lambda (l) (not (p107-neg? l))) body))
(define-function p107-negatives (body) (p107-filter p107-neg? body))

(define-function p107-facts? (fs)
  (and (p107-list? fs)
       (not (p107-any? (lambda (f) (not (and (p107-shape? f 3) (p107-ground-atom? (p107-nth f 2))))) fs))))
(define-function p107-rules? (rs) (and (p107-list? rs) (not (p107-any? (lambda (r) (not (p107-rule-safe? r))) rs))))
(define-function p107-fact-in? (key fs) (p107-any? (lambda (f) (equal key (p107-atom-key (p107-nth f 2)))) fs))
(define-function p107-given-in? (key fs)
  (p107-any? (lambda (f) (and (equal key (p107-atom-key (p107-nth f 2)))
                              (let ((p (p107-nth f 3))) (and (p107-shape? p 2) (equal (car p) 'given)))))
             fs))

(define *p107-steps* 0)
(define *p107-budget* 20000)
(define *p107-exhausted* false)
(define-function p107-spend ()
  (set *p107-steps* (+ *p107-steps* 1))
  (if (> *p107-steps* *p107-budget*) (begin (set *p107-exhausted* true) false) true))

;;; positive join only
(define-function p107-solve-pos (lits facts sub)
  (if (not lits) (list sub)
    (if (not (p107-spend)) ()
      (let ((out ()))
        (list-do f facts
          (let ((s2 (p107-match (car lits) (p107-nth f 2) sub)))
            (if s2 (set out (p107-append out (p107-solve-pos (cdr lits) facts s2))))))
        out))))

;;; every negated literal must be absent from the EXTENSIONAL base
(define-function p107-negs-ok? (lits facts sub)
  (if (not lits) true
    (let ((target (p107-subst-atom (p107-nth (car lits) 1) sub)))
      (if (not (p107-ground-atom? target)) false
        (if (p107-given-in? (p107-atom-key target) facts) false
          (p107-negs-ok? (cdr lits) facts sub))))))

(define-function p107-solve (body facts sub)
  (let ((subs (p107-solve-pos (p107-positives body) facts sub)) (out ()) (neg (p107-negatives body)))
    (list-do s subs (if (p107-negs-ok? neg facts s) (set out (p107-append out (list s)))))
    out))

(define-function p107-lookup (atom table)
  (let ((out ()) (key (p107-atom-key atom)))
    (list-do f table (if (equal key (p107-atom-key (p107-nth f 2))) (set out f))) out))
(define-function p107-evidence (atom table)
  (let ((f (p107-lookup atom table))) (if f (p107-nth f 3) ())))
(define-function p107-fact-by-id (id table)
  (let ((out ())) (list-do f table (if (equal (p107-nth f 1) id) (set out f))) out))

(define-function p107-child-ids (body facts sub)
  (let ((out ()) (ok true))
    (list-do l (p107-positives body)
      (if ok
        (let* ((a (p107-subst-atom l sub)) (f (p107-lookup a facts)))
          (if f (set out (p107-append out (list (p107-nth f 1)))) (set ok false)))))
    (if ok (list 'ids out) false)))

(define-function p107-derive-pass (facts rules next-id)
  (let ((new ()) (id next-id) (n 0))
    (list-do r rules
      (if (not *p107-exhausted*)
        (list-do sub (p107-solve (p107-rule-body r) facts (p107-subst ()))
          (if (not *p107-exhausted*)
            (let* ((head (p107-subst-atom (p107-rule-head r) sub))
                   (key (p107-atom-key head))
                   (kids (p107-child-ids (p107-rule-body r) facts sub)))
              (if (and (p107-ground-atom? head) kids
                       (not (p107-fact-in? key facts)) (not (p107-fact-in? key new)))
                (begin
                  (set new (p107-append new (list (list 'fact (concat-strings "d" (number->string id))
                    head (list 'pr n (p107-pairs sub) (p107-nth kids 1))))))
                  (set id (+ id 1))))))))
      (set n (+ n 1)))
    (list new id)))

(define-function p107-close (facts rules budget)
  (set *p107-steps* 0) (set *p107-exhausted* false) (set *p107-budget* budget)
  (let ((table facts) (id 0) (changed true))
    (while (and changed (not *p107-exhausted*))
      (let* ((r (p107-derive-pass table rules id)) (new (car r)))
        (set id (p107-nth r 1))
        (if new (set table (p107-append table new)) (set changed false))))
    (list 'closed (if *p107-exhausted* 'unknown 'complete) table *p107-steps*)))

;;; ---------------- proof structure ----------------
(define-function p107-tvar? (x) (and (p107-shape? x 2) (equal (car x) 'var) (symbol? (p107-nth x 1))))
(define-function p107-pair? (p) (and (p107-shape? p 2) (p107-tvar? (p107-nth p 0)) (p107-const? (p107-nth p 1))))
(define-function p107-pairs? (ps) (and (p107-list? ps) (not (p107-any? (lambda (p) (not (p107-pair? p))) ps))))
(define-function p107-names? (xs) (and (p107-list? xs) (not (p107-any? (lambda (x) (not (p107-name? x))) xs))))
(define-function p107-proof-shape? (p)
  (cond ((and (p107-shape? p 2) (equal (car p) 'given)) (p107-name? (p107-nth p 1)))
        ((and (p107-shape? p 4) (equal (car p) 'pr))
         (and (is <long> (p107-nth p 1)) (>= (p107-nth p 1) 0)
              (p107-pairs? (p107-nth p 2)) (p107-names? (p107-nth p 3))))
        (else false)))
(define-function p107-rule-at (rules i)
  (if (not (pair? rules)) ()
    (if (not (and (is <long> i) (>= i 0))) ()
      (if (= i 0) (car rules) (p107-rule-at (cdr rules) (- i 1))))))

;;; ---------------- iterative, cycle-safe validation ----------------
;;; A proof is accepted only if every step is a valid rule instance and every
;;; child's OWN stored proof checks. The worklist is bounded so a cyclic or
;;; endlessly expanding derivation is refused instead of looping.

(define-function p107-rule-instance? (r atom sub table)
  (and r
       (equal (p107-atom-key atom) (p107-atom-key (p107-subst-atom (p107-rule-head r) sub)))
       (p107-negs-ok? (p107-negatives (p107-rule-body r)) table sub)))

(define-function p107-children? (lits kids table sub)
  (if (not lits) (not kids)
    (if (not (pair? kids)) false
      (let ((f (p107-fact-by-id (car kids) table)))
        (and f
             (equal (p107-atom-key (p107-subst-atom (car lits) sub)) (p107-atom-key (p107-nth f 2)))
             (p107-children? (cdr lits) (cdr kids) table sub))))))

(define-function p107-push-kids (kids table queue)
  (let ((out queue))
    (list-do k kids
      (let ((f (p107-fact-by-id k table)))
        (if f (set out (p107-append out (list (list (p107-nth f 3) (p107-nth f 2))))))))
    out))

(define-function p107-validate (queue table rules n limit)
  (cond ((not queue) true)
        ((> n limit) false)
        (else
          (let* ((item (car queue)) (proof (car item)) (atom (p107-nth item 1)))
            (if (not (p107-proof-shape? proof)) false
              (if (equal (car proof) 'given)
                (let ((f (p107-fact-by-id (p107-nth proof 1) table)))
                  (and f (equal (p107-atom-key atom) (p107-atom-key (p107-nth f 2)))
                       (let ((p (p107-nth f 3))) (and (p107-shape? p 2) (equal (car p) 'given)))
                       (p107-validate (cdr queue) table rules (+ n 1) limit)))
                (let* ((sub (p107-subst (p107-nth proof 2)))
                       (kids (p107-nth proof 3))
                       (r (p107-rule-at rules (p107-nth proof 1)))
                       (pos (p107-positives (p107-rule-body r))))
                  (if (and (p107-rule-instance? r atom sub table)
                           (p107-children? pos kids table sub))
                    (p107-validate (p107-push-kids kids table (cdr queue)) table rules (+ n 2) limit)
                    false))))))))

(define-function p107-proof-ok? (proof atom table rules)
  (p107-validate (list (list proof atom)) table rules 0
                 (+ 32 (* 4 (p107-len table)))))
