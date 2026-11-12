;;; loop.l — failed goal -> transitivity synthesis -> admit -> re-evaluate.
(define-function sy-term (x) (if (string? x) (string->symbol x) x))
(define-function sy-atom (a) (l-atom (l-pred a) (l-map sy-term (l-args a))))
(define-function sy-fact (f) (l-fact (l-fact-id f) (sy-atom (l-fact-atom f))))
(define-function sy-rule (r) (l-rule (sy-atom (l-head r)) (l-map sy-atom (l-body r))))

(define *records* (w-to-records *web-obs*))
(define *kb* (nl-build *records*))
(define *facts* (l-map sy-fact (car *kb*)))
(define *rules0* (l-map sy-rule (car (cdr *kb*))))
(define *rules* *rules0*)
(define *neg* (l-atom 'isa (list 'data-collection 'MNIST)))
(define *pos*
  (list (l-atom 'isa (list 'MNIST 'data-collection))
        (l-atom 'isa (list 'handwritten-digit 'pixel-grid))
        (l-atom 'isa (list 'image 'data-structure))))
(define *held*
  (list (l-atom 'isa (list 'MNIST 'data-structure))
        (l-atom 'isa (list 'handwritten-digit 'data-structure))))

(define-function p3 (facts rules q)
  (let ((pr (p-prove facts rules q 20000)))
    (if (and (equal (l-nth pr 1) 'proof)
             (p-proof-check facts rules q (l-nth pr 2))) 1 0)))
(define-function c3 (facts rules qs n ok)
  (if qs (c3 facts rules (cdr qs) (+ n 1) (+ ok (p3 facts rules (car qs)))) (list n ok)))
(define-function unproved (facts rules qs out)
  (if qs (unproved facts rules (cdr qs)
          (if (= (p3 facts rules (car qs)) 0) (l-append out (list (car qs))) out)) out))

(define b0 (c3 *facts* *rules* *pos* 0 0))
(define failed (unproved *facts* *rules* *pos* ()))
(define-function learn-goals (facts rules qs learned)
  (if (not qs) (list rules learned)
    (let ((c (s-trans-synthesize facts (car qs) rules (list *neg*) 20000)))
      (if (equal c '(none))
        (learn-goals facts rules (cdr qs) learned)
        (learn-goals facts (l-append rules (list (s-rule c)))
                     (l-append (cdr qs) (unproved facts (l-append rules (list (s-rule c))) *pos* ()))
                     (l-append learned (list c)))))))
(define learned (learn-goals *facts* *rules* failed ()))
(define *rules1* (car learned))
(define *learned* (car (cdr learned)))
(define b1 (c3 *facts* *rules1* *pos* 0 0))
(define h0 (c3 *facts* *rules1* *held* 0 0))

;; Need-driven acquisition: the residual bridge fact is synthetic/acquired,
;; not a theorem. It is added only after the held failure is observed.
(define *bridge* (l-fact "acq-bridge"
  (l-atom 'isa (list 'pixel-matrix-collection 'pixel-grid))))
(define *facts2* (l-append *facts* (list *bridge*)))
(define h1 (c3 *facts2* *rules1* *held* 0 0))

;; Content scramble: same structure, different predicate constant.
(define-function scr-fact (f)
  (let ((a (l-fact-atom f)))
    (l-fact (l-fact-id f) (l-atom 'scrambled (l-args a)))))
(define-function scr-rule (r)
  (l-rule (l-atom 'scrambled (l-args (l-head r)))
          (l-map (lambda (a) (l-atom 'scrambled (l-args a))) (l-body r))))
(define scr (c3 (l-map scr-fact *facts*) (l-map scr-rule *rules1*) *pos* 0 0))

(print "WEB " (l-len *web-obs*) " FACTS " (l-len *facts*) " RULES0 " (l-len *rules0*) "\n")
(print "BEFORE " (car (cdr b0)) "/" (car b0) " FAILED " (l-len failed) "\n")
(print "LEARNED " (l-len *learned*) " RULES1 " (l-len *rules1*) "\n")
(print "AFTER " (car (cdr b1)) "/" (car b1) " HELD0 " (car (cdr h0)) "/" (car h0) " HELD1 " (car (cdr h1)) "/" (car h1) "\n")
(print "NEG " (p3 *facts2* *rules1* *neg*) " SCRAMBLE " (car (cdr scr)) "/" (car scr) "\n")
(print "PROV-ACQ synthetic" " BRIDGE " (l-fact-id *bridge*) "\n")
(print "done-transitivity-loop\n")
