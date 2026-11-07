;;; d107-def.l — checked definitional basis over the same observations.
;;; A definition abbreviates a conjunctive query:
;;;   (def107 ID VARS PATTERN BODY)
;;; PATTERN : atoms over VARS (the query it names)
;;; BODY    : atoms or (call107 ID (TERMS...)); expanding calls must reproduce
;;;           PATTERN up to variable renaming and atom order.
;;; Definitions are conservative: they add no facts and change no answer. What
;;; changes is the inference unit (a plan step) and, later, its support.

(define-function p107-call (id terms) (list 'call107 id terms))
(define-function p107-call? (x) (and (p107-shape? x 3) (equal (car x) 'call107) (p107-name? (p107-nth x 1))))
(define-function p107-step? (x) (or (p107-atom? x) (p107-call? x)))

(define-function p107-def (id vars pattern body) (list 'def107 id vars pattern body))
(define-function p107-def? (d)
  (and (p107-shape? d 5) (equal (car d) 'def107) (p107-name? (p107-nth d 1))
       (p107-list? (p107-nth d 2)) (p107-list? (p107-nth d 3)) (p107-list? (p107-nth d 4))
       (not (p107-any? (lambda (a) (not (p107-atom? a))) (p107-nth d 3)))
       ;; body steps are atoms or call107, not arbitrary lists
       (not (p107-any? (lambda (s) (not (p107-step? s))) (p107-nth d 4)))))
(define-function p107-def-id (d) (p107-nth d 1))
(define-function p107-def-vars (d) (p107-nth d 2))
(define-function p107-def-pattern (d) (p107-nth d 3))
(define-function p107-def-body (d) (p107-nth d 4))
(define-function p107-defs? (ds) (and (p107-list? ds) (not (p107-any? (lambda (d) (not (p107-def? d))) ds))))
(define-function p107-find-def (ds id) (let ((out ())) (list-do d ds (if (equal (p107-def-id d) id) (set out d))) out))

(define-function p107-atom-vars (a) (p107-filter p107-var? (p107-args a)))
(define-function p107-all-vars (atoms)
  (let ((out ())) (list-do a atoms (set out (p107-union out (p107-atom-vars a)))) out))
(define-function p107-vars-of (pattern) (p107-all-vars pattern))
(define-function p107-rename-term (t map)
  (if (p107-var? t) (let ((hit (p107-assoc t map))) (if hit (p107-nth hit 1) t)) t))
(define-function p107-rename-atom (a map)
  (p107-atom (p107-pred a) (p107-map (lambda (t) (p107-rename-term t map)) (p107-args a))))
(define-function p107-sort-keys (xs)
  (if (not xs) ()
    (let ((head (car xs)) (less ()) (more ()))
      (list-do x (cdr xs)
        (if (> (string-compare x head) 0) (set more (p107-append more (list x)))
          (set less (p107-append less (list x)))))
      (p107-append (p107-sort-keys less) (p107-append (list head) (p107-sort-keys more))))))

;;; ---------- canonical key: smallest serialization over all variable bijections ----------
;;; Sorting variable names is NOT canonical: two isomorphic patterns with
;;; differently named variables can sort into different shapes. With at most 5
;;; variables we can enumerate the bijections and keep the lexicographically
;;; smallest key.
(define-function p107-perms (xs)
  (if (not xs) (list ())
    (let ((out ()))
      (list-do x xs
        (let ((rest (p107-filter (lambda (y) (not (equal y x))) xs)))
          (list-do p (p107-perms rest) (set out (p107-append out (list (cons x p)))))))
      out)))
(define-function p107-bind-vars (perm)
  (let ((m ()) (i 0))
    (list-do v perm
      (set m (p107-append m (list (list v (p107-var (string->symbol (concat-strings "v" (number->string i))))))))
      (set i (+ i 1)))
    m))
(define-function p107-key-under (atoms perm)
  (let ((m (p107-bind-vars perm)))
    (p107-join-strings
      (p107-sort-keys (p107-map (lambda (a) (p107-serialize (p107-rename-atom a m))) atoms)) " ")))
(define-function p107-conj-key (atoms)
  (let ((best "") (ps (p107-perms (p107-all-vars atoms))) (first true))
    (list-do perm ps
      (let ((k (p107-key-under atoms perm)))
        (if (or first (> (string-compare best k) 0)) (begin (set best k) (set first false)))))
    best))

;;; ---------- expansion ----------
(define-function p107-call-bindings (dvars terms)
  ;; exactly as many actuals as formals: admission and execution now share the
  ;; same arity rule (0.0110 review F5).
  (if (not dvars) (if terms 'bind-failed ())
    (if (not terms) 'bind-failed
      (let ((rest (p107-call-bindings (cdr dvars) (cdr terms))))
        (if (equal rest 'bind-failed) 'bind-failed (cons (list (car dvars) (car terms)) rest))))))
(define-function p107-expand-step (step defs depth)
  (if (> depth 16) 'expand-failed
    (if (not (p107-call? step)) (list step)
      (let* ((d (p107-find-def defs (p107-nth step 1)))
             (terms (p107-nth step 2)))
        (if (not d) 'expand-failed
          (let ((bind (p107-call-bindings (p107-def-vars d) terms)))
            (if (equal bind 'bind-failed) 'expand-failed
              (p107-map (lambda (a)
                (p107-atom (p107-pred a) (p107-map (lambda (t) (let ((h (p107-assoc t bind)))
                  (if h (p107-nth h 1) t))) (p107-args a))))
                (p107-def-pattern d)))))))))
(define-function p107-expand (body defs depth)
  (if (not body) ()
    (let ((head (p107-expand-step (car body) defs depth)))
      (if (equal head 'expand-failed) 'expand-failed
        (let ((rest (p107-expand (cdr body) defs depth)))
          (if (equal rest 'expand-failed) 'expand-failed (p107-append head rest)))))))

;;; ---------- validation ----------
(define-function p107-connected? (atoms)
  (if (not atoms) false
    (let ((seen (list (car atoms))) (vars (p107-atom-vars (car atoms))) (changed true))
      (while changed
        (set changed false)
        (list-do a atoms
          (if (and (not (p107-member? a seen)) (p107-intersection vars (p107-atom-vars a)))
            (begin (set seen (cons a seen)) (set vars (p107-union vars (p107-atom-vars a)))
                   (set changed true)))))
      (= (p107-len seen) (p107-len atoms)))))

;;; A query pattern is a proper, connected list of atoms. This guard runs before
;;; p107-atom-vars / p107-conj-key / p107-all-vars so a malformed public pattern
;;; is a rejection rather than a native fault.
(define-function p107-atoms? (xs)
  (and (p107-list? xs)
       (not (p107-any? (lambda (a) (not (p107-atom? a))) xs))))
(define-function p107-query-pattern? (xs)
  (and (p107-atoms? xs) (p107-connected? xs)))
(define-function p107-known-def? (defs id)
  ;; every call in a body must name an earlier definition
  (let ((found false))
    (list-do d defs (if (equal (p107-def-id d) id) (set found true)))
    found))
(define-function p107-calls-in (body) (p107-filter p107-call? body))
(define-function p107-body-vars (body)
  (let ((out ()))
    (list-do s body
      (if (p107-call? s)
        (list-do t (p107-nth s 2) (if (p107-var? t) (set out (p107-add out t))))
        (set out (p107-union out (p107-atom-vars s)))))
    out))
(define-function p107-var-order (atoms)
  ;; exported roles must follow first occurrence in the stored pattern
  (let ((out ()))
    (list-do a atoms
      (list-do t (p107-args a)
        (if (and (p107-var? t) (not (p107-member? t out))) (set out (p107-append out (list t))))))
    out))
(define-function p107-exact-key (atoms)
  ;; order-insensitive in atoms, but variable names are NOT renamed
  (p107-sort-keys (p107-map p107-serialize atoms)))
(define-function p107-def-ok? (d defs)
  (and (p107-def? d)
       (equal (p107-def-vars d) (p107-var-order (p107-def-pattern d)))
       (p107-connected? (p107-def-pattern d))
       (let ((exp (p107-expand (p107-def-body d) defs 0)))
         (and (not (equal exp 'expand-failed))
              ;; roles are the interface: compare with VARS fixed, no renaming
              (equal (p107-exact-key exp) (p107-exact-key (p107-def-pattern d)))
              (p107-set-equal? (p107-all-vars exp) (p107-all-vars (p107-def-pattern d)))))))

;;; ---------- keep the longest prefix that still checks ----------
(define-function p107-revalidate (defs)
  ;; after a revision, keep the longest prefix of definitions that still checks
  (let ((kept ()) (dropped ()) (ok true))
    (list-do d defs
      (if (and ok (p107-def-ok? d kept))
        (set kept (p107-append kept (list d)))
        (begin (set ok false) (set dropped (p107-append dropped (list (p107-def-id d)))))))
    (list kept dropped)))