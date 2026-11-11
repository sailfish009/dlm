;;; transformer.l — Q16 inference for the tiny encoder-decoder transformer.

(define sqrt-d 370728) ; sqrt(32) * 65536

;;; ---------- embeddings ----------
(define-function tt-seq-add (a b)
  (if a (cons (v-add (car a) (car b)) (tt-seq-add (cdr a) (cdr b))) ()))

(define-function tt-embed (id table pe pos)
  (v-add (v-scale (l-nth table id) sqrt-d) (l-nth pe pos)))

(define-function tt-embed-seq (ids table pe pos)
  (if ids
      (cons (tt-embed (car ids) table pe pos)
            (tt-embed-seq (cdr ids) table pe (+ pos 1)))
      ()))

;;; ---------- attention ----------
(define-function tt-score-row (q ks)
  (map (lambda (k) (/ (v-dot q k) 4)) ks))

(define-function tt-mask-row (row j i)
  (if row
      (cons (if (> j i) -6553600 (car row))
            (tt-mask-row (cdr row) (+ j 1) i))
      ()))

(define-function tt-causal (rows i)
  (if rows
      (cons (tt-mask-row (car rows) 0 i)
            (tt-causal (cdr rows) (+ i 1)))
      ()))

(define-function tt-zero-like (v) (map (lambda (x) 0) v))

(define-function tt-wsum (ws vs zero)
  (if ws
      (v-add (v-scale (car vs) (car ws))
             (tt-wsum (cdr ws) (cdr vs) zero))
      zero))

(define-function tt-score-rows (q k)
  (if q (cons (tt-score-row (car q) k) (tt-score-rows (cdr q) k)) ()))

(define-function tt-softmax-seq (rows)
  (if rows (cons (v-softmax (car rows)) (tt-softmax-seq (cdr rows))) ()))

(define-function tt-attend-out (ws v zero)
  (if ws (cons (tt-wsum (car ws) v zero) (tt-attend-out (cdr ws) v zero)) ()))

(define-function tt-attend (q k v causal)
  (let* ((rows (tt-score-rows q k))
         (rows2 (if causal (tt-causal rows 0) rows))
         (ws (tt-softmax-seq rows2))
         (zero (tt-zero-like (car v))))
    (tt-attend-out ws v zero)))

(define-function tt-project (x w b)
  (if x (cons (v-add (mat-vec w (car x)) b) (tt-project (cdr x) w b)) ()))

(define-function tt-head (xq xk xv wq bq wk bk wv bv causal)
  (let* ((q (tt-project xq wq bq))
         (k (tt-project xk wk bk))
         (v (tt-project xv wv bv)))
    (tt-attend q k v causal)))

(define-function tt-pair-vecs (a b)
  (if a (cons (l-append (car a) (car b)) (tt-pair-vecs (cdr a) (cdr b))) ()))

(define-function tt-mha
  (xq xk xv
   wq0 bq0 wk0 bk0 wv0 bv0
   wq1 bq1 wk1 bk1 wv1 bv1
   wo bo causal)
  (let* ((h0 (tt-head xq xk xv wq0 bq0 wk0 bk0 wv0 bv0 causal))
         (h1 (tt-head xq xk xv wq1 bq1 wk1 bk1 wv1 bv1 causal))
         (joined (tt-pair-vecs h0 h1)))
    (tt-project joined wo bo)))

;;; ---------- feed-forward ----------
(define-function tt-relu (v) (map (lambda (x) (if (> x 0) x 0)) v))

(define-function tt-ffn (x w1 b1 w2 b2)
  (let ((h (v-add (mat-vec w1 x) b1)))
    (v-add (mat-vec w2 (tt-relu h)) b2)))

(define-function tt-ffn-seq (x w1 b1 w2 b2)
  (if x (cons (tt-ffn (car x) w1 b1 w2 b2)
              (tt-ffn-seq (cdr x) w1 b1 w2 b2)) ()))

(define-function tt-ln-seq (x g b)
  (if x (cons (layernorm (car x) g b)
              (tt-ln-seq (cdr x) g b)) ()))

