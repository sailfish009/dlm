;;; Discovery sees current visible execution tokens, not archived primitive words.
;;; Adjacent factors may be regrouped because join90 is associative composition.
;;; Support counts non-overlapping occurrences inside explicit training tasks.
(define-function b90-pair-count (a b tokens)
  (if (not (cdr tokens)) 0
    (if (and (equal a (car tokens)) (equal b (dlm-nth tokens 1)))
      (+ 1 (b90-pair-count a b (cdr (cdr tokens))))
      (b90-pair-count a b (cdr tokens)))))
(define-function b90-support (body tasks)
  (let ((n 0)) (list-do t tasks
    (set n (+ n (b90-pair-count (dlm-nth body 1) (dlm-nth body 2) (b90-tokens (dlm-nth t 3)))))) n))
(define-function b90-candidates (s)
  (let ((bodies ()) (out ()) (sig (dlm-nth s 2)) (lib (dlm-nth s 4)) (tasks (dlm-nth s 5)))
    (list-do t tasks
      (let ((tokens (b90-tokens (dlm-nth t 3))))
        (while (cdr tokens)
          (set bodies (dlm-add bodies (list 'join90 (car tokens) (dlm-nth tokens 1))))
          (set tokens (cdr tokens)))))
    (list-do body bodies
      (let ((word (b90-word body sig lib 16)) (count (b90-support body tasks)) (known false))
        (list-do m lib (if (equal word (dlm-nth m 3)) (set known true)))
        (if (and word (>= count 2) (not known))
          (set out (dlm-append out (list (list 'candidate90 body word count
            (- (* count 2) 3)))))))) out))
(define-function b90-propose (s)
  (if (>= (dlm-length (dlm-nth s 4)) 8) '(waiting90 basis-capacity)
    (let ((best ()) (score -100000))
      (list-do c (b90-candidates s)
        (if (> (dlm-nth c 4) score) (begin (set best c) (set score (dlm-nth c 4)))))
      (if (not best) '(waiting90 no-repeated-factor)
        (let* ((m (list 'basis90 (+ (dlm-length (dlm-nth s 4)) 1) (dlm-nth best 1) (dlm-nth best 2)))
               (lib (dlm-append (dlm-nth s 4) (list m))))
          (list 'learn90 m (b90-rewrites (dlm-nth s 5) (dlm-nth s 2) lib)))))))
