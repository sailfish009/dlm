;;; dump.l — print Q16 encoder activations and first-step logits for all cases.
(define-function tt-print-ints (xs)
  (if xs (begin (print (car xs)) (print " ") (tt-print-ints (cdr xs))) ()))

(define-function tt-print-matrix (rows)
  (if rows
      (begin (tt-print-ints (car rows)) (print "\n") (tt-print-matrix (cdr rows)))
      ()))

(define-function tt-dump-case (ids idx)
  (let* ((enc (tt-encode (tt-embed-seq ids
             w-source-embedding-embedding-weight
             w-source-embedding-position-pe 0)))
         (x (tt-embed-seq (list bos-id)
             w-target-embedding-embedding-weight
             w-target-embedding-position-pe 0))
         (h (tt-decoder x enc))
         (logits (tt-last (tt-logits h))))
    (print "ENC " idx "\n")
    (tt-print-matrix enc)
    (print "LOGITS " idx "\n")
    (tt-print-ints logits)
    (print "\n")))

(define-function tt-dump-all (ids idx)
  (if ids
      (begin (tt-dump-case (car ids) idx)
             (tt-dump-all (cdr ids) (+ idx 1)))
      ()))

(tt-dump-all case-ids 0)
