;;; -*- mode: lisp; coding: us-ascii -*-
;;; Load after boot.l: maru boot.l dlm.l -
;;; Terms: constants are strings/symbols; variables are (var NAME).
;;; This is a small reference kernel, not the Python persistence/web runtime.
;;; All public names are prefixed to avoid changing Maru's runtime bindings.

(define-function dlm-nth (xs n)
  (if (= n 0) (car xs) (dlm-nth (cdr xs) (- n 1))))

(define-function dlm-length (xs)
  (if xs (+ 1 (dlm-length (cdr xs))) 0))

(define-function dlm-append (xs ys)
  (if xs (cons (car xs) (dlm-append (cdr xs) ys)) ys))

(define-function dlm-member? (x xs)
  (and xs (or (equal x (car xs)) (dlm-member? x (cdr xs)))))

(define-function dlm-add (xs x)
  (if (dlm-member? x xs) xs (dlm-append xs (list x))))

(define-function dlm-union (xs ys)
  (if ys (dlm-union (dlm-add xs (car ys)) (cdr ys)) xs))

(define-function dlm-intersection (xs ys)
  (if xs
      (if (dlm-member? (car xs) ys)
          (cons (car xs) (dlm-intersection (cdr xs) ys))
        (dlm-intersection (cdr xs) ys))
    ()))

(define-function dlm-difference (xs ys)
  (if xs
      (if (dlm-member? (car xs) ys)
          (dlm-difference (cdr xs) ys)
        (cons (car xs) (dlm-difference (cdr xs) ys)))
    ()))

(define-function dlm-assoc (key xs)
  (if xs
      (if (equal key (car (car xs))) (car xs)
        (dlm-assoc key (cdr xs)))
    ()))

