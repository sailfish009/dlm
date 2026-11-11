;;; library_selfsup.l — E07: label-free support/conflict gate.
;;; Candidate h :- first K on-bits from a training image.
;;; Validation: count covered images whose existing valid rule set contains h
;;; (support) vs does not (conflict). No labels used in the gate.

(define-function ss-range (a b) (if (>= a b) () (cons a (ss-range (+ a 1) b))))
(define val-heads
  (dt-seq-map (lambda (j)
                (dt-seq-map (lambda (k) (l-nth rule-heads k))
                            (dt-valid-rules (l-nth pool-bits j) 0 rule-heads rule-bodies ())))
              (ss-range 150 190)))

(define-function ss-take-on (bits i k)
  (if (or (>= i 196) (<= k 0)) ()
      (if (= (l-nth bits i) 1)
          (cons i (ss-take-on bits (+ i 1) (- k 1)))
          (ss-take-on bits (+ i 1) k))))

(define-function ss-match? (bits body)
  (if body (if (= (l-nth bits (car body)) 1) (ss-match? bits (cdr body)) ()) (not ())))

(define-function ss-count (body h j support conflict)
  (if (>= j 190) (list support conflict)
      (let ((bits (l-nth pool-bits j)))
        (if (ss-match? bits body)
            (if (l-member? h (l-nth val-heads (- j 150)))
                (ss-count body h (+ j 1) (+ support 1) conflict)
                (ss-count body h (+ j 1) support (+ conflict 1)))
            (ss-count body h (+ j 1) support conflict)))))

(define-function ss-member? (h b lib)
  (if lib (if (and (= h (car (car lib))) (equal b (car (cdr (car lib))))) 1
             (ss-member? h b (cdr lib)))
      0))

(define-function ss-add-one (K i lib)
  (if (>= i 150) lib
      (let* ((bits (l-nth pool-bits i))
             (body (ss-take-on bits 0 K))
             (h (head-pred bits))
             (c (ss-count body h 150 0 0))
             (support (car c)) (conflict (car (cdr c))))
        (if (and (>= support 2) (>= support conflict)
                 (= 0 (ss-member? h body lib)))
            (ss-add-one K (+ i 1) (l-append lib (list (list h body))))
            (ss-add-one K (+ i 1) lib)))))

(define-function ss-build (K) (ss-add-one K 0 ()))

(define-function ss-matches (bits lib out)
  (if lib
      (ss-matches bits (cdr lib)
                  (if (ss-match? bits (car (cdr (car lib))))
                      (l-append out (list (car (car lib)))) out))
      out))

(define-function ss-pick-head (bits valid lib)
  (let* ((hs (head-scores bits))
         (heads (l-append (dt-seq-map (lambda (k) (l-nth rule-heads k)) valid)
                          (ss-matches bits lib ()))))
    (if heads
        (let ((best (car heads)))
          (list-do h (cdr heads) (if (> (l-nth hs h) (l-nth hs best)) (set best h)))
          best)
        -1)))

(define-function ss-eval-case (c lib ok)
  (if (>= c 10) ok
      (let* ((bits (l-nth case-bits c))
             (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
             (h (ss-pick-head bits valid lib))
             (lab (string->number (car (l-nth *mnist-cases* c)))))
        (ss-eval-case (+ c 1) lib (if (= h lab) (+ ok 1) ok)))))

(define-function ss-atoms (idx)
  (if idx (cons (l-atom 'on (list (number->string (car idx)))) (ss-atoms (cdr idx))) ()))

(define-function ss-rules (lib)
  (if lib
      (cons (l-rule (l-atom 'digit (list (number->string (car (car lib)))))
                    (ss-atoms (car (cdr (car lib)))))
            (ss-rules (cdr lib)))
      ()))

(define-function ss-proof-case (c lib ok)
  (if (>= c 10) ok
      (let* ((bits (l-nth case-bits c))
             (valid (dt-valid-rules bits 0 rule-heads rule-bodies ()))
             (h (ss-pick-head bits valid lib))
             (facts (l-nth (l-nth *mnist-cases* c) 1))
             (goal (l-atom 'digit (list (number->string h))))
             (rules2 (l-append rules218 (ss-rules lib)))
             (pr (p-prove facts rules2 goal 50000))
             (pok (if (and pr (equal (l-nth pr 1) 'proof))
                      (if (p-proof-check facts rules2 goal (l-nth pr 2)) 1 0) 0)))
        (ss-proof-case (+ c 1) lib (+ ok pok)))))

(define-function ss-eval-k (K)
  (let* ((lib (ss-build K)) (acc (ss-eval-case 0 lib 0)))
    (print "K " K " LIB " (list-length lib) " ACC " acc "/10\n")
    lib))

(head-train 10)
(ss-eval-k 1)
(ss-eval-k 3)
(define lib5 (ss-eval-k 5))
(ss-eval-k 10)
(ss-eval-k 20)
(print "K5-PROOF " (ss-proof-case 0 lib5 0) "/10\n")
