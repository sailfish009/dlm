;;; Equivalent repeated dependencies: certificate DAG versus annotation traversal.
(list-do depth '(2 4 6 8 10)
  (let ((f '(pred p ())))
    (times-do depth (set f (list 'and f f)))
    (let* ((s (s79-proof-job (s79-new) 'p
                (list 'problem 'classical-prop-v1 '((p 0)) (sq-sequent '((pred p ())) (list f)))))
           (done (s79-run s 1000))
           (cert (dlm-nth (dlm-nth (s79-job done 'p) 5) 2))
           (annotation (i79-annotation cert)) (steps 0))
      (while (dlm-nth annotation 1)
        (set annotation (i79-annotation-step annotation)) (set steps (+ steps 1)))
      (dump (list 'depth depth 'certificate-nodes (dlm-length (dlm-nth cert 3))
                  'annotation-events steps)) (print "\n"))))
