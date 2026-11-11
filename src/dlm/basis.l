;;; basis.l — accumulated, versioned basis axioms.
;;; Learning produces candidate rules; a basis axiom makes them usable only
;;; while active. Proof remains the truth gate.
(define-function b-axiom (id rules evidence support version status history)
  (list 'baxiom id rules evidence support version status history))
(define-function b-axiom? (x)
  (and (l-shape? x 8) (equal (car x) 'baxiom) (l-name? (l-nth x 1))
       (l-list? (l-nth x 2)) (l-list? (l-nth x 3)) (l-list? (l-nth x 4))
       (l-member? (l-nth x 6) '(active inactive))
       (l-list? (l-nth x 7))))
(define-function b-id (x) (l-nth x 1))
(define-function b-rules (x) (l-nth x 2))
(define-function b-evidence (x) (l-nth x 3))
(define-function b-support (x) (l-nth x 4))
(define-function b-version (x) (l-nth x 5))
(define-function b-status (x) (l-nth x 6))
(define-function b-history (x) (l-nth x 7))

(define-function b-find (id xs)
  (let ((hit (l-filter (lambda (x) (equal id (b-id x))) xs)))
    (if hit (car hit) ())))
(define-function b-put (ax xs)
  (cons ax (l-filter (lambda (x) (not (equal (b-id ax) (b-id x)))) xs)))
(define-function b-add (basis id rules evidence support)
  (if (b-find id basis) basis
    (l-append basis (list (b-axiom id rules evidence support 0 'inactive ())))))
(define-function b-set-status (basis id status)
  (let ((ax (b-find id basis)))
    (if (not ax) basis
      (b-put (b-axiom id (b-rules ax) (b-evidence ax) (b-support ax)
                      (+ (b-version ax) 1) status
                      (l-append (b-history ax) (list (list (b-status ax) (b-version ax)))))
             basis))))
(define-function b-activate (basis id) (b-set-status basis id 'active))
(define-function b-deactivate (basis id) (b-set-status basis id 'inactive))
(define-function l-remove-nth (xs n)
  (if (not xs) ()
    (if (= n 0) (cdr xs) (cons (car xs) (l-remove-nth (cdr xs) (- n 1))))))
(define-function b-rollback (basis id)
  (let ((ax (b-find id basis)))
    (if (or (not ax) (not (b-history ax))) basis
      (let* ((h (b-history ax)) (last (l-nth h (- (l-len h) 1)))
             (prev (l-remove-nth h (- (l-len h) 1))))
        (b-put (b-axiom id (b-rules ax) (b-evidence ax) (b-support ax)
                        (l-nth last 1) (car last) prev) basis)))))
(define-function b-active-rules (basis)
  (let ((out ()))
    (list-do ax basis
      (if (equal (b-status ax) 'active)
        (set out (l-append out (b-rules ax)))))
    out))
(define-function b-active-ids (basis)
  (let ((out ()))
    (list-do ax basis (if (equal (b-status ax) 'active) (set out (l-append out (list (b-id ax))))))
    out))

;;; Deduplicate basis axioms with identical rules/evidence/support.
(define-function b-key (ax)
  (list (b-rules ax) (b-evidence ax) (b-support ax)))
(define-function b-cse (basis)
  (let ((seen ()) (out ()))
    (list-do ax basis
      (let ((k (b-key ax)))
        (if (not (l-any? (lambda (e) (equal k (car e))) seen))
          (begin
            (set seen (l-append seen (list (list k ax))))
            (set out (l-append out (list ax)))))))
    out))
