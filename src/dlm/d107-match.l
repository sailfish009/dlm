;;; d107-match.l — Shen-inspired structural matching as a library, not a new VM.
;;; Semantics fixed by tests:
;;;   mismatch  -> (no-match)   and the caller tries the next clause
;;;   guard     -> false = mismatch, never an error
;;;   repeated  -> the same value, not merely the same shape
;;;   empty     -> (ok ()) is SUCCESS and must not be read as failure
;;;   bad input -> (error reason); never silently treated as mismatch
(define-function p107-pat (x) x)
(define-function p107-pat-var? (x) (and (p107-shape? x 2) (equal (car x) 'pat) (symbol? (p107-nth x 1))))
(define-function p107-pat-var (n) (list 'pat n))

(define-function p107-match1 (pat value binds)
  ;; returns (ok (binds ...)) | (no-match) | (error reason)
  (cond
    ((p107-pat-var? pat)
      (let ((old (p107-assoc (p107-nth pat 1) binds)))
        (if old
          (if (equal (p107-nth old 1) value) (list 'ok binds) '(no-match))
          (list 'ok (p107-append binds (list (list (p107-nth pat 1) value)))))))
    ((pair? pat)
      (if (not (p107-list? pat)) '(error dotted-pattern)
        (if (not (p107-list? value)) '(no-match)
          (let ((b1 (p107-match1 (car pat) (if value (car value) ()) binds)))
            (cond
              ((not (equal (car b1) 'ok)) b1)
              (else (p107-match1 (cdr pat) (if value (cdr value) ()) (p107-nth b1 1))))))))
    (else
      (if (equal pat value) (list 'ok binds) '(no-match)))))

(define-function p107-match-all (pats values binds)
  (cond
    ((not pats) (list 'ok binds))
    ((not values) '(no-match))
    (else
      (let ((r (p107-match1 (car pats) (car values) binds)))
        (if (equal (car r) 'ok) (p107-match-all (cdr pats) (cdr values) (p107-nth r 1)) r)))))

;;; (p107-cases value ((PATTERN (guard) BODY) ...) fallback)
;;; guard is a function of the bindings; it returns true/false only.
(define-function p107-cases (value clauses fallback)
  (if (not clauses) (fallback)
    (let* ((c (car clauses)) (pat (p107-nth c 0)) (guard (p107-nth c 1)) (body (p107-nth c 2))
           (r (p107-match1 pat value ())))
      (cond
        ((equal (car r) 'error) r)
        ((not (equal (car r) 'ok)) (p107-cases value (cdr clauses) fallback))
        ((and guard (not (guard (p107-nth r 1)))) (p107-cases value (cdr clauses) fallback))
        (else (list 'ok (body (p107-nth r 1))))))))