;;; ---------- encoder ----------
(define-function tt-enc-layer
  (x
   wq0 bq0 wk0 bk0 wv0 bv0 wq1 bq1 wk1 bk1 wv1 bv1 wo bo
   f1 fb1 f2 fb2 n1g n1b n2g n2b)
  (let* ((a (tt-mha x x x
                    wq0 bq0 wk0 bk0 wv0 bv0
                    wq1 bq1 wk1 bk1 wv1 bv1 wo bo ()))
         (x1 (tt-ln-seq (tt-seq-add x a) n1g n1b))
         (f (tt-ffn-seq x1 f1 fb1 f2 fb2)))
    (tt-ln-seq (tt-seq-add x1 f) n2g n2b)))

(define-function tt-encode (x)
  (let* ((l0 (tt-enc-layer x
        w-encoder-layers-0-self-mha-heads-0-q-proj-weight
        w-encoder-layers-0-self-mha-heads-0-q-proj-bias
        w-encoder-layers-0-self-mha-heads-0-k-proj-weight
        w-encoder-layers-0-self-mha-heads-0-k-proj-bias
        w-encoder-layers-0-self-mha-heads-0-v-proj-weight
        w-encoder-layers-0-self-mha-heads-0-v-proj-bias
        w-encoder-layers-0-self-mha-heads-1-q-proj-weight
        w-encoder-layers-0-self-mha-heads-1-q-proj-bias
        w-encoder-layers-0-self-mha-heads-1-k-proj-weight
        w-encoder-layers-0-self-mha-heads-1-k-proj-bias
        w-encoder-layers-0-self-mha-heads-1-v-proj-weight
        w-encoder-layers-0-self-mha-heads-1-v-proj-bias
        w-encoder-layers-0-self-mha-out-proj-weight
        w-encoder-layers-0-self-mha-out-proj-bias
        w-encoder-layers-0-ffn-network-0-weight
        w-encoder-layers-0-ffn-network-0-bias
        w-encoder-layers-0-ffn-network-2-weight
        w-encoder-layers-0-ffn-network-2-bias
        w-encoder-layers-0-norm1-weight
        w-encoder-layers-0-norm1-bias
        w-encoder-layers-0-norm2-weight
        w-encoder-layers-0-norm2-bias))
         (l1 (tt-enc-layer l0
        w-encoder-layers-1-self-mha-heads-0-q-proj-weight
        w-encoder-layers-1-self-mha-heads-0-q-proj-bias
        w-encoder-layers-1-self-mha-heads-0-k-proj-weight
        w-encoder-layers-1-self-mha-heads-0-k-proj-bias
        w-encoder-layers-1-self-mha-heads-0-v-proj-weight
        w-encoder-layers-1-self-mha-heads-0-v-proj-bias
        w-encoder-layers-1-self-mha-heads-1-q-proj-weight
        w-encoder-layers-1-self-mha-heads-1-q-proj-bias
        w-encoder-layers-1-self-mha-heads-1-k-proj-weight
        w-encoder-layers-1-self-mha-heads-1-k-proj-bias
        w-encoder-layers-1-self-mha-heads-1-v-proj-weight
        w-encoder-layers-1-self-mha-heads-1-v-proj-bias
        w-encoder-layers-1-self-mha-out-proj-weight
        w-encoder-layers-1-self-mha-out-proj-bias
        w-encoder-layers-1-ffn-network-0-weight
        w-encoder-layers-1-ffn-network-0-bias
        w-encoder-layers-1-ffn-network-2-weight
        w-encoder-layers-1-ffn-network-2-bias
        w-encoder-layers-1-norm1-weight
        w-encoder-layers-1-norm1-bias
        w-encoder-layers-1-norm2-weight
        w-encoder-layers-1-norm2-bias)))
    l1))

