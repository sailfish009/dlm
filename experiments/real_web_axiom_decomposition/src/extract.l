;;; extract.l — text-only extraction; no gold is loaded here.
(define-function wtext-text (x) (l-nth x 3))
(define-function wtext-id (x) (l-nth x 1))
(define-function pred-of (r) (if (equal (nl-kind r) 'nl-subclass) 'subclass 'isa))
(define-function parse-all (xs out)
  (if (not xs) out
      (let ((r (nl-parse (wtext-text (car xs)))))
        (parse-all (cdr xs)
          (if (or (equal (nl-kind r) 'nl-fact) (equal (nl-kind r) 'nl-rule))
              (l-append out (list (list (wtext-id (car xs)) (nl-kind r) (pred-of r) (nl-subj r) (nl-obj r))))
              out)))))
(define *extracted* (parse-all *web-text* ()))
(print "TEXT " (l-len *web-text*) " EXTRACTED " (l-len *extracted*) "\n")
