;;; d107-agenda.l — one deterministic agenda over one state.
;;; Order: interpret every observation, then try to move the logical basis by
;;; learning a definition from the SAME data, then idle. Learning never mutates
;;; observations.

(define-function p107-next-item (s)
  (let ((out ()))
    (list-do o (p107-obs-list s)
      (if (and (not out) (not (p107-int s (p107-nth o 1))))
        (set out (list 'interpret (p107-nth o 1)))))
    (if out out
      (let ((r (p107-learn s)))
        (if (and r (equal (car r) 'learned107)) (list 'learn) ())))))

(define-function p107-step (s budget)
  (let ((item (p107-next-item s)))
    (if (not item) (list 'idle s)
      (if (equal (car item) 'learn)
        (let ((r (p107-learn s)))
          (if (and r (equal (car r) 'learned107))
            (let ((tr (p107-transition s (list 'def107 (p107-nth r 1)))))
              (if (= (car tr) 'applied) (list 'worked (p107-nth tr 1) (list 'learned107 (p107-def-id (p107-nth r 1))))
                tr))
            (list 'idle s)))
        (let ((r (p107-transition s (list 'interpret107 (p107-nth item 1) budget))))
          (if (= (car r) 'applied)
            (list 'worked (p107-nth r 1) (p107-int (p107-nth r 1) (p107-nth item 1)))
            r))))))
