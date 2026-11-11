;;; curve.l — sample-efficiency and ablation curve for the Maru-trained readout.
(define-function head-reset ()
  (set head-w (list (dt-zero 196) (dt-zero 196) (dt-zero 196) (dt-zero 196) (dt-zero 196)
                    (dt-zero 196) (dt-zero 196) (dt-zero 196) (dt-zero 196) (dt-zero 196)))
  (set head-b (list 0 0 0 0 0 0 0 0 0 0)))

(define-function head-train-n (n)
  (if (<= n 0) ()
    (begin (head-train-epoch pool-bits pool-labels) (head-train-n (- n 1)))))

(define-function head-eval-cases (c ok)
  (if (>= c 10) ok
    (let* ((bits (l-nth case-bits c))
           (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
           (pick (head-rule-score bits valid 0 -999999999 -1))
           (head (if (< pick 0) -1 (l-nth rule-heads pick)))
           (lab (string->number (car (l-nth *mnist-cases* c)))))
      (head-eval-cases (+ c 1) (if (= head lab) (+ ok 1) ok)))))

(define-function head-run-curve (n)
  (head-reset)
  (head-train-n n)
  (print "N " n " ACC " (head-eval-cases 0 0) "/10\n"))

;; no-mask ablation: score every rule, ignore unifier validity
(define-function all-rule-pick (bits i best bk)
  (if (< i 218)
      (let ((sc (l-nth (head-scores bits) (l-nth rule-heads i))))
        (if (> sc best) (all-rule-pick bits (+ i 1) sc i)
            (all-rule-pick bits (+ i 1) best bk)))
      bk))

(define-function head-eval-nomask (c ok valid)
  (if (>= c 10) (list ok valid)
    (let* ((bits (l-nth case-bits c))
           (pick (all-rule-pick bits 0 -999999999 -1))
           (head (l-nth rule-heads pick))
           (lab (string->number (car (l-nth *mnist-cases* c))))
           (ok? (dt-body-ok bits (l-nth rule-bodies pick))))
      (head-eval-nomask (+ c 1)
        (if (= head lab) (+ ok 1) ok)
        (if ok? (+ valid 1) valid)))))

(head-run-curve 1)
(head-run-curve 3)
(head-run-curve 5)
(head-run-curve 10)
(let ((r (head-eval-nomask 0 0 0))) (print "NOMASK-10 ACC " (car r) "/10 VALID " (car (cdr r)) "/10\n"))
