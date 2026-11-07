;;; d107-surface.l — a small Shen-inspired surface notation for contracts,
;;; library units and checked definitions. This is an EXPANDER, not a new
;;; kernel: every surface form is matched with d107-match.l, expanded to the
;;; canonical c107/unit107/def107 data, and
;;; then re-validated by p107-c-valid?. The canonical IR remains the only thing
;;; the verifier, checker and evidence boundary accept.
;;;
;;; Contract surface:
;;;   (contract NAME (VARS...)
;;;     (pre EXPR)
;;;     (body (STMT...))
;;;     (post EXPR)
;;;     (frame (VAR...)))
;;;
;;; Unit surface (the name occurs twice on purpose: repeated-variable matching
;;; enforces that the unit name and the contract name are the same):
;;;   (unit NAME
;;;     (contract NAME (VARS...) (pre ...) (body ...) (post ...) (frame ...))
;;;     (CASES...))
;;;
;;; Definition surface:
;;;   (define NAME (VARS...)
;;;     (pattern (ATOM...))
;;;     (body (STEP...)))          STEP = ATOM | (call NAME (TERM...))
;;;
;;; Results: (ok CANONICAL) or (invalid REASON). A dotted surface form is an
;;; error in the matcher and is reported as an invalid surface, never as a
;;; silent mismatch. The canonical IR is re-validated before (ok ...).

(define-function p107-sfc-pat ()
  (list 'contract (p107-pat-var 'name) (p107-pat-var 'vars)
        (list 'pre (p107-pat-var 'pre))
        (list 'body (p107-pat-var 'body))
        (list 'post (p107-pat-var 'post))
        (list 'frame (p107-pat-var 'frame))))

(define-function p107-sfu-pat ()
  (list 'unit (p107-pat-var 'name) (p107-sfc-pat) (p107-pat-var 'cases)))

(define-function p107-sfc-bind (binds key)
  (let ((h (p107-assoc key binds))) (if h (p107-nth h 1) 'missing)))

(define-function p107-sfc-body (binds)
  (let* ((name (p107-sfc-bind binds 'name)) (vars (p107-sfc-bind binds 'vars))
         (pre (p107-sfc-bind binds 'pre)) (body (p107-sfc-bind binds 'body))
         (post (p107-sfc-bind binds 'post)) (frame (p107-sfc-bind binds 'frame)))
    (list 'c107 name vars pre body post frame)))

(define-function p107-sc (form)
  (let ((r (p107-match1 (p107-sfc-pat) form ())))
    (cond
      ((equal (car r) 'error) (list 'invalid 'surface-pattern))
      ((not (equal (car r) 'ok)) (list 'invalid 'surface-shape))
      (else
        (let ((c (p107-sfc-body (p107-nth r 1))))
          (if (p107-c-valid? c) (list 'ok c) (list 'invalid 'contract)))))))

(define-function p107-su (form)
  (let ((r (p107-match1 (p107-sfu-pat) form ())))
    (cond
      ((equal (car r) 'error) (list 'invalid 'surface-pattern))
      ((not (equal (car r) 'ok)) (list 'invalid 'surface-shape))
      (else
        (let* ((b (p107-nth r 1)) (c (p107-sfc-body b))
               (name (p107-sfc-bind b 'name)) (cases (p107-sfc-bind b 'cases)))
          (if (and (p107-c-valid? c) (p107-list? cases))
            (list 'ok (list 'unit107 name c cases))
            (list 'invalid 'unit)))))))

;;; Canonical -> surface writers make round-trips testable.
(define-function p107-sc-write (c)
  (list 'contract (p107-nth c 1) (p107-nth c 2)
        (list 'pre (p107-nth c 3))
        (list 'body (p107-nth c 4))
        (list 'post (p107-nth c 5))
        (list 'frame (p107-nth c 6))))

(define-function p107-su-write (u)
  (list 'unit (p107-nth u 1) (p107-sc-write (p107-nth u 2)) (p107-nth u 3)))
;;; ------------------------------------------------------------------ definitions
;;; Surface:
;;;   (define NAME (VARS...)
;;;     (pattern (ATOM...))
;;;     (body (STEP...)))          STEP = ATOM | (call NAME (TERM...))
;;; Expands to (def107 NAME VARS PATTERN BODY). `call` is surface sugar for the
;;; canonical `call107`; atoms stay canonical `(atom PRED (TERMS...))`.
(define-function p107-sfd-pat ()
  (list 'define (p107-pat-var 'name) (p107-pat-var 'vars)
        (list 'pattern (p107-pat-var 'pattern))
        (list 'body (p107-pat-var 'body))))

(define-function p107-sd-step (s)
  (if (and (p107-shape? s 3) (equal (car s) 'call))
    (list 'call107 (p107-nth s 1) (p107-nth s 2))
    s))

(define-function p107-sd-body (body)
  (if (not (p107-list? body)) body (p107-map p107-sd-step body)))

(define-function p107-sd (form)
  (let ((r (p107-match1 (p107-sfd-pat) form ())))
    (cond
      ((equal (car r) 'error) (list 'invalid 'surface-pattern))
      ((not (equal (car r) 'ok)) (list 'invalid 'surface-shape))
      (else
        (let* ((b (p107-nth r 1)) (name (p107-sfc-bind b 'name))
               (vars (p107-sfc-bind b 'vars)) (pattern (p107-sfc-bind b 'pattern))
               (body (p107-sd-body (p107-sfc-bind b 'body)))
               (d (list 'def107 name vars pattern body)))
          (if (p107-def? d) (list 'ok d) (list 'invalid 'definition)))))))

(define-function p107-sd-write-step (s)
  (if (p107-call? s) (list 'call (p107-nth s 1) (p107-nth s 2)) s))

(define-function p107-sd-write (d)
  (list 'define (p107-nth d 1) (p107-nth d 2)
        (list 'pattern (p107-nth d 3))
        (list 'body (p107-map p107-sd-write-step (p107-nth d 4)))))
