;;; Matching and routing propose plans; they never confer logical truth.
;;; Binding succeeds with (ok ENV), including an empty environment.
(define-function b91-bind (env key value)
  (let ((entry (dlm-assoc key env)))
    (if entry (if (equal (dlm-nth entry 1) value) (list 'ok env) ())
      (list 'ok (dlm-append env (list (list key value)))))))
(define-function b91-map-atom (a b env)
  (if (not (equal (car a) (car b))) ()
    (let ((one (b91-bind env (dlm-nth a 1) (dlm-nth b 1))))
      (if one (b91-bind (dlm-nth one 1) (dlm-nth a 2) (dlm-nth b 2)) ()))))
(define-function b91-embeds (body remaining env)
  (if (not body) (list (list 'embedding91 env remaining))
    (let ((out ())) (list-do a remaining
      (let ((one (b91-map-atom (car body) a env)))
        (if one (set out (dlm-append out
          (b91-embeds (cdr body) (dlm-difference remaining (list a)) (dlm-nth one 1))))))) out)))
(define-function b91-args (env n)
  (let ((out ())) (list-do i (b91-range n) (set out (dlm-append out (list (s79-at env i))))) out))
(define-function b91-cover (p lib)
  (if (not p) ()
    (let ((best (cons (list 'fact91 (car (car p)) (cdr (car p))) (b91-cover (cdr p) lib))))
      (list-do m lib
        (list-do e (b91-embeds (dlm-nth m 2) p ())
          (let ((candidate (cons (list 'call91 (dlm-nth m 1)
              (b91-args (dlm-nth e 1) (b91-arity (dlm-nth m 2))))
              (b91-cover (dlm-nth e 2) lib))))
            (if (< (dlm-length candidate) (dlm-length best)) (set best candidate))))) best)))
(define-function b91-plan (p sig lib) (b91-cover p lib))
(define-function b91-rewrites (readings sig lib)
  (let ((out ())) (list-do v readings
    (set out (dlm-append out (list (list 'rewrite91 (dlm-nth v 1) (dlm-nth v 2)
      (dlm-nth v 3) (dlm-nth v 4) (b91-plan (dlm-nth v 3) sig lib)))))) out))
