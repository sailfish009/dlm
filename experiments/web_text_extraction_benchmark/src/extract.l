;;; extract.l — actual text parser; gold is loaded only after extraction.
(define-function wtext-id (x) (l-nth x 1))
(define-function wtext-url (x) (l-nth x 2))
(define-function wtext-text (x) (l-nth x 3))
(define-function parse-text (xs out)
  (if (not xs) out
      (let* ((o (car xs)) (r (nl-parse (wtext-text o))))
        (parse-text (cdr xs)
          (if (or (equal (nl-kind r) 'nl-fact)
                  (equal (nl-kind r) 'nl-subclass)
                  (equal (nl-kind r) 'nl-rule))
              (l-append out (list (list (wtext-id o) (nl-kind r) (nl-subj r) (nl-obj r))))
              out)))))
(define *extracted* (parse-text *web-text* ()))
