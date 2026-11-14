;;; parity-world.l — Maru ground-closure oracle for the GENERATED worlds.
;;;
;;; The 0.0242 oracle only checked a hardcoded 6-atom toy. Here the C kernel
;;; emits two real worlds (a fixed reference episode and the first test episode
;;; of seed 777) as Maru source (`out/episode.l`), and this file re-derives their
;;; closure independently with p-close. Only GROUND closure is cross-checked:
;;; the credit-weighted budgeted search is C-side (Maru has no credit search).
(define-function world-check (name facts rules goals ed er)
  (let ((table (p-close facts rules 20000)) (reached 0))
    (list-do g goals (if (l-lookup g table) (set reached (+ reached 1))))
    (print "WORLD " name " derived=" (l-len table) " reached=" reached
           " total=" (l-len goals) "\n")
    (and (= (l-len table) ed) (= reached er))))
(define wok (world-check "ref" wref-facts wref-rules wref-goals
                         wref-derived wref-reached))
(define tok (world-check "test0" wtest0-facts wtest0-rules wtest0-goals
                         wtest0-derived wtest0-reached))
(if (and wok tok)
    (print "MARU-WORLD-PASS\n")
    (print "MARU-WORLD-FAIL\n"))