;;; learn.l — Maru-native perceptron training for the head readout of a
;;; hard-binding deductive transformer. No gradients, no Python.

(define head-w (list (dt-zero 196) (dt-zero 196) (dt-zero 196) (dt-zero 196) (dt-zero 196)
                     (dt-zero 196) (dt-zero 196) (dt-zero 196) (dt-zero 196) (dt-zero 196)))
(define head-b (list 0 0 0 0 0 0 0 0 0 0))


(define-function lset (xs i v)
  (if (= i 0) (cons v (cdr xs))
      (cons (car xs) (lset (cdr xs) (- i 1) v))))

(define-function dot01 (w x)
  (if w (+ (* (car w) (car x)) (dot01 (cdr w) (cdr x))) 0))

(define-function add01 (w x)
  (if w (cons (+ (car w) (car x)) (add01 (cdr w) (cdr x))) ()))

(define-function sub01 (w x)
  (if w (cons (- (car w) (car x)) (sub01 (cdr w) (cdr x))) ()))

(define-function head-scores (bits)
  (let ((out ()) (i 0))
    (while (< i 10)
      (set out (l-append out (list (+ (dot01 (l-nth head-w i) bits)
                                      (l-nth head-b i)))))
      (set i (+ i 1)))
    out))

(define-function score-argmax (xs i best bi)
  (if xs
      (if (> (car xs) best)
          (score-argmax (cdr xs) (+ i 1) (car xs) i)
          (score-argmax (cdr xs) (+ i 1) best bi))
      bi))

(define-function head-pred (bits) (score-argmax (head-scores bits) 0 -999999999 0))

(define-function head-train-one (bits label)
  (let* ((s (head-scores bits))
         (pred (score-argmax s 0 -999999999 0)))
    (if (not (= pred label))
        (begin
          (set head-w (lset head-w label (add01 (l-nth head-w label) bits)))
          (set head-b (lset head-b label (+ 1 (l-nth head-b label))))
          (set head-w (lset head-w pred (sub01 (l-nth head-w pred) bits)))
          (set head-b (lset head-b pred (- (l-nth head-b pred) 1)))))
    (if (= pred label) 1 0)))

(define-function head-train-epoch (imgs labels)
  (if imgs
      (+ (head-train-one (car imgs) (car labels))
         (head-train-epoch (cdr imgs) (cdr labels)))
      0))

(define-function head-train (n)
  (if (<= n 0) ()
    (let ((ok (head-train-epoch pool-bits pool-labels)))
      (print "EPOCH " n " TRAIN-ACC " ok "/" (list-length pool-labels) "\n")
      (head-train (- n 1)))))

;;; ---------- inference: hard-binding rule mask + head readout + proof ----------
(define-function head-rule-score (bits valid i best bk)
  (if valid
      (let* ((k (car valid)) (h (l-nth rule-heads k))
             (sc (l-nth (head-scores bits) h)))
        (if (> sc best)
            (head-rule-score bits (cdr valid) (+ i 1) sc k)
            (head-rule-score bits (cdr valid) (+ i 1) best bk)))
      bk))

(define-function head-run-case (c)
  (let* ((bits (l-nth case-bits c))
         (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
         (pick (head-rule-score bits valid 0 -999999999 -1))
         (head (if (< pick 0) -1 (l-nth rule-heads pick)))
         (facts (l-nth (l-nth *mnist-cases* c) 1))
         (goal (l-atom 'digit (list (number->string head))))
         (pr (if (< head 0) () (p-prove facts rules218 goal 50000)))
         (pok (if (and pr (equal (l-nth pr 1) 'proof))
                  (if (p-proof-check facts rules218 goal (l-nth pr 2)) 1 0) 0)))
    (print "CASE " c " IMG " (head-pred bits) " VALID " valid
           " PICK " pick " HEAD " head " LABEL " (car (l-nth *mnist-cases* c))
           " PROOF " pok "\n")))

(define-function head-run (c)
  (if (< c 10) (begin (head-run-case c) (head-run (+ c 1))) ()))
