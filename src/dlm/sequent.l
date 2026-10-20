;;; Ordered occurrence lists: duplicates and their positions are never erased.
;;; There is only one classical context; no graph75 observations are imported.
(define-function sq-sequent (left right) (list 'sequent 'classical-prop-v1 left right))
(define-function sq-left (s) (dlm-nth s 2))
(define-function sq-right (s) (dlm-nth s 3))
(define-function sq-sequent? (s sig)
  (and (sq-shape? s 4) (= (car s) 'sequent) (= (dlm-nth s 1) 'classical-prop-v1)
       (sq-formulas? (sq-left s) sig) (sq-formulas? (sq-right s) sig)))
(define-function sq-index? (i xs)
  (and (is <long> i) (>= i 0) (< i (dlm-length xs))))
(define-function sq-remove (xs i)
  (if (= i 0) (cdr xs) (cons (car xs) (sq-remove (cdr xs) (- i 1)))))
(define-function sq-problem? (p)
  (and (sq-shape? p 4) (= (car p) 'problem) (= (dlm-nth p 1) 'classical-prop-v1)
       (sq-signature? (dlm-nth p 2)) (sq-sequent? (dlm-nth p 3) (dlm-nth p 2))))
;;; The full root + signature + profile is the context key; there is no cross-problem cache.
