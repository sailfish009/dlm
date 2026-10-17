;;; -*- mode: lisp; coding: us-ascii -*-
;;; Episodes: (episode SOURCE FACTS CONFIRMED CONTRADICTED).
;;; Unknown atoms are simply absent from the explicit contradicted partition.
(define-function dlm-episode (source facts confirmed contradicted)
  (list 'episode source facts confirmed contradicted))

;;; Verdict: (verdict COVERAGE DEBT FALSE-ASSERTS SOURCES REWARD USEFUL).
(define-function dlm-evaluate (r episodes theory)
  (if (not (dlm-safe? r)) (list 'verdict 0 0 0 () -100 false)
    (let ((coverage 0) (debt 0) (bad 0) (sources ()))
      (list-do e episodes
        (let* ((facts (dlm-nth e 2)) (confirmed (dlm-nth e 3))
               (before (dlm-closure facts theory))
               (after (dlm-closure facts (cons r theory)))
               (gained (dlm-difference (dlm-intersection confirmed after) before)))
          (set coverage (+ coverage (dlm-length gained)))
          (set debt (+ debt (dlm-length (dlm-difference confirmed after))))
          (set bad (+ bad (dlm-length (dlm-intersection (dlm-nth e 4) after))))
          (if gained (set sources (dlm-add sources (dlm-nth e 1))))))
      (list 'verdict coverage debt bad sources
            (- (+ (* 4 coverage) (* 2 (dlm-length sources))) (+ debt (* 20 bad)))
            (and (> coverage 0) (= bad 0))))))

;;; Three candidate families from the reference file, with arity constraints.
(define-function dlm-signatures (atoms)
  (if atoms
      (dlm-add (dlm-signatures (cdr atoms))
               (list (dlm-pred (car atoms)) (dlm-length (dlm-args (car atoms)))))
    ()))

(define-function dlm-execute-programs (facts goals)
  (let ((result ()) (body-sigs (dlm-signatures (dlm-append facts goals)))
        (head-sigs (dlm-signatures goals))
        (x (dlm-var 'x)) (y (dlm-var 'y)) (z (dlm-var 'z)))
    (list-do h head-sigs
      (list-do p body-sigs
        (if (= (dlm-nth h 1) (dlm-nth p 1))
            (begin
              (if (= (dlm-nth h 1) 1)
                  (set result (dlm-add result
                    (dlm-rule (dlm-atom (car h) x) (dlm-atom (car p) x)))))
              (if (= (dlm-nth h 1) 2)
                  (begin
                    (set result (dlm-add result
                      (dlm-rule (dlm-atom (car h) x z) (dlm-atom (car p) x z))))
                    (list-do q body-sigs
                      (if (= (dlm-nth q 1) 2)
                          (set result (dlm-add result
                            (dlm-rule (dlm-atom (car h) x z)
                                      (dlm-atom (car p) x y)
                                      (dlm-atom (car q) y z))))))))))))
    result))

(define-function dlm-supplied? (body supplies)
  (or (not body)
      (and (dlm-member? (dlm-pred (car body)) supplies)
           (dlm-supplied? (cdr body) supplies))))

(define-function dlm-route-candidates (candidates targets available mechanism)
  (let ((result ()))
    (list-do r candidates
      (if (or (equal mechanism "global-fixpoint")
              (and (or (not targets) (dlm-member? (dlm-pred (dlm-head r)) targets))
                   (or (not (equal mechanism "proof-flux"))
                       (dlm-supplied? (dlm-body r)
                                      (cons (dlm-pred (dlm-head r)) available)))))
          (set result (dlm-append result (list r)))))
    result))

;;; Choose at most one useful rule. No persistent-state/commit authority here.
;;; Result: (learning-result THEORY CHOSEN VERDICT CHECKS).
(define-function dlm-learn-round (episodes theory candidates budget)
  (let ((chosen ()) (best ()) (checks 0))
    (list-do r candidates
      (if (and (< checks budget) (not (dlm-member? r theory)))
          (let ((v (dlm-evaluate r episodes theory)))
            (set checks (+ checks 1))
            (if (and (dlm-nth v 6)
                     (or (not best) (> (dlm-nth v 5) (dlm-nth best 5))))
                (begin (set chosen r) (set best v))))))
    (list 'learning-result (if chosen (dlm-append theory (list chosen)) theory)
          chosen best checks)))

