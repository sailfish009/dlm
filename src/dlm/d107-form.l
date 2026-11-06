;;; d107-form.l — terms, atoms, rules, substitutions.
;;; Fixes from the 0.0103 review: an extensional predicate can no longer be a
;;; rule head, and rules must be range-restricted (every head/negative variable
;;; occurs in a positive body atom). Negation remains EDB-only, so every program
;;; is stratified by construction.
;;; Maru treats () as false, so a substitution is wrapped: (subst (var val) ...).

(define-function p107-const? (x) (or (string? x) (and (symbol? x) (not (equal x ())))))
(define-function p107-var (name) (list 'var name))
(define-function p107-var? (x) (and (p107-shape? x 2) (= (car x) 'var) (symbol? (p107-nth x 1))))
(define-function p107-atom (pred args) (list 'atom pred args))
(define-function p107-term? (x) (or (p107-const? x) (p107-var? x)))
(define-function p107-atom? (a) (and (p107-shape? a 3) (= (car a) 'atom)
  (symbol? (p107-nth a 1)) (p107-list? (p107-nth a 2))
  (not (p107-any? (lambda (x) (not (p107-term? x))) (p107-nth a 2)))))
(define-function p107-pred (a) (p107-nth a 1))
(define-function p107-args (a) (p107-nth a 2))
(define-function p107-neg (a) (list 'not a))
(define-function p107-neg? (x) (and (p107-shape? x 2) (= (car x) 'not) (p107-atom? (p107-nth x 1))))
(define-function p107-lit-atom (l) (if (p107-neg? l) (p107-nth l 1) l))
(define-function p107-ground-atom? (a) (and (p107-atom? a) (not (p107-any? p107-var? (p107-args a)))))
(define-function p107-atom-key (a) (cons (p107-pred a) (p107-args a)))
(define-function p107-name? (x)
  (cond ((string? x) (and (> (string-length x) 0) (<= (string-length x) 64)))
        ((symbol? x) (not (equal x ()))) (else false)))
(define-function p107-given-id (id atom) (list 'fact id atom (list 'given id)))

(define-function p107-atom-var-names (a) (p107-filter p107-var? (p107-args a)))
(define-function p107-body-vars-of (body)
  (let ((out ()))
    (list-do l body (if (not (p107-neg? l)) (set out (p107-union out (p107-atom-var-names l)))))
    out))
(define-function p107-named-vars (body)
  (let ((out ()))
    (list-do l body
      (if (p107-neg? l) (set out (p107-union out (p107-atom-var-names (p107-nth l 1))))))
    out))
(define-function p107-set-equal? (a b)
  (and (= (p107-len a) (p107-len b)) (not (p107-any? (lambda (x) (not (p107-member? x b))) a))))

(define-function p107-rule (head body) (list 'rule head body))
(define-function p107-rule? (r) (and (p107-shape? r 3) (= (car r) 'rule)
  (p107-atom? (p107-nth r 1)) (p107-list? (p107-nth r 2))
  (not (p107-any? (lambda (l) (not (or (p107-atom? l) (p107-neg? l)))) (p107-nth r 2)))))
(define-function p107-rule-head (r) (p107-nth r 1))
(define-function p107-rule-body (r) (p107-nth r 2))

(define *p107-edb* ())
(define-function p107-edb? (p) (p107-member? p *p107-edb*))
(define-function p107-rule-safe? (r)
  (and (p107-rule? r)
       ;; closed-world predicates stay in the extensional base
       (not (p107-edb? (p107-pred (p107-rule-head r))))
       ;; negation only over extensional predicates
       (not (p107-any? (lambda (l) (and (p107-neg? l) (not (p107-edb? (p107-pred (p107-nth l 1))))))
                       (p107-rule-body r)))
       ;; range restriction
       (let ((need (p107-union (p107-atom-var-names (p107-rule-head r)) (p107-named-vars (p107-rule-body r))))
             (have (p107-body-vars-of (p107-rule-body r))))
         (not (p107-any? (lambda (v) (not (p107-member? v have))) need)))))

(define-function p107-subst (pairs) (cons 'subst pairs))
(define-function p107-pairs (s) (cdr s))
(define-function p107-subst-term (t s)
  (if (p107-var? t) (let ((v (p107-assoc t (p107-pairs s)))) (if v (p107-nth v 1) t)) t))
(define-function p107-subst-args (args s)
  (if args (cons (p107-subst-term (car args) s) (p107-subst-args (cdr args) s)) ()))
(define-function p107-subst-atom (a s) (p107-atom (p107-pred a) (p107-subst-args (p107-args a) s)))

(define-function p107-bind (v value s)
  (let ((old (p107-assoc v (p107-pairs s))))
    (if old (if (equal (p107-nth old 1) value) s false)
      (p107-subst (cons (list v value) (p107-pairs s))))))
(define-function p107-unify-term (t1 t2 s)
  (cond ((equal s false) false)
        ((p107-var? t1) (p107-bind t1 (p107-subst-term t2 s) s))
        ((p107-var? t2) (p107-bind t2 (p107-subst-term t1 s) s))
        ((equal t1 t2) s) (else false)))
(define-function p107-unify-args (a b s)
  (cond ((equal s false) false) ((not a) s) ((not b) false)
        (else (p107-unify-args (cdr a) (cdr b) (p107-unify-term (car a) (car b) s)))))
(define-function p107-match (pattern fact s)
  (if (not (equal (p107-pred pattern) (p107-pred fact))) false
    (if (not (= (p107-len (p107-args pattern)) (p107-len (p107-args fact)))) false
      (p107-unify-args (p107-args pattern) (p107-args fact) s))))