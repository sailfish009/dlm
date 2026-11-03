;;; Formation remains data-led Basis91. Control starts from its frozen core.
(require "experiments/basis91/setup.l")
(basis91 'learn) (basis91 'learn)
(basis91 'observe 'dense '((atom r (a b)) (atom r (c d)) (atom r (e f)) (atom r (g h))
                           (atom s (b c)) (atom s (d e)) (atom s (f g)) (atom t (c d))))
