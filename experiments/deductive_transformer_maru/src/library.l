;;; library.l — E05: validated synthesis of short image rules.
;;; Candidate: head_pred(image) :- first K on-bits.
;;; Accept iff it covers >=2 pool images and >=80% of covered images have
;;; the same label. Test on the 10 measured cases with the original 218 rules.

(define-function lib-take-on (bits i k)
  (if (or (>= i 196) (<= k 0)) ()
      (if (= (l-nth bits i) 1)
          (cons i (lib-take-on bits (+ i 1) (- k 1)))
          (lib-take-on bits (+ i 1) k))))

(define-function lib-match? (bits body)
  (if body (if (= (l-nth bits (car body)) 1) (lib-match? bits (cdr body)) ()) (not ())))

(define-function lib-count (body j cover good)
  (if (>= j 190) (list cover good)
      (let ((bits (l-nth pool-bits j)))
        (if (lib-match? bits body)
            (lib-count body (+ j 1) (+ cover 1)
                       (if (= (head-pred bits) (l-nth pool-labels j)) (+ good 1) good))
            (lib-count body (+ j 1) cover good)))))

(define-function lib-member? (h b lib)
  (if lib (if (and (= h (car (car lib))) (equal b (car (cdr (car lib))))) 1
             (lib-member? h b (cdr lib)))
      0))

(define-function lib-add-one (K i lib)
  (if (>= i 190) lib
      (let* ((bits (l-nth pool-bits i))
             (body (lib-take-on bits 0 K))
             (c (lib-count body 0 0 0))
             (cover (car c)) (good (car (cdr c))))
        (if (and (>= cover 2) (>= (* good 5) (* cover 4))
                 (= 0 (lib-member? (head-pred bits) body lib)))
            (lib-add-one K (+ i 1) (l-append lib (list (list (head-pred bits) body))))
            (lib-add-one K (+ i 1) lib)))))

(define-function lib-build (K) (lib-add-one K 0 ()))

(define-function lib-matches (bits lib out)
  (if lib
      (lib-matches bits (cdr lib)
                   (if (lib-match? bits (car (cdr (car lib))))
                       (l-append out (list (car (car lib))))
                       out))
      out))

(define-function lib-pick-head (bits valid lib best)
  (let* ((hs (head-scores bits))
         (heads (l-append (dt-seq-map (lambda (k) (l-nth rule-heads k)) valid)
                          (lib-matches bits lib ()))))
    (if heads
        (let ((h (car heads)) (rest (cdr heads)) (bs best))
          (if (> (l-nth hs h) (l-nth hs bs)) (set bs h))
          (list-do x rest (if (> (l-nth hs x) (l-nth hs bs)) (set bs x)))
          bs)
        -1)))

(define-function lib-eval-case (c lib ok)
  (if (>= c 10) ok
      (let* ((bits (l-nth case-bits c))
             (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
             (h (lib-pick-head bits valid lib 0))
             (lab (string->number (car (l-nth *mnist-cases* c)))))
        (lib-eval-case (+ c 1) lib (if (= h lab) (+ ok 1) ok)))))

(define-function lib-atoms (idx)
  (if idx (cons (l-atom 'on (list (number->string (car idx)))) (lib-atoms (cdr idx))) ()))

(define-function lib-rule-list (lib)
  (if lib
      (cons (l-rule (l-atom 'digit (list (number->string (car (car lib)))))
                    (lib-atoms (car (cdr (car lib)))))
            (lib-rule-list (cdr lib)))
      ()))

(define-function lib-proof-case (c lib ok)
  (if (>= c 10) ok
      (let* ((bits (l-nth case-bits c))
             (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
             (h (lib-pick-head bits valid lib 0))
             (facts (l-nth (l-nth *mnist-cases* c) 1))
             (goal (l-atom 'digit (list (number->string h))))
             (rules2 (l-append rules218 (lib-rule-list lib)))
             (pr (p-prove facts rules2 goal 50000))
             (pok (if (and pr (equal (l-nth pr 1) 'proof))
                      (if (p-proof-check facts rules2 goal (l-nth pr 2)) 1 0) 0)))
        (print "PROOF-CASE " c " HEAD " h " PROOF " pok "\n")
        (lib-proof-case (+ c 1) lib (+ ok pok)))))

(define-function lib-eval-k (K)
  (let* ((lib (lib-build K))
         (acc (lib-eval-case 0 lib 0)))
    (print "K " K " LIB " (list-length lib) " ACC " acc "/10\n")
    lib))

(head-train 10)
(lib-eval-k 1)
(lib-eval-k 3)
(define lib5 (lib-eval-k 5))
(lib-eval-k 10)
(lib-eval-k 20)
(print "K5-PROOF " (lib-proof-case 0 lib5 0) "/10\n")
