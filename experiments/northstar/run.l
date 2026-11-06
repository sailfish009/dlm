;;; North-star slice (M1): reduce -> observe -> interpret -> read -> count.
;;; Input is data only. Background laws are GIVEN and declared; nothing here is
;;; a learned definition, and N4-N9 are not implemented yet.

(define-function ns-load (path)
  (let ((d (p107-read-data path)))
    (if (not (= (car d) 'data)) () (cdr (p107-nth d 1)))))

(define-function ns-facts (rows)
  (let ((out ()))
    (list-do r rows
      (set out (p107-append out (list (p107-atom (string->symbol (p107-nth r 1)) (p107-nth r 2))))))
    out))


(set *p107-edb* '(calls has_layer method_of attr meaning))
(define background (list (p107-rule (p107-atom 'calls_concept (list (p107-var 'm) (p107-var 'c)))
  (list (p107-atom 'calls (list (p107-var 'm) (p107-var 'x)))
        (p107-atom 'meaning (list (p107-var 'x) (p107-var 'c)))))))
(dlm 'rules background)

(define reduced (ns-load "experiments/northstar/facts.sexp"))
(assert reduced "facts file must be present (run adapters/reduce.py)")
(define code-facts (ns-facts reduced))
(print "reduced facts: " (p107-len code-facts) "\n")
(dlm 'observe 'mnist-code "pytorch/examples" "main.py" 'mnist code-facts)

(define meanings (list
  (p107-atom 'meaning (list "nn.Module" "module_base"))
  (p107-atom 'meaning (list "nn.Conv2d" "layer"))
  (p107-atom 'meaning (list "nn.Linear" "layer"))
  (p107-atom 'meaning (list "nn.Dropout" "layer"))
  (p107-atom 'meaning (list "DataLoader" "data_loading"))
  (p107-atom 'meaning (list "loss.backward" "backpropagation"))
  (p107-atom 'meaning (list "optimizer.step" "parameter_update"))
  (p107-atom 'meaning (list "model.eval" "evaluation"))
  (p107-atom 'meaning (list "torch.no_grad" "gradient_free"))
  (p107-atom 'meaning (list "torch.save" "serialization"))))
(dlm 'observe 'pytorch-knowledge "given-vocabulary" "knowledge-map" 'mnist meanings)

(dlm 'run 4 200000)
(dump (dlm 'status)) (print "\n")

(define reading (dlm 'read 'mnist 200000))
(print "status=" (p107-nth reading 2) " facts=" (p107-nth reading 3)
       " sentences=" (p107-len (p107-nth reading 4)) " skipped=" (p107-nth reading 5) "\n")
(dump (p107-levels (p107-nth reading 4))) (print "\n")

;; library-only view: calls whose callee is not a locally defined method
(define lib (p107-filter (lambda (s)
    (let ((a (p107-nth s 3)))
      (if (equal (p107-pred a) 'calls)
        (let ((callee (p107-str (p107-nth (p107-args a) 1))))
          (and (p107-has-char callee 46) (not (p107-prefix? callee "self."))))
        true)))
  (p107-nth reading 4)))
(dump (p107-levels lib)) (print "\n")
(print "library sentences=" (p107-len lib) "\n")
(list-do s lib (if (<= (p107-nth s 1) 3) (begin (print "  " (p107-nth s 2) "\n"))))
(print "done-northstar\n")
