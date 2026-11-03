;;; Data only: no task programs, expected basis definitions or answer labels.
(basis91 'init '(r s t))
(basis91 'observe 'train '((atom r (a b)) (atom s (b c)) (atom t (c d))
                           (atom r (p q)) (atom s (q z)) (atom t (z w))))
(basis91 'interpret 'train 200000)