(define-function dlm-var (name) (list 'var name))
(define-function dlm-var? (x)
  (and (pair? x) (= (car x) 'var) (= (dlm-length x) 2)))
(define-function dlm-atom (pred . args) (list 'atom pred args))
(define-function dlm-pred (a) (dlm-nth a 1))
(define-function dlm-args (a) (dlm-nth a 2))
(define-function dlm-rule (head . body) (list 'rule head body))
(define-function dlm-head (r) (dlm-nth r 1))
(define-function dlm-body (r) (dlm-nth r 2))

(define-function dlm-vars (terms)
  (if terms
      (if (dlm-var? (car terms))
          (dlm-add (dlm-vars (cdr terms)) (car terms))
        (dlm-vars (cdr terms)))
    ()))

(define-function dlm-body-vars (body)
  (if body
      (dlm-union (dlm-vars (dlm-args (car body)))
                 (dlm-body-vars (cdr body)))
    ()))

(require "src/dlm/validation.l")

(define-function dlm-safe? (r)
  (and (dlm-rule? r) (dlm-body r)
       (not (dlm-difference (dlm-vars (dlm-args (dlm-head r)))
                            (dlm-body-vars (dlm-body r))))))

(define-function dlm-ground? (a) (not (dlm-vars (dlm-args a))))

;;; Successful matches return (ok ENV), including the empty environment.
(define-function dlm-match-terms (ps fs env)
  (if ps
      (let ((p (car ps)) (f (car fs)))
        (if (dlm-var? p)
            (let ((binding (dlm-assoc p env)))
              (if binding
                  (and (equal (dlm-nth binding 1) f)
                       (dlm-match-terms (cdr ps) (cdr fs) env))
                (dlm-match-terms (cdr ps) (cdr fs)
                                (cons (list p f) env))))
          (and (equal p f) (dlm-match-terms (cdr ps) (cdr fs) env))))
    (list 'ok env)))

(define-function dlm-match (pattern fact env)
  (and (equal (dlm-pred pattern) (dlm-pred fact))
       (= (dlm-length (dlm-args pattern)) (dlm-length (dlm-args fact)))
       (dlm-ground? fact)
       (dlm-match-terms (dlm-args pattern) (dlm-args fact) env)))

(define-function dlm-subst-terms (terms env)
  (if terms
      (let ((binding (dlm-assoc (car terms) env)))
        (cons (if binding (dlm-nth binding 1) (car terms))
              (dlm-subst-terms (cdr terms) env)))
    ()))

(define-function dlm-substitute (a env)
  (list 'atom (dlm-pred a) (dlm-subst-terms (dlm-args a) env)))

(define-function dlm-fact-proof (a) (list 'proof a 'fact () ()))
(define-function dlm-rule-proof (a r ps) (list 'proof a 'rule r ps))
(define-function dlm-conclusion (p) (dlm-nth p 1))

(define-function dlm-seed-proofs (facts)
  (if facts
      (begin
        (if (not (dlm-ground? (car facts))) (error "DLM: facts must be ground"))
        (cons (dlm-fact-proof (car facts)) (dlm-seed-proofs (cdr facts))))
    ()))

(define-function dlm-find-proof (a proofs)
  (if proofs
      (if (equal a (dlm-conclusion (car proofs))) (car proofs)
        (dlm-find-proof a (cdr proofs)))
    ()))

;;; Join states are (ENV PREMISES); each literal uses exact matching.
(define-function dlm-join (body proofs states)
  (if body
      (let ((next ()))
        (list-do state states
          (list-do proof proofs
            (let ((m (dlm-match (car body) (dlm-conclusion proof) (car state))))
              (if m
                  (set next (cons (list (dlm-nth m 1)
                                        (dlm-append (dlm-nth state 1) (list proof)))
                                  next))))))
        (dlm-join (cdr body) proofs next))
    states))

;;; Full indexed/delta optimization is deliberately deferred; semantics first.
;;; Budget counts fixpoint passes, not instructions or unification operations.
(define-function dlm-derive-result (proofs rules budget)
  (let ((changed true))
    (while (and changed (> budget 0))
      (set budget (- budget 1))
      (set changed false)
      (list-do r rules
        (if (not (dlm-safe? r)) (error "DLM: unsafe rule"))
        (list-do state (dlm-join (dlm-body r) proofs (list (list () ())))
          (let ((a (dlm-substitute (dlm-head r) (car state))))
            (if (and (dlm-ground? a) (not (dlm-find-proof a proofs)))
                (begin
                  (set proofs (dlm-append proofs
                    (list (dlm-rule-proof a r (dlm-nth state 1)))))
                  (set changed true)))))))
    (list 'derivation (if changed 'incomplete 'complete) proofs)))

(define-function dlm-derive (proofs rules budget)
  (let ((result (dlm-derive-result proofs rules budget)))
    (if (= (dlm-nth result 1) 'incomplete)
        (error "DLM: fixpoint budget exhausted; result is incomplete"))
    (dlm-nth result 2)))

(define-function dlm-proofs (facts rules budget)
  (dlm-derive (dlm-seed-proofs facts) rules budget))

(define-function dlm-conclusions (proofs)
  (if proofs
      (dlm-add (dlm-conclusions (cdr proofs)) (dlm-conclusion (car proofs)))
    ()))

(define-function dlm-closure (facts rules)
  (dlm-conclusions (dlm-proofs facts rules 1000)))

(define-function dlm-prove (facts rules target)
  (dlm-find-proof target (dlm-proofs facts rules 1000)))

(define dlm-verify ())

(define-function dlm-verify-premises (body premises facts rules env fuel)
  (if body
      (and premises
           (dlm-verify (car premises) facts rules fuel)
           (let ((m (dlm-match (car body) (dlm-conclusion (car premises)) env)))
             (and m (dlm-verify-premises (cdr body) (cdr premises) facts rules
                                        (dlm-nth m 1) fuel))))
    (and (not premises) (list 'ok env))))

(set dlm-verify
  (lambda (p facts rules fuel)
    (and (> fuel 0) (pair? p) (dlm-proper? p 6)
         (= (dlm-length p) 5) (= (car p) 'proof)
         (let ((a (dlm-conclusion p)) (kind (dlm-nth p 2))
               (r (dlm-nth p 3)) (ps (dlm-nth p 4)))
           (and (dlm-atom? a) (dlm-ground? a)
                (dlm-proper? ps 1000)
                (if (= kind 'fact)
                    (and (not r) (not ps) (dlm-member? a facts))
                  (and (= kind 'rule) (dlm-member? r rules) (dlm-safe? r)
                       (let ((m (dlm-verify-premises (dlm-body r) ps facts rules
                                                    () (- fuel 1))))
                         (and m (equal a (dlm-substitute (dlm-head r)
                                                       (dlm-nth m 1))))))))))))

(define-function dlm-verify-proof (proof facts rules)
  (dlm-verify proof facts rules 1000))

