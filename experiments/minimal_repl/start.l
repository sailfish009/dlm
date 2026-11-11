;;; Maru REPL experiment: fixed data + fixed axiom library matching.
;;; Run: ./scripts/experiment.sh

(define vx (l-var? (list 'var 'x)))
(define x (list 'var 'x)) (define y (list 'var 'y)) (define z (list 'var 'z))
(define A (list
  (l-rule (l-atom 'ancestor (list x z)) (list (l-atom 'parent (list x z))))
  (l-rule (l-atom 'ancestor (list x z)) (list (l-atom 'parent (list x y)) (l-atom 'ancestor (list y z))))))
(define B (list
  (l-rule (l-atom 'reaches (list x z)) (list (l-atom 'manages (list x z))))
  (l-rule (l-atom 'reaches (list x z)) (list (l-atom 'manages (list x y)) (l-atom 'reaches (list y z))))))
(define C (list
  (l-rule (l-atom 'path (list x z)) (list (l-atom 'hop1 (list x y)) (l-atom 'hop2 (list y z))))))
(define D (list
  (l-rule (l-atom 'inside (list x z)) (list (l-atom 'contains (list x z))))
  (l-rule (l-atom 'inside (list x z)) (list (l-atom 'contains (list x y)) (l-atom 'inside (list y z))))))
(define E (list (l-rule (l-atom 'reaches (list x z)) (list (l-atom 'manages (list z x))))))
(define F (list (l-rule (l-atom 'foo (list x)) (list (l-atom 'bar (list x))))))
(define lib (list (d-axiom "A" A) (d-axiom "B" B) (d-axiom "C" C) (d-axiom "D" D) (d-axiom "E" E) (d-axiom "F" F)))
(define t1 (d-task "ancestor"
  (list (l-atom 'parent (list "a" "b")) (l-atom 'parent (list "b" "c")))
  (list (l-atom 'ancestor (list "a" "c"))) (list (l-atom 'ancestor (list "c" "a")))))
(define t2 (d-task "reaches"
  (list (l-atom 'manages (list "j" "k")) (l-atom 'manages (list "k" "l")))
  (list (l-atom 'reaches (list "j" "l"))) (list (l-atom 'reaches (list "l" "j")))))
(define t3 (d-task "path"
  (list (l-atom 'hop1 (list "r" "s")) (l-atom 'hop2 (list "s" "t")))
  (list (l-atom 'path (list "r" "t"))) (list (l-atom 'path (list "t" "r")))))
(define t4 (d-task "inside"
  (list (l-atom 'contains (list "u" "v")) (l-atom 'contains (list "v" "w")))
  (list (l-atom 'inside (list "u" "w"))) (list (l-atom 'inside (list "w" "u")))))
(print "DEDUCE-REPL minimal\n")
(define summary (d-run (list t1 t2 t3 t4) lib 20000))
(dump summary) (print "\n")
(list-do t (list t1 t2 t3 t4)
  (let ((e (d-eval t () 20000)))
    (print "FROZEN " (d-name t) " covered=" (l-nth e 0) "/" (l-nth e 1)
           " conflict=" (l-nth e 2) "\n")))
(define all-rules (d-rules lib (l-map d-axiom-id lib)))
(list-do t (list t1 t2 t3 t4)
  (let ((e (d-eval t all-rules 20000)))
    (print "ALL " (d-name t) " covered=" (l-nth e 0) "/" (l-nth e 1)
           " conflict=" (l-nth e 2) "\n")))
(print "done-deduce\n")
