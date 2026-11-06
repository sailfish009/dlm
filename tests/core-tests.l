;;; core-tests.l — native assertions for the minimal 0.0103 core.
;;; Each block is independent; a failure aborts with a message.

(define *failures* 0)
(define-function check (label value)
  (if (not value) (begin (set *failures* (+ *failures* 1)) (print "FAIL " label "\n"))
    (print "ok " label "\n")))

;;; ---------- 1. proof checker ----------
(set *p107-edb* '(link right blocked))
(define rules (list
  (p107-rule (p107-atom 'path (list (p107-var 'x) (p107-var 'z)))
    (list (p107-atom 'link (list (p107-var 'x) (p107-var 'y)))
          (p107-atom 'right (list (p107-var 'y) (p107-var 'z)))))
  (p107-rule (p107-atom 'start (list (p107-var 'x)))
    (list (p107-atom 'link (list (p107-var 'x) (p107-var 'y)))
          (p107-neg (p107-atom 'blocked (list (p107-var 'x))))))))
(check "rules are safe" (p107-rules? rules))
(define facts (list (p107-given-id "g0" (p107-atom 'link (list "a" "b")))
                    (p107-given-id "g1" (p107-atom 'link (list "b" "c")))
                    (p107-given-id "g2" (p107-atom 'right (list "c" "d")))
                    (p107-given-id "g3" (p107-atom 'blocked (list "b")))))
(define cl (p107-close facts rules 5000))
(check "closure complete" (equal (p107-nth cl 1) 'complete))
(define table (p107-nth cl 2))
(define path (p107-atom 'path (list "b" "d")))
(define proof (p107-evidence path table))
(check "derived fact has proof" (p107-proof-ok? proof path table rules))
(check "forged substitution rejected"
  (not (p107-proof-ok? '(pr 0 (((var x) "a") ((var y) "b") ((var z) "d"))) path table rules)))
(check "wrong atom rejected" (not (p107-proof-ok? proof (p107-atom 'path (list "a" "d")) table rules)))
(check "unknown proof shape rejected" (not (p107-proof-ok? '(bogus) path table rules)))

;;; ---------- 2. negation is closed-world over EDB ----------
(check "blocked source has no start" (not (p107-lookup (p107-atom 'start (list "b")) table)))
(check "unblocked source has start" (p107-lookup (p107-atom 'start (list "a")) table))
(check "negative over intensional predicate is unsafe"
  (not (p107-rule-safe? (p107-rule (p107-atom 'q (list (p107-var 'x)))
    (list (p107-atom 'link (list (p107-var 'x) (p107-var 'y)))
          (p107-neg (p107-atom 'path (list (p107-var 'x) (p107-var 'y)))))))))

;;; ---------- 3. budget exhaustion is unknown, never false ----------
(define tight (p107-close facts rules 2))
(check "tight budget reports unknown" (equal (p107-nth tight 1) 'unknown))
(define wide (p107-lookup path table))
(check "wide budget derived it" (not (equal wide ())))

;;; ---------- 4. session, scope, retraction, replay ----------
(define-function obs-of (id scope atoms) (list 'obs107 id "src" "rec" scope atoms))
(define s0 (p107-new))
(define r1 (p107-transition s0 (list 'obs107 'oA "src" "rec" 'scopeA
  (list (p107-atom 'link (list "a" "b")) (p107-atom 'right (list "b" "c"))
        (p107-atom 'calls (list "a" "b"))))))
(define s1 (p107-nth r1 1))
(check "observe applies" (equal (car r1) 'applied))
(check "duplicate observation rejected"
  (equal (p107-apply s1 (list 'obs107 'oA "src" "rec" 'scopeA ())) '(rejected107 observation)))
(define r2 (p107-transition s1 (list 'obs107 'oB "src" "rec" 'scopeB
  (list (p107-atom 'link (list "z" "z"))))))
(define s2 (p107-nth r2 1))
(check "scope A closure isolated"
  (= 3 (p107-len (p107-nth (p107-closure s2 'scopeA 5000) 1))))
(check "scope B closure isolated"
  (= 1 (p107-len (p107-nth (p107-closure s2 'scopeB 5000) 1))))
(define r3 (p107-transition s2 (list 'interpret107 'oA 5000)))
(define s3 (p107-nth r3 1))
(check "interpret records metrics" (and (= 5 (p107-len (p107-int s3 'oA)))
  (equal (p107-nth (p107-int s3 'oA) 2) 'complete)))
(define r4 (p107-transition s3 (list 'retract107 'oA)))
(define s4 (p107-nth r4 1))
(check "retract removes only the retracted facts"
  (and (= 1 (p107-len (p107-obs-list s4))) (not (p107-obs s4 'oA)) (p107-obs s4 'oB)))
(check "retract removes interpretation" (= 0 (p107-len (p107-int-list s4))))
(define rr (p107-replay (p107-events s3)))
(check "replay reproduces state" (and (= (car rr) 'replayed) (equal (p107-nth rr 1) s3)))
(check "snapshot validates" (p107-snapshot? (p107-snapshot s3)))
(define tampered (p107-snapshot (p107-set s3 5 (list (p107-def 'x () (list (p107-atom 'q (list))) ())))))
(check "tampered snapshot rejected" (not (p107-snapshot? tampered)))
(check "event limit rejected"
  (let ((big (p107-set s3 6 (p107-map (lambda (i) (list 'reset107)) (p107-range 300)))))
    (equal (p107-transition big '(reset107)) '(rejected107 event-limit))))

;;; ---------- 5. reading abstains without support ----------
(define sent (p107-read s3 'scopeA 5000))
(check "reading has status" (= (p107-nth sent 2) 'complete))
(check "reading emits sentences" (= 1 (p107-len (p107-nth sent 4))))
(check "unreadable predicates are not narrated" (= 0 (p107-level-count (p107-nth sent 4) 2)))
(check "no sentence without checked support"
  (not (p107-any? (lambda (x) (not (p107-proof-ok? (p107-nth x 4) (p107-nth x 3)
                                                    (p107-nth (p107-closure s3 'scopeA 5000) 1) rules)))
                  (p107-nth sent 4))))
(check "level counts are consistent"
  (= (p107-len (p107-nth sent 4))
     (let ((n 0)) (list-do l (p107-levels (p107-nth sent 4)) (set n (+ n (p107-nth l 1)))) n)))


;;; ---------- 6. review regressions (0.0103 defects) ----------
;;; (a) a derived fact cannot be presented as an extensional `given`
(define derived-id (p107-nth (p107-lookup path table) 1))
(check "given proof must point at an extensional fact"
  (not (p107-proof-ok? (list 'given derived-id) path table rules)))

;;; (b) a child with an invalid proof cannot support a later conclusion
(set *p107-edb* '(seed q))
(define srules (list
  (p107-rule (p107-atom 'node (list (p107-var 'x))) (list (p107-atom 'q (list (p107-var 'x)))))
  (p107-rule (p107-atom 'node2 (list (p107-var 'x))) (list (p107-atom 'node (list (p107-var 'x)))))))
(define forged (list (p107-given-id "g0" (p107-atom 'q (list "a")))
                     (list 'fact "d0" (p107-atom 'node (list "z"))
                           (list 'pr 0 (list (list (p107-var 'x) "z")) ()))
                     (list 'fact "d1" (p107-atom 'node2 (list "z"))
                           (list 'pr 1 (list (list (p107-var 'x) "z")) (list "d0")))
                     (list 'fact "d2" (p107-atom 'node (list "z"))
                           (list 'pr 0 (list (list (p107-var 'x) "z")) (list "d2")))))
(check "child with an invalid proof rejected"
  (not (p107-proof-ok? (list 'pr 0 (list (list (p107-var 'x) "z")) ()) (p107-atom 'node (list "z")) forged srules)))
(check "downstream of an invalid child rejected"
  (not (p107-proof-ok? (list 'pr 1 (list (list (p107-var 'x) "z")) (list "d0"))
                       (p107-atom 'node2 (list "z")) forged srules)))
(check "cyclic stored proof rejected"
  (not (p107-proof-ok? (list 'pr 0 (list (list (p107-var 'x) "z")) (list "d2"))
                       (p107-atom 'node (list "z")) forged srules)))
(check "negative rule index rejected without a fatal"
  (not (p107-proof-ok? (list 'pr -1 () ()) (p107-atom 'node (list "z")) forged srules)))
(check "malformed proof structure rejected"
  (not (p107-proof-ok? (list 'pr 0 'notpairs ()) (p107-atom 'node (list "z")) forged srules)))

;;; (c) an extensional predicate cannot be a rule head
(set *p107-edb* '(q r))
(check "extensional head rejected"
  (not (p107-rule-safe? (p107-rule (p107-atom 'q (list (p107-var 'a) (p107-var 'b)))
    (list (p107-atom 'r (list (p107-var 'a) (p107-var 'b))))))))
(check "head variable must be range-restricted"
  (not (p107-rule-safe? (p107-rule (p107-atom 'h (list (p107-var 'a)))
    (list (p107-atom 'q (list (p107-var 'b) (p107-var 'b))))))))

;;; (d) argument order changes the background-law digest
(define rorder1 (list (p107-rule (p107-atom 'h (list (p107-var 'x) (p107-var 'y)))
  (list (p107-atom 'q (list (p107-var 'x) (p107-var 'y)))))))
(define rorder2 (list (p107-rule (p107-atom 'h (list (p107-var 'x) (p107-var 'y)))
  (list (p107-atom 'q (list (p107-var 'y) (p107-var 'x)))))))
(check "rule digest detects argument order"
  (not (equal (p107-digest rorder1) (p107-digest rorder2))))

;;; (e) malformed command input is rejected, not a native fault
(check "malformed observe rejected" (equal (dlm 'observe 'x "s" "r" 'demo 'notalist)
                                           '(rejected107 observation)))
(check "dotted term rejected"
  (equal (dlm 'observe 'x "s" "r" 'demo (list (p107-atom 'q (list (cons "a" "b")))))
         '(rejected107 observation)))
(check "nested list term rejected"
  (equal (dlm 'observe 'x "s" "r" 'demo (list (p107-atom 'q (list (list "a")))))
         '(rejected107 observation)))
(check "non-numeric budget rejected" (equal (dlm 'step "x") '(rejected107 command-or-arity)))
(check "empty command rejected" (equal (dlm) '(rejected107 command)))
(check "non-atom query rejected" (equal (dlm 'query 'demo 'notatom) '(rejected107 query)))
(check "non-list command rejected" (equal (dlm 'run . 5) '(rejected107 command)))


;;; (f) literal order does not matter: a negation may precede its binding
(set *p107-edb* '(q blocked))
(define order-rules (list (p107-rule (p107-atom 'ok (list (p107-var 'x)))
  (list (p107-neg (p107-atom 'blocked (list (p107-var 'x))))
        (p107-atom 'q (list (p107-var 'x)))))))
(define order-facts (list (p107-given-id "g0" (p107-atom 'q (list "a")))
                          (p107-given-id "g1" (p107-atom 'q (list "b")))
                          (p107-given-id "g2" (p107-atom 'blocked (list "b")))))
(define order-table (p107-nth (p107-close order-facts order-rules 5000) 2))
(check "negation before its binding still fires"
  (and (p107-lookup (p107-atom 'ok (list "a")) order-table)
       (not (p107-lookup (p107-atom 'ok (list "b")) order-table))))

;;; (g) an empty body derives a nullary fact
(define empty-rules (list (p107-rule (p107-atom 'base ()) ())))
(define empty-table (p107-nth (p107-close () empty-rules 5000) 2))
(check "empty-body rule derives its nullary head" (p107-lookup (p107-atom 'base ()) empty-table))
(check "empty-body proof checks"
  (p107-proof-ok? (p107-nth (p107-lookup (p107-atom 'base ()) empty-table) 3)
                  (p107-atom 'base ()) empty-table empty-rules))


;;; ---------- 7. learning transition: data fixed, basis moves ----------
(set *p107-edb* '(calls tool))
(define-function lrec (s id owner a b c t1 t2)
  (p107-transition s (list 'obs107 id "fixture" id 'demo
    (list (p107-atom 'calls (list owner a)) (p107-atom 'calls (list owner b))
          (p107-atom 'calls (list owner c)) (p107-atom 'tool (list owner t1))
          (p107-atom 'tool (list owner t2))))))
(define ls0 (lrec (p107-new) 'r1 "m1" "open" "read" "close" "torch" "numpy"))
(define ls (p107-nth (lrec (p107-nth ls0 1) 'r2 "m2" "open" "write" "close" "torch" "numpy") 1))
(define q3 (list (p107-atom 'calls (list (p107-var 'a) (p107-var 'b)))
                 (p107-atom 'calls (list (p107-var 'a) (p107-var 'c)))
                 (p107-atom 'calls (list (p107-var 'a) (p107-var 'd)))))
(define before (p107-answer ls 'demo q3 200000))
(check "no basis before learning" (= 0 (p107-len (p107-defs-of ls))))
(check "raw plan has 3 steps" (= 3 (p107-nth (p107-plan ls q3) 2)))
(define l1 (p107-learn ls))
(check "first learning step forms a 2-atom unit" (equal (car l1) 'learned107))
(define ls1 (p107-nth (p107-transition ls (list 'def107 (p107-nth l1 1))) 1))
(define l2 (p107-learn ls1))
(check "second learning step forms a 3-atom unit" (equal (car l2) 'learned107))
(define ls2 (p107-nth (p107-transition ls1 (list 'def107 (p107-nth l2 1))) 1))
(check "two units in the basis" (= 2 (p107-len (p107-defs-of ls2))))
(check "second unit calls the first"
  (p107-call? (car (p107-def-body (p107-find-def (p107-defs-of ls2) 'b2)))))
(check "planned steps drop 3 -> 2" (= 2 (p107-nth (p107-plan ls2 q3) 3)))
(check "data unchanged by learning"
  (equal (p107-obs-list ls) (p107-obs-list ls2)))
(define after (p107-answer ls2 'demo q3 200000))
(check "answers and witnesses unchanged" (equal (p107-nth before 4) (p107-nth after 4)))
(check "raw path makes no unit call" (= 0 (p107-nth before 5)))
(check "planned path actually calls the unit" (>= (p107-nth after 5) 1))
(check "planned path uses the 2-step plan" (= 2 (p107-nth (p107-plan ls2 q3) 3)))
(check "planned answer names its cover" (equal (p107-nth after 7) 'b2))
(check "closure size unchanged" (= (p107-len (p107-nth before 4)) (p107-len (p107-nth after 4))))

;;; retraction reduces support; the unit stays but stops being used
(define ls3 (p107-nth (p107-transition ls2 (list 'retract107 'r2)) 1))
(check "support drops to 1" (= 1 (p107-support ls3 (p107-def-pattern (p107-find-def (p107-defs-of ls3) 'b1)))))
(check "unit remains, inactive" (= 2 (p107-len (p107-defs-of ls3))))
(check "plan reverts to 3 steps" (= 3 (p107-nth (p107-plan ls3 q3) 2)))
(check "retracted answer uses no unit" (= 0 (p107-nth (p107-answer ls3 'demo q3 200000) 5)))
(check "retracted answers shrink" (< (p107-len (p107-nth (p107-answer ls3 'demo q3 200000) 4))
                                     (p107-len (p107-nth after 4))))

;;; revision: replace the 2-atom unit by another supported structure
(define b1v (p107-def-vars (p107-find-def (p107-defs-of ls2) 'b1)))
(define toolq (list (p107-atom 'tool (list (p107-nth b1v 0) (p107-nth b1v 1)))
                    (p107-atom 'tool (list (p107-nth b1v 0) (p107-nth b1v 2)))))
(check "revision with permuted roles rejected"
  (equal (car (p107-transition ls2 (list 'revise107 'b1
    (list (p107-atom 'tool (list (p107-nth b1v 0) (p107-nth b1v 2)))
          (p107-atom 'tool (list (p107-nth b1v 0) (p107-nth b1v 1))))))) 'rejected107))
(define rev (p107-transition ls2 (list 'revise107 'b1 toolq)))
(check "revision accepted" (equal (car rev) 'applied))
(define ls4 (p107-nth rev 1))
(check "dependent unit dropped after revision" (= 1 (p107-len (p107-defs-of ls4))))
(check "revised pattern is the tool structure"
  (equal (p107-conj-key (p107-def-pattern (p107-find-def (p107-defs-of ls4) 'b1)))
         (p107-conj-key toolq)))
(check "calls plan no longer covered" (= 3 (p107-nth (p107-plan ls4 q3) 2)))

;;; a row may not reuse one fact for two atoms (shared-DAG refusal)
(define one (p107-nth (lrec (p107-new) 'r9 "m9" "open" "read" "close" "torch" "numpy") 1))
(define dupq (list (p107-atom 'calls (list (p107-var 'a) (p107-var 'b)))
                   (p107-atom 'calls (list (p107-var 'a) (p107-var 'b)))))
(check "repeated atom cannot reuse one fact"
  (= 0 (p107-len (p107-nth (p107-answer one 'demo dupq 200000) 4))))
(define shared (list (p107-atom 'calls (list (p107-var 'a) (p107-var 'b)))
                     (p107-atom 'calls (list (p107-var 'a) (p107-var 'c)))))
(check "distinct facts are still enumerable"
  (= 6 (p107-len (p107-nth (p107-answer one 'demo shared 200000) 4))))

(if (= *failures* 0) (print "ALL-CORE-TESTS-PASSED\n") (print "FAILURES " *failures* "\n"))