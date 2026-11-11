;;; rulelearn.l — LOCO structured perceptron for hard-binding rule tokens.
(define rule-w (dt-zero 16))
(define current-test 0)

(define-function qdot (w x)
  (if w (+ (fx-mul (car w) (car x)) (qdot (cdr w) (cdr x))) 0))

(define-function rule-scores (bits valid)
  (if valid
      (cons (qdot rule-w (dt-rule-features bits (l-nth rule-heads (car valid))
                                            (l-nth rule-bodies (car valid))))
            (rule-scores bits (cdr valid)))
      ()))

(define-function rule-argmax (xs i best bi)
  (if xs
      (if (> (car xs) best)
          (rule-argmax (cdr xs) (+ i 1) (car xs) i)
          (rule-argmax (cdr xs) (+ i 1) best bi))
      bi))

(define-function rule-pick (bits valid)
  (let ((ss (rule-scores bits valid)))
    (l-nth valid (rule-argmax ss 0 -999999999 0))))

(define-function rule-correct (valid label)
  (if valid
      (if (= (l-nth rule-heads (car valid)) label) (car valid)
          (rule-correct (cdr valid) label))
      -1))

(define-function rule-update (a b)
  (if a (cons (+ (car a) (car b)) (rule-update (cdr a) (cdr b))) ()))

(define-function rule-train-case (c label)
  (let* ((bits (l-nth case-bits c))
         (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
         (pick (rule-pick bits valid))
         (good (rule-correct valid label)))
    (if (and (>= good 0) (not (= pick good)))
        (let* ((fp (dt-rule-features bits (l-nth rule-heads pick) (l-nth rule-bodies pick)))
               (fg (dt-rule-features bits (l-nth rule-heads good) (l-nth rule-bodies good))))
          (set rule-w (rule-update rule-w (map - fg fp)))))))

(define-function rule-train-epoch (cases c)
  (if (< c 10)
      (begin
        (if (not (= c current-test))
            (rule-train-case c (string->number (car (l-nth *mnist-cases* c)))))
        (rule-train-epoch cases (+ c 1)))
      ()))

(define-function rule-train (epochs)
  (if (<= epochs 0) ()
    (begin (rule-train-epoch 0 0) (rule-train (- epochs 1)))))

(define-function rule-eval-case (c)
  (let* ((bits (l-nth case-bits c))
         (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
         (pick (rule-pick bits valid))
         (head (if (< pick 0) -1 (l-nth rule-heads pick)))
         (lab (string->number (car (l-nth *mnist-cases* c)))))
    (if (= head lab) 1 0)))

(define-function rule-loco (c ok)
  (if (>= c 10) ok
    (begin
      (set current-test c)
      (set rule-w (dt-zero 16))
      (rule-train 20)
      (rule-loco (+ c 1) (+ ok (rule-eval-case c))))))

(print "RULE-LOCO " (rule-loco 0 0) "/10\n")
