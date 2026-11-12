;;; dt.l — native Maru inference for a mask-compact deductive transformer.
;;; Tokens = image + unifier-valid rules; attention runs only over valid tokens.
;;; Training is external (PyTorch); weights are Q16.

(define sqrt-d-model 370728) ; sqrt(32) * 65536

(define-function dt-zero (n)
  (if (<= n 0) () (cons 0 (dt-zero (- n 1)))))

(define-function dt-seq-map (f xs)
  (if xs (cons (f (car xs)) (dt-seq-map f (cdr xs))) ()))

(define-function dt-seq-add (a b)
  (if a (cons (v-add (car a) (car b)) (dt-seq-add (cdr a) (cdr b))) ()))

(define-function dt-ln-seq (x g b)
  (if x (cons (layernorm (car x) g b) (dt-ln-seq (cdr x) g b)) ()))

(define-function dt-project (xs w b)
  (dt-seq-map (lambda (x) (v-add (mat-vec w x) b)) xs))

(define-function dt-vrelu (v)
  (map (lambda (x) (if (> x 0) x 0)) v))

(define-function dt-relu-seq (x)
  (if x (cons (dt-vrelu (car x)) (dt-relu-seq (cdr x))) ()))

(define-function dt-prefix (xs n)
  (if (<= n 0) () (cons (car xs) (dt-prefix (cdr xs) (- n 1)))))

(define-function dt-slice (xs start n)
  (dt-prefix (if (<= start 0) xs (dt-slice (cdr xs) (- start 1) n)) n))

(define-function dt-softmax (scores) (v-softmax scores))

(define-function dt-score-row (q ks)
  (dt-seq-map (lambda (k) (fx-div (v-dot q k) sqrt-d-model)) ks))

(define-function dt-wsum (ws vs zero)
  (if ws
      (v-add (v-scale (car vs) (car ws)) (dt-wsum (cdr ws) (cdr vs) zero))
      zero))

(define-function dt-attend (q k v)
  (let ((zero (dt-zero (list-length (car v)))))
    (dt-seq-map (lambda (qi)
                  (let ((w (v-softmax (dt-score-row qi k))))
                    (dt-wsum w v zero)))
                q)))

(define-function dt-mha (tokens inw inb outw outb)
  (let* ((wq (dt-slice inw 0 32))
         (wk (dt-slice inw 32 32))
         (wv (dt-slice inw 64 32))
         (bq (dt-slice inb 0 32))
         (bk (dt-slice inb 32 32))
         (bv (dt-slice inb 64 32))
         (q (dt-project tokens wq bq))
         (k (dt-project tokens wk bk))
         (v (dt-project tokens wv bv))
         (a (dt-attend q k v)))
    (dt-project a outw outb)))

(define-function dt-block (tokens m)
  (let* ((inw (l-nth m 4)) (inb (l-nth m 5))
         (ow (l-nth m 6)) (ob (l-nth m 7))
         (l1w (l-nth m 8)) (l1b (l-nth m 9))
         (l2w (l-nth m 10)) (l2b (l-nth m 11))
         (n1g (l-nth m 12)) (n1b (l-nth m 13))
         (n2g (l-nth m 14)) (n2b (l-nth m 15))
         (a (dt-mha tokens inw inb ow ob))
         (x1 (dt-ln-seq (dt-seq-add tokens a) n1g n1b))
         (f1 (dt-project x1 l1w l1b))
         (f2 (dt-project (dt-relu-seq f1) l2w l2b))
         (x2 (dt-ln-seq (dt-seq-add x1 f2) n2g n2b)))
    x2))

(define-function dt-loops (tokens m n)
  (if (<= n 0) tokens (dt-loops (dt-block tokens m) m (- n 1))))

(define-function dt-out-token (x w b)
  (+ (v-dot w x) b))

;;; ---------- rule features / validity ----------
(define-function dt-count-on (codes)
  (if codes (if (> (car codes) 0) (+ 1 (dt-count-on (cdr codes))) (dt-count-on (cdr codes))) 0))

(define-function dt-count-idx (codes)
  (if codes (+ (if (> (car codes) 0) (- (car codes) 1) (- (- (car codes)) 1))
               (dt-count-idx (cdr codes))) 0))