;;; ---------- decoder ----------
(define-function tt-dec-layer
  (x enc
   sq0 sbq0 sk0 sbk0 sv0 sbv0 sq1 sbq1 sk1 sbk1 sv1 sbv1 so sbo
   cq0 cbq0 ck0 cbk0 cv0 cbv0 cq1 cbq1 ck1 cbk1 cv1 cbv1 co cbo
   f1 fb1 f2 fb2 n1g n1b n2g n2b n3g n3b)
  (let* ((a (tt-mha x x x
                    sq0 sbq0 sk0 sbk0 sv0 sbv0
                    sq1 sbq1 sk1 sbk1 sv1 sbv1 so sbo (not ())))
         (x1 (tt-ln-seq (tt-seq-add x a) n1g n1b))
         (b (tt-mha x1 enc enc
                    cq0 cbq0 ck0 cbk0 cv0 cbv0
                    cq1 cbq1 ck1 cbk1 cv1 cbv1 co cbo ()))
         (x2 (tt-ln-seq (tt-seq-add x1 b) n2g n2b))
         (f (tt-ffn-seq x2 f1 fb1 f2 fb2)))
    (tt-ln-seq (tt-seq-add x2 f) n3g n3b)))

(define-function tt-decoder (x enc)
  (let* ((l0 (tt-dec-layer x enc
        w-decoder-layers-0-self-attn-heads-0-q-proj-weight
        w-decoder-layers-0-self-attn-heads-0-q-proj-bias
        w-decoder-layers-0-self-attn-heads-0-k-proj-weight
        w-decoder-layers-0-self-attn-heads-0-k-proj-bias
        w-decoder-layers-0-self-attn-heads-0-v-proj-weight
        w-decoder-layers-0-self-attn-heads-0-v-proj-bias
        w-decoder-layers-0-self-attn-heads-1-q-proj-weight
        w-decoder-layers-0-self-attn-heads-1-q-proj-bias
        w-decoder-layers-0-self-attn-heads-1-k-proj-weight
        w-decoder-layers-0-self-attn-heads-1-k-proj-bias
        w-decoder-layers-0-self-attn-heads-1-v-proj-weight
        w-decoder-layers-0-self-attn-heads-1-v-proj-bias
        w-decoder-layers-0-self-attn-out-proj-weight
        w-decoder-layers-0-self-attn-out-proj-bias
        w-decoder-layers-0-cross-attn-heads-0-q-proj-weight
        w-decoder-layers-0-cross-attn-heads-0-q-proj-bias
        w-decoder-layers-0-cross-attn-heads-0-k-proj-weight
        w-decoder-layers-0-cross-attn-heads-0-k-proj-bias
        w-decoder-layers-0-cross-attn-heads-0-v-proj-weight
        w-decoder-layers-0-cross-attn-heads-0-v-proj-bias
        w-decoder-layers-0-cross-attn-heads-1-q-proj-weight
        w-decoder-layers-0-cross-attn-heads-1-q-proj-bias
        w-decoder-layers-0-cross-attn-heads-1-k-proj-weight
        w-decoder-layers-0-cross-attn-heads-1-k-proj-bias
        w-decoder-layers-0-cross-attn-heads-1-v-proj-weight
        w-decoder-layers-0-cross-attn-heads-1-v-proj-bias
        w-decoder-layers-0-cross-attn-out-proj-weight
        w-decoder-layers-0-cross-attn-out-proj-bias
        w-decoder-layers-0-ffn-network-0-weight
        w-decoder-layers-0-ffn-network-0-bias
        w-decoder-layers-0-ffn-network-2-weight
        w-decoder-layers-0-ffn-network-2-bias
        w-decoder-layers-0-norm1-weight
        w-decoder-layers-0-norm1-bias
        w-decoder-layers-0-norm2-weight
        w-decoder-layers-0-norm2-bias
        w-decoder-layers-0-norm3-weight
        w-decoder-layers-0-norm3-bias))
         (l1 (tt-dec-layer l0 enc
        w-decoder-layers-1-self-attn-heads-0-q-proj-weight
        w-decoder-layers-1-self-attn-heads-0-q-proj-bias
        w-decoder-layers-1-self-attn-heads-0-k-proj-weight
        w-decoder-layers-1-self-attn-heads-0-k-proj-bias
        w-decoder-layers-1-self-attn-heads-0-v-proj-weight
        w-decoder-layers-1-self-attn-heads-0-v-proj-bias
        w-decoder-layers-1-self-attn-heads-1-q-proj-weight
        w-decoder-layers-1-self-attn-heads-1-q-proj-bias
        w-decoder-layers-1-self-attn-heads-1-k-proj-weight
        w-decoder-layers-1-self-attn-heads-1-k-proj-bias
        w-decoder-layers-1-self-attn-heads-1-v-proj-weight
        w-decoder-layers-1-self-attn-heads-1-v-proj-bias
        w-decoder-layers-1-self-attn-out-proj-weight
        w-decoder-layers-1-self-attn-out-proj-bias
        w-decoder-layers-1-cross-attn-heads-0-q-proj-weight
        w-decoder-layers-1-cross-attn-heads-0-q-proj-bias
        w-decoder-layers-1-cross-attn-heads-0-k-proj-weight
        w-decoder-layers-1-cross-attn-heads-0-k-proj-bias
        w-decoder-layers-1-cross-attn-heads-0-v-proj-weight
        w-decoder-layers-1-cross-attn-heads-0-v-proj-bias
        w-decoder-layers-1-cross-attn-heads-1-q-proj-weight
        w-decoder-layers-1-cross-attn-heads-1-q-proj-bias
        w-decoder-layers-1-cross-attn-heads-1-k-proj-weight
        w-decoder-layers-1-cross-attn-heads-1-k-proj-bias
        w-decoder-layers-1-cross-attn-heads-1-v-proj-weight
        w-decoder-layers-1-cross-attn-heads-1-v-proj-bias
        w-decoder-layers-1-cross-attn-out-proj-weight
        w-decoder-layers-1-cross-attn-out-proj-bias
        w-decoder-layers-1-ffn-network-0-weight
        w-decoder-layers-1-ffn-network-0-bias
        w-decoder-layers-1-ffn-network-2-weight
        w-decoder-layers-1-ffn-network-2-bias
        w-decoder-layers-1-norm1-weight
        w-decoder-layers-1-norm1-bias
        w-decoder-layers-1-norm2-weight
        w-decoder-layers-1-norm2-bias
        w-decoder-layers-1-norm3-weight
        w-decoder-layers-1-norm3-bias)))
    l1))

