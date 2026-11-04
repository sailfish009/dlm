;;; Synthetic numerical observations only; no expected basis body is supplied.
(define fixture93 (e79-raw-read "experiments/eml93/input-example.sexp"))
(assert (= (car fixture93) 'data) "EML93 fixture")
(define-function e93-demo-state (branch)
  (let ((s (e93-new branch)))
    (list-do cmd (dlm-nth (dlm-nth fixture93 1) 3)
      (let ((next (e93-step s cmd)))
        (assert (= (car next) 'eml-state93) "EML93 formation demo") (set s next))) s))