(define-function dt-body-ok (bits codes)
  (if codes
      (let ((code (car codes)))
        (let ((idx (if (> code 0) (- code 1) (- (- code) 1)))
              (want (if (> code 0) 1 0)))
          (and (= (l-nth bits idx) want) (dt-body-ok bits (cdr codes)))))
      (not ())))

(define-function dt-sat (bits codes)
  (if codes
      (+ (if (dt-body-ok bits (list (car codes))) 65536 0) (dt-sat bits (cdr codes)))
      0))

(define-function dt-rule-features (bits head codes)
  (let* ((n (list-length codes))
         (on (dt-count-on codes))
         (off (- n on))
         (si (dt-count-idx codes))
         (sat (/ (dt-sat bits codes) n)))
    (l-append
      (dt-seq-map (lambda (k) (if (= k head) 65536 0)) (list 0 1 2 3 4 5 6 7 8 9))
      (list (fx-div (if (> n 30) 30 n) 30)
            (fx-div on n)
            (fx-div off n)
            (fx-div si (* 196 n))
            sat
            (- 65536 sat)))))

;;; ---------- kNN head prior ----------
(define-function dt-dist (a b)
  (if a (let ((d (- (car a) (car b)))) (+ (* d d) (dt-dist (cdr a) (cdr b)))) 0))

(define-function dt-insert (e xs)
  (if xs
      (if (<= (car e) (car (car xs)))
          (cons e xs)
          (cons (car xs) (dt-insert e (cdr xs))))
      (list e)))

(define-function dt-take (xs n)
  (if (or (<= n 0) (not xs)) () (cons (car xs) (dt-take (cdr xs) (- n 1)))))

(define-function dt-knn-loop (bits pool labels i top)
  (if pool
      (dt-knn-loop bits (cdr pool) (cdr labels) (+ i 1)
                   (dt-take (dt-insert (list (dt-dist bits (car pool)) (car labels)) top) 5))
      top))

(define-function dt-count-label (lab top)
  (if top (if (= lab (car (cdr (car top)))) (+ 1 (dt-count-label lab (cdr top))) (dt-count-label lab (cdr top))) 0))

;;; ---------- pipeline ----------
(define-function dt-valid-rules (bits i heads bodies out)
  (if bodies
      (dt-valid-rules bits (+ i 1) (cdr heads) (cdr bodies)
        (if (dt-body-ok bits (car bodies)) (l-append out (list i)) out))
      out))

(define-function dt-selector-scores (bits valid model)
  (let* ((imgq (dt-seq-map (lambda (b) (* b 65536)) bits))
         (itok (v-add (mat-vec (l-nth model 0) imgq) (l-nth model 1)))
         (rtoks (dt-seq-map
                  (lambda (k) (v-add (mat-vec (l-nth model 2)
                                              (dt-rule-features bits (l-nth rule-heads k) (l-nth rule-bodies k)))
                                     (l-nth model 3)))
                  valid))
         (tokens (cons itok rtoks))
         (h (dt-loops tokens model 6))
         (rule-h (cdr h))
         (ow (l-nth model 16)) (ob (l-nth model 17)))
    (dt-seq-map (lambda (x) (dt-out-token x ow ob)) rule-h)))

(define-function dt-score-step (valid scores bits top i best bestk)
  (if valid
      (let* ((k (car valid))
             (cnt (dt-count-label (l-nth rule-heads k) top))
             (prior (l-nth prior-log cnt))
             (score (+ (car scores) (* 8 prior))))
        (if (> score best)
            (dt-score-step (cdr valid) (cdr scores) bits top (+ i 1) score k)
            (dt-score-step (cdr valid) (cdr scores) bits top (+ i 1) best bestk)))
      bestk))

(define-function dt-pick-scores (bits valid scores)
  (let ((top (dt-knn-loop bits pool-bits pool-labels 0 ())))
    (dt-score-step valid scores bits top 0 -999999999 -1)))

(define-function dt-pick (bits valid model)
  (dt-pick-scores bits valid (dt-selector-scores bits valid model)))

(define-function dt-pick-head (bits valid model)
  (let ((k (dt-pick bits valid model)))
    (if (< k 0) -1 (l-nth rule-heads k))))
