;;; library_split.l — E06: synthesize on 150 pool images, validate on held-out 40.
;;; Candidate: head_pred(image) :- first K on-bits of a training image.
;;; Accept iff validation coverage >= 2 and precision >= 0.8.

(define-function ls-take-on (bits i k)
  (if (or (>= i 196) (<= k 0)) ()
      (if (= (l-nth bits i) 1)
          (cons i (ls-take-on bits (+ i 1) (- k 1)))
          (ls-take-on bits (+ i 1) k))))

(define-function ls-match? (bits body)
  (if body (if (= (l-nth bits (car body)) 1) (ls-match? bits (cdr body)) ()) (not ())))

;; range [start,end)
(define-function ls-count (body j end cover good)
  (if (>= j end) (list cover good)
      (let ((bits (l-nth pool-bits j)))
        (if (ls-match? bits body)
            (ls-count body (+ j 1) end (+ cover 1)
                      (if (= (head-pred bits) (l-nth pool-labels j)) (+ good 1) good))
            (ls-count body (+ j 1) end cover good)))))

(define-function ls-member? (h b lib)
  (if lib (if (and (= h (car (car lib))) (equal b (car (cdr (car lib))))) 1
             (ls-member? h b (cdr lib)))
      0))

(define-function ls-add-one (K i lib)
  (if (>= i 150) lib
      (let* ((bits (l-nth pool-bits i))
             (body (ls-take-on bits 0 K))
             (c (ls-count body 150 190 0 0))
             (cover (car c)) (good (car (cdr c))))
        (if (and (>= cover 2) (>= (* good 5) (* cover 4))
                 (= 0 (ls-member? (head-pred bits) body lib)))
            (ls-add-one K (+ i 1) (l-append lib (list (list (head-pred bits) body))))
            (ls-add-one K (+ i 1) lib)))))

(define-function ls-build (K) (ls-add-one K 0 ()))

(define-function ls-matches (bits lib out)
  (if lib
      (ls-matches bits (cdr lib)
                  (if (ls-match? bits (car (cdr (car lib))))
                      (l-append out (list (car (car lib))))
                      out))
      out))

(define-function ls-pick-head (bits valid lib)
  (let* ((hs (head-scores bits))
         (heads (l-append (dt-seq-map (lambda (k) (l-nth rule-heads k)) valid)
                          (ls-matches bits lib ()))))
    (if heads
        (let ((best (car heads)))
          (list-do h (cdr heads) (if (> (l-nth hs h) (l-nth hs best)) (set best h)))
          best)
        -1)))

(define-function ls-eval-case (c lib ok)
  (if (>= c 10) ok
      (let* ((bits (l-nth case-bits c))
             (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
             (h (ls-pick-head bits valid lib))
             (lab (string->number (car (l-nth *mnist-cases* c)))))
        (ls-eval-case (+ c 1) lib (if (= h lab) (+ ok 1) ok)))))

(define-function ls-atoms (idx)
  (if idx (cons (l-atom 'on (list (number->string (car idx)))) (ls-atoms (cdr idx))) ()))

(define-function ls-rules (lib)
  (if lib
      (cons (l-rule (l-atom 'digit (list (number->string (car (car lib)))))
                    (ls-atoms (car (cdr (car lib)))))
            (ls-rules (cdr lib)))
      ()))

(define-function ls-proof-case (c lib ok)
  (if (>= c 10) ok
      (let* ((bits (l-nth case-bits c))
             (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
             (h (ls-pick-head bits valid lib))
             (facts (l-nth (l-nth *mnist-cases* c) 1))
             (goal (l-atom 'digit (list (number->string h))))
             (rules2 (l-append rules218 (ls-rules lib)))
             (pr (p-prove facts rules2 goal 50000))
             (pok (if (and pr (equal (l-nth pr 1) 'proof))
                      (if (p-proof-check facts rules2 goal (l-nth pr 2)) 1 0) 0)))
        (ls-proof-case (+ c 1) lib (+ ok pok)))))

(define-function ls-eval-k (K)
  (let* ((lib (ls-build K)) (acc (ls-eval-case 0 lib 0)))
    (print "K " K " LIB " (list-length lib) " ACC " acc "/10\n")
    lib))

(head-train 10)
(ls-eval-k 1)
(ls-eval-k 3)
(define lib5 (ls-eval-k 5))
(ls-eval-k 10)
(ls-eval-k 20)
(print "K5-PROOF " (ls-proof-case 0 lib5 0) "/10\n")
