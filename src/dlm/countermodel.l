;;; Total valuation over exactly the ground atoms of the root.
(define-function sq-eval (f model)
  (let ((tag (car f)))
    (if (= tag 'pred) (= (dlm-nth (dlm-assoc f model) 1) 'yes)
      (if (= tag 'top) true
        (if (= tag 'bottom) false
          (if (= tag 'not) (not (sq-eval (dlm-nth f 1) model))
            (if (= tag 'and) (and (sq-eval (dlm-nth f 1) model) (sq-eval (dlm-nth f 2) model))
              (if (= tag 'or) (or (sq-eval (dlm-nth f 1) model) (sq-eval (dlm-nth f 2) model))
                (or (not (sq-eval (dlm-nth f 1) model)) (sq-eval (dlm-nth f 2) model))))))))))
(define-function sq-check-countermodel (problem model)
  (and (sq-problem? problem) (sq-shape? model 2) (= (car model) 'model)
    (dlm-proper? (dlm-nth model 1) 1000)
    (let ((root (dlm-nth problem 3)) (seen ()) (ok true) (values (dlm-nth model 1)))
      (list-do entry values
        (if (and (sq-shape? entry 2) (sq-formula? 'classical-prop-v1 (car entry) (dlm-nth problem 2))
                 (= (car (car entry)) 'pred) (not (dlm-member? (car entry) seen))
                 (or (= (dlm-nth entry 1) 'yes) (= (dlm-nth entry 1) 'no)))
            (set seen (cons (car entry) seen)) (set ok false)))
      (let ((atoms (dlm-union (sq-context-atoms (sq-left root)) (sq-context-atoms (sq-right root)))))
        (set ok (and ok (not (dlm-difference atoms seen)) (not (dlm-difference seen atoms)))))
      (if ok
          (begin (list-do f (sq-left root) (if (not (sq-eval f values)) (set ok false)))
                 (list-do f (sq-right root) (if (sq-eval f values) (set ok false))))) ok)))
