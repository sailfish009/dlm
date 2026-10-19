;;; -*- mode: lisp; coding: us-ascii -*-
;;; Input is a single datum, read without eval. One recursive round per process.
(define *sl-saved* (read *standard-input*))
(define *sl-current*
  (if *sl-saved*
      (let ((restored (sl-replay (dlm-nth *sl-saved* 2) (dlm-nth *sl-saved* 3))))
        (assert (and (= (car *sl-saved*) 'store) (= (dlm-nth *sl-saved* 1) 73)
                     (equal (dlm-nth *sl-saved* 2) *sl-training*)
                     (equal restored (dlm-nth *sl-saved* 4))) "store verification failed")
        restored)
    (sl-new *sl-training*)))
(define *sl-next* (sl-step *sl-current* (dlm-length (sl-candidates *sl-training*))))
(print (list 'store 73 *sl-training* (dlm-nth *sl-next* 4) *sl-next*) "\n")
