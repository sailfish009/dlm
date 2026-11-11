;;; synth_eval.l — coverage/conflict evaluation of image-specific synthesized rules.
;;; Rule: head h :- first K on-bits of the source image.

(define-function take-on (bits i k)
  (if (or (>= i 196) (<= k 0)) ()
      (if (= (l-nth bits i) 1)
          (cons i (take-on bits (+ i 1) (- k 1)))
          (take-on bits (+ i 1) k))))

(define-function on-atoms (idx)
  (if idx (cons (l-atom 'on (list (number->string (car idx))))
                (on-atoms (cdr idx)))
      ()))

(define-function synth-rule (bits head k)
  (l-rule (l-atom 'digit (list (number->string head)))
          (on-atoms (take-on bits 0 k))))

(define-function eval-rule (body j s-head cover conflict)
  (if (>= j 10) (list cover conflict)
      (let* ((bits (l-nth case-bits j))
             (lab (string->number (car (l-nth *mnist-cases* j)))))
        (if (dt-body-ok bits (map (lambda (i) (+ i 1)) body))
            (eval-rule body (+ j 1) s-head (+ cover 1)
                       (if (= s-head lab) conflict (+ conflict 1)))
            (eval-rule body (+ j 1) s-head cover conflict)))))

(define-function synth-eval-k (k s cover conflict)
  (if (>= s 10) (list cover conflict)
      (let* ((bits (l-nth case-bits s))
             (h (head-pred bits))
             (body (take-on bits 0 k))
             (r (eval-rule body 0 h 0 0)))
        (synth-eval-k k (+ s 1) (+ cover (car r)) (+ conflict (car (cdr r)))))))

(define-function synth-eval-all (s correct)
  (if (>= s 10) correct
      (let* ((bits (l-nth case-bits s))
             (h (head-pred bits))
             (lab (string->number (car (l-nth *mnist-cases* s)))))
        (synth-eval-all (+ s 1) (if (= h lab) (+ correct 1) correct)))))

(head-train 10)
(print "ALWAYS-SYNTH ACC " (synth-eval-all 0 0) "/10\n")
(list-do k (list 1 3 5 10 20 40 196)
  (let ((r (synth-eval-k k 0 0 0)))
    (print "K " k " COVER " (car r) " CONFLICT " (car (cdr r)) "\n")))
