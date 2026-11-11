;;; Fresh process: load basis learned from actual web data.
(print "LOAD " (w-load "/tmp/dlm-web-recursive-basis.l") "\n")
(define qs (list (l-atom 'isa (list 'dog 'living-thing))
                 (l-atom 'isa (list 'sparrow 'living-thing))
                 (l-atom 'isa (list 'plant 'living-thing))))
(define held (let ((n 0)) (list-do q qs (if (equal (l-nth (p-prove *web-edges* (w-rules) q 20000) 1) 'proof) (set n (+ n 1)))) n))
(define neg (l-nth (p-prove *web-edges* (w-rules) (l-atom 'isa (list 'living-thing 'dog)) 20000) 1))
(print "HELD " held "/3 NEG " neg " RULES " (l-len (w-rules)) "\n")
(print "done-rec-persist-p2\n")