;;; ---------- output / greedy ----------
(define-function tt-logits (h)
  (if h (cons (v-add (mat-vec w-output-projection-weight (car h))
                     w-output-projection-bias)
              (tt-logits (cdr h)))
      ()))

(define-function tt-argmax (xs best bi)
  (if xs
      (if (> (car xs) best)
          (tt-argmax (cdr xs) (car xs) bi)
          (tt-argmax (cdr xs) best (+ bi 1)))
      0))

(define-function tt-argmax-from (xs i best bi)
  (if xs
      (if (> (car xs) best)
          (tt-argmax-from (cdr xs) (+ i 1) (car xs) i)
          (tt-argmax-from (cdr xs) (+ i 1) best bi))
      bi))

(define-function tt-last (xs)
  (if (cdr xs) (tt-last (cdr xs)) (car xs)))

(define-function tt-decode-step (prefix enc)
  (let* ((x (tt-embed-seq prefix w-target-embedding-embedding-weight
                          w-target-embedding-position-pe 0))
         (h (tt-decoder x enc))
         (logits (tt-logits h))
         (last (tt-last logits)))
    (tt-argmax-from last 0 -999999999 0)))

(define-function tt-greedy (prefix enc steps)
  (if (<= steps 0) prefix
    (let ((id (tt-decode-step prefix enc)))
      (if (= id eos-id) prefix
        (tt-greedy (l-append prefix (list id)) enc (- steps 1))))))

(define-function tt-translate-ids (ids)
  (let ((enc (tt-encode (tt-embed-seq ids w-source-embedding-embedding-weight
                                      w-source-embedding-position-pe 0))))
    (tt-greedy (list bos-id) enc 16)))

(define-function tt-total-len (ws)
  (if ws (+ (string-length (car ws)) (tt-total-len (cdr ws))) 0))

(define-function tt-join (ws)
  (let ((out (string (tt-total-len ws))) (i 0))
    (while ws
      (let ((w (car ws)) (j 0))
        (while (< j (string-length w))
          (set-string-at out i (string-at w j))
          (set i (+ i 1))
          (set j (+ j 1))))
      (set ws (cdr ws)))
    out))

(define-function tt-words (ids)
  (if ids (cons (l-nth target-words (car ids)) (tt-words (cdr ids))) ()))

(define-function tt-translate (ids)
  (tt-join (tt-words (cdr (tt-translate-ids ids)))))
