;;; mechanism.l — compare proof-frontier basis revision with examples.
(define-function sy-term (x) (if (string? x) (string->symbol x) x))
(define-function sy-atom (a) (l-atom (l-pred a) (l-map sy-term (l-args a))))
(define-function sy-fact (f) (l-fact (l-fact-id f) (sy-atom (l-fact-atom f))))
(define-function sy-rule (r) (l-rule (sy-atom (l-head r)) (l-map sy-atom (l-body r))))

(define *records* (w-to-records *web-obs*))
(define *kb* (nl-build *records*))
(define *facts* (l-map sy-fact (car *kb*)))
(define *rules0* (l-map sy-rule (car (cdr *kb*))))
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

;; Put the given rules in a real axiom store.
(define-function ax-load (i rs out)
  (if rs (ax-load (+ i 1) (cdr rs)
          (l-append out (list (a-axiom (concat-strings "base-" (number->string i))
                 (car rs) (list "given:web") (list "given") () 0 'active ()))))
      out))
(define *ax* (ax-load 0 *rules0* ()))
(define-function active-rules (axs) (a-active-rules axs))

;; Mechanism M2: from the failed proof frontier signature alone (predicate/arity),
;; propose a same-predicate composition schema. No fact-pair enumeration.
(define-function frontier-rule (goal)
  (let ((p (l-pred goal)) (args (l-args goal)))
    (if (= 2 (l-len args))
        (let ((x (l-var 'x)) (y (l-var 'y)) (z (l-var 'z)))
          (l-rule (l-atom p (list x z))
                  (list (l-atom p (list x y))
                        (l-atom p (list y z)))))
        ())))
(define-function frontier-candidate (facts rules goal)
  (let ((fr (p-frontier facts rules goal 20000)))
    (if fr (let ((r (frontier-rule goal)))
             (if r (list 'candidate 'frontier-signature r (list goal)) ()))
        ())))
(define-function admit-frontier (facts axs goal n)
  (let ((c (frontier-candidate facts (active-rules axs) goal)))
    (if (not c) (list axs 0)
      (let ((r (l-nth c 2)))
        (if (not (s-conflict? facts (l-append (active-rules axs) (list r)) (list *neg*) 20000))
            (let* ((id (concat-strings "learned-" (number->string n)))
                   (ax2 (a-add axs id r (list "proof-frontier") (list "frontier") ())))
              (list (a-activate ax2 id) 1))
            (list axs 0))))))
(define-function learn-loop (facts axs qs n added)
  (if (not qs) (list axs added)
      (let* ((r (admit-frontier facts axs (car qs) n))
             (ax2 (car r)) (add (car (cdr r))))
        (learn-loop facts ax2 (cdr qs) (+ n 1) (+ added add)))))
(define b0 (c3 *facts* *rules0* *pos* 0 0))
(define learn (learn-loop *facts* *ax* *pos* 0 0))
(define *ax1* (car learn))
(define *learned* (car (cdr learn)))

(define b1 (c3 *facts* (active-rules *ax1*) *pos* 0 0))
(define h0 (c3 *facts* (active-rules *ax1*) *held* 0 0))

;; M3 acquisition: use the proof frontier's missing atom, not a hardcoded bridge.
(define-function first-missing (facts rules qs)
  (if qs
      (let ((f (p-frontier facts rules (car qs) 20000)))
        (if f f (first-missing facts rules (cdr qs))))
      ()))
(define miss (first-missing *facts* (active-rules *ax1*) *held*))
(define *facts2* *facts*)
(define *acq* ())
(if (and miss (equal (car miss) 'missing107))
    (begin
      (set *acq* (l-fact "acq-frontier" (l-nth miss 1)))
      (set *facts2* (l-append *facts* (list *acq*)))))
(define h1 (c3 *facts2* (active-rules *ax1*) *held* 0 0))

;; Retraction atomically removes the learned rule from the store.
(define *ax1r* (a-deactivate *ax1* "learned-0"))
(define br (c3 *facts* (active-rules *ax1r*) *pos* 0 0))

;; M2 invariance under fact permutation.
(define-function rev (xs) (if (not xs) () (l-append (rev (cdr xs)) (list (car xs)))))
(define bp (c3 (rev *facts*) (active-rules *ax1*) *pos* 0 0))

;; Content scramble: same shape, different predicate constant.
(define-function scr-fact (f)
  (let ((a (l-fact-atom f))) (l-fact (l-fact-id f) (l-atom 'scrambled (l-args a)))))
(define-function scr-rule (r)
  (l-rule (l-atom 'scrambled (l-args (l-head r)))
          (l-map (lambda (a) (l-atom 'scrambled (l-args a))) (l-body r))))
(define scr (c3 (l-map scr-fact *facts2*) (l-map scr-rule (active-rules *ax1*)) *pos* 0 0))

(print "WEB " (l-len *web-obs*) " FACTS " (l-len *facts*) " RULES0 " (l-len *rules0*) " STORE " (l-len *ax*) "\n")
(print "M2 BEFORE " (car (cdr b0)) "/" (car b0) " AFTER " (car (cdr b1)) "/" (car b1) " LEARNED " *learned* "\n")
(print "M2 SOURCE frontier-signature ENUMERATED false\n")
(print "M3 FRONTIER " miss " ACQ " (if *acq* (l-fact-id *acq*) "none") " HELD0 " (car (cdr h0)) "/" (car h0) " HELD1 " (car (cdr h1)) "/" (car h1) "\n")
(print "RETRACT " (car (cdr br)) "/" (car br) " PERMUTE " (car (cdr bp)) "/" (car bp) " SCRAMBLE " (car (cdr scr)) "/" (car scr) "\n")
(print "NEG " (p3 *facts2* (active-rules *ax1*) *neg*) " ACQ-TIER synthetic\n")
(print "done-mechanism\n")
