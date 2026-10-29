;;; Sparse symbolic routing. Eligibility is exact word-prefix matching.
;;; OR candidates: primitive token or a checked basis covering this prefix.
;;; Score: number of execution tokens, with stable primitive/older-basis ties.
;;; This is not neural attention, and scores never authorize a theorem.
(define-function b90-prefix? (prefix word)
  (or (not prefix) (and word (equal (car prefix) (car word)) (b90-prefix? (cdr prefix) (cdr word)))))
(define-function b90-drop (xs n) (if (= n 0) xs (b90-drop (cdr xs) (- n 1))))
(define-function b90-cover (word lib)
  (if (not word) ()
    (let ((best (cons (list 'rel90 (car word)) (b90-cover (cdr word) lib))))
      (list-do m lib
        (let ((w (dlm-nth m 3)))
          (if (b90-prefix? w word)
            (let ((candidate (cons (list 'use90 (dlm-nth m 1))
                              (b90-cover (b90-drop word (dlm-length w)) lib))))
              (if (< (dlm-length candidate) (dlm-length best)) (set best candidate)))))) best)))
(define-function b90-plan (original sig lib)
  (b90-expression (b90-cover (b90-word original sig () 8) lib)))
(define-function b90-rewrites (tasks sig lib)
  (let ((out ())) (list-do task tasks
    (set out (dlm-append out (list (list 'rewrite90 (dlm-nth task 1) (dlm-nth task 3)
      (b90-plan (dlm-nth task 2) sig lib)
      (list 'same-word90 (b90-word (dlm-nth task 2) sig () 8))))))) out))
(define-function b90-work-size (tasks)
  (let ((n 0)) (list-do t tasks (set n (+ n (b90-size (dlm-nth t 3))))) n))
(define-function b90-basis-size (lib)
  (let ((n 0)) (list-do m lib (set n (+ n (b90-size (dlm-nth m 2))))) n))
