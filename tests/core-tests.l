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

;;; role preservation: a permuted body no longer passes the definition check
(set *p107-edb* '(q))
(define rp (p107-def 'rp (list (p107-var 'v0) (p107-var 'v1))
  (list (p107-atom 'q (list (p107-var 'v0) (p107-var 'v1))))
  (list (p107-atom 'q (list (p107-var 'v0) (p107-var 'v1))))))
(define rp-bad (p107-def 'rp (list (p107-var 'v0) (p107-var 'v1))
  (list (p107-atom 'q (list (p107-var 'v0) (p107-var 'v1))))
  (list (p107-atom 'q (list (p107-var 'v1) (p107-var 'v0))))))
(check "role-preserving definition accepted" (p107-def-ok? rp ()))
(check "definition with permuted roles rejected" (not (p107-def-ok? rp-bad ())))
(define rp-call (p107-def 'rp2 (list (p107-var 'v0) (p107-var 'v1))
  (list (p107-atom 'q (list (p107-var 'v0) (p107-var 'v1))))
  (list (p107-call 'rp (list (p107-var 'v1) (p107-var 'v0))))))
(define rp-ok (p107-def 'rp2 (list (p107-var 'v0) (p107-var 'v1))
  (list (p107-atom 'q (list (p107-var 'v0) (p107-var 'v1))))
  (list (p107-call 'rp (list (p107-var 'v0) (p107-var 'v1))))))
(check "call with permuted actuals rejected" (not (p107-def-ok? rp-call (list rp))))
(check "call with matching actuals accepted" (p107-def-ok? rp-ok (list rp)))

;;; an answer witness must denote an atom of the grounded plan
(define wt (list (p107-given-id "w0" (p107-atom 'calls (list "zz" "yy")))))
(check "witness for a different atom rejected"
  (not (p107-witness-atoms? (list "w0") (list (p107-atom 'calls (list "a" "b"))) wt)))
(check "witness for a matching atom accepted"
  (p107-witness-atoms? (list "w0") (list (p107-atom 'calls (list "zz" "yy"))) wt))

;;; ---------- 8. Shen-inspired structural matching (library, not a VM) ----------
(define-function mv (n) (p107-pat-var n))
(check "literal match" (equal (car (p107-match1 "a" "a" ())) 'ok))
(check "literal mismatch" (equal (car (p107-match1 "a" "b" ())) 'no-match))
(check "repeated variable must be equal"
  (and (equal (car (p107-match1 (list (mv 'a) (mv 'a)) (list "v" "v") ())) 'ok)
       (equal (car (p107-match1 (list (mv 'a) (mv 'a)) (list "v" "w") ())) 'no-match)))
(check "empty bindings are a success, not a failure"
  (and (equal (car (p107-match1 (list) (list) ())) 'ok)
       (equal (p107-nth (p107-match1 (list) (list) ()) 1) ())))
(check "dotted pattern is an error, not a mismatch"
  (equal (car (p107-match1 (cons "a" "b") (list "a") ())) 'error))
(check "guard failure falls through to the next clause"
  (equal (p107-cases 2 (list (list (mv 'n) (lambda (b) false) (lambda (b) 'first))
                             (list (mv 'n) () (lambda (b) 'second)))
                     (lambda () 'fallback))
         '(ok second)))
(check "no clause yields the fallback"
  (equal (p107-cases 3 (list (list "a" () (lambda (b) 'x))) (lambda () '(no-match)))
         '(no-match)))
(check "mismatch never calls the body"
  (equal (p107-cases "z" (list (list "a" () (lambda (b) 'x))) (lambda () '(no-match)))
         '(no-match)))

;;; ---------- 9. Silicon-shaped Pre/Body/Post: assign only (step 0+1) ----------
(define c-ok (list 'c107 'setflag (list 'flag 'ready) '(b 1)
                   (list '(assign flag 1)) '(v flag) (list 'flag)))
(define c-post (list 'c107 'badpost (list 'flag) '(b 1)
                     (list '(assign flag 1)) '(not (v flag)) (list 'flag)))
(define c-vac (list 'c107 'vac (list 'x) (list 'and '(v x) '(not (v x)))
                    (list '(assign x 1)) '(b 1) (list 'x)))
(define c-frame (list 'c107 'badframe (list 'flag 'ready) '(b 1)
                      (list '(assign ready 1)) '(v flag) (list 'flag)))
(define c-bad (list 'c107 'bad (list 'x) '(b 1) (list '(assign y 1)) '(b 1) (list 'x)))
(check "valid contract verified" (equal (car (p107-c-verify c-ok)) 'verified))
(check "eligible inputs are exactly the Pre-satisfying states"
  (= 4 (p107-len (p107-nth (p107-c-verify c-ok) 1))))
(check "case table has 4 rows" (= 4 (p107-len (p107-nth (p107-c-verify c-ok) 1))))
(check "wrong postcondition refuted" (equal (car (p107-c-verify c-post)) 'refuted))
(check "vacuous precondition inapplicable" (equal (car (p107-c-verify c-vac)) 'inapplicable))
(check "frame violation refuted" (equal (car (p107-c-verify c-frame)) 'refuted))
(check "undeclared assign is invalid" (equal (car (p107-c-verify c-bad)) 'invalid))
(define ok-cases (p107-nth (p107-c-verify c-ok) 1))
(check "checker accepts the real table" (p107-c-check c-ok ok-cases))
(check "checker rejects a forged output"
  (not (p107-c-check c-ok (list (list 'case (list 1 1) (list 0 0))
                                (list 'case (list 1 0) (list 0 0))
                                (list 'case (list 0 1) (list 0 0))
                                (list 'case (list 0 0) (list 0 0))))))
(check "checker rejects a missing row"
  (not (p107-c-check c-ok (cdr ok-cases))))
(check "checker rejects a duplicated row"
  (not (p107-c-check c-ok (cons (car ok-cases) ok-cases))))
(check "checker rejects a non-boolean input row"
  (not (p107-c-check c-ok (list (list 'case (list 1 2) (list 1 1))))))

;;; ---------- 10. if: every feasible branch is checked ----------
(define c-if (list 'c107 'iff (list 'c 'f) '(b 1)
  (list (list 'if '(v c) (list '(assign f 1)) (list '(assign f 0))))
  (list 'or (list 'and '(v c) '(v f)) (list 'and (list 'not '(v c)) (list 'not '(v f))))
  (list 'f)))
(check "if with both branches verifies" (equal (car (p107-c-verify c-if)) 'verified))
(check "if produces one case per eligible input"
  (= 4 (p107-len (p107-nth (p107-c-verify c-if) 1))))
(check "if outputs contain both branch results"
  (let ((outs (p107-map (lambda (k) (p107-nth k 2)) (p107-nth (p107-c-verify c-if) 1))))
    (and (p107-member? (list 1 1) outs) (p107-member? (list 0 0) outs))))
(define c-if-bad (list 'c107 'ifbad (list 'c 'f) '(b 1)
  (list (list 'if '(v c) (list '(assign f 1)) ()))
  (list 'and '(v c) '(v f))
  (list 'f)))
(check "feasible else branch that violates Post is refuted"
  (equal (car (p107-c-verify c-if-bad)) 'refuted))
(define c-if-invalid (list 'c107 'ifinv (list 'c) '(b 1)
  (list (list 'if '(v q) (list '(assign c 1)) ())) '(b 1) (list 'c)))
(check "if on an undeclared variable is invalid"
  (equal (car (p107-c-verify c-if-invalid)) 'invalid))

;;; ---------- 11. call summaries over a prefix-checked library ----------
;;; The callee summary is the verified case table. A call applies a row; it
;;; never re-runs the callee body.
(define cc-clear (list 'c107 'clear (list 'b) '(b 1)
  (list '(assign b 0)) '(not (v b)) (list 'b)))
(define cc-clear-cases (p107-nth (p107-c-verify cc-clear) 1))
(define cc-clear-unit (list 'unit107 'clear cc-clear cc-clear-cases))
(define cc-lib (list cc-clear-unit))
(check "callee summary verifies" (equal (car (p107-c-verify cc-clear)) 'verified))
(check "callee has one row per Boolean input" (= 2 (p107-len cc-clear-cases)))
(check "checked library accepts the exact summary"
  (equal (car (p107-c-lib-check cc-lib)) 'ok))

(define cc-caller (list 'c107 'caller (list 'a 'b) '(v b)
  (list '(call clear)) '(not (v b)) (list 'b)))
(define cc-caller-r (p107-c-verify-lib cc-caller cc-lib))
(define cc-caller-cases (p107-nth cc-caller-r 1))
(check "caller verifies against the checked library" (equal (car cc-caller-r) 'verified))
(check "environment construction stays separate from update"
  (and (equal (p107-c-env (list 'x 'y) (list 1 0)) '((x 1) (y 0)))
       (equal (p107-c-update (p107-c-env (list 'x 'y) (list 1 0)) 'y 1) '((x 1) (y 1)))))
(check "eligible inputs are exactly the Pre-satisfying states"
  (p107-set-equal? (p107-c-eligible cc-caller) (list (list 1 1) (list 0 1))))
(check "call changes the callee bit and preserves the rest of the state"
  (and (= 2 (p107-len cc-caller-cases))
       (p107-member? (list 'case (list 1 1) (list 1 0)) cc-caller-cases)
       (p107-member? (list 'case (list 0 1) (list 0 0)) cc-caller-cases)))
(check "caller table is accepted by the public checker"
  (p107-c-check-lib cc-caller cc-caller-cases cc-lib))

;;; Reuse accounting: the direct evaluator applies one row with lib checked
;;; once; the public boundary re-validates the whole prefix before evaluating.
(p107-c-reset-stats)
(define cc-run (p107-c-run (list '(call clear)) (list (list 'a 1) (list 'b 1)) cc-lib))
(check "call applies a summary row" (equal cc-run '(ok ((a 1) (b 0)))))
(check "call does not re-execute the callee body"
  (and (= *p107-c-applied* 1) (= *p107-c-verified* 0) (= *p107-c-call-runs* 1)))
(p107-c-reset-stats)
(define cc-pub (p107-c-verify-lib cc-caller cc-lib))
(check "public boundary revalidates the prefix, then the caller"
  (and (equal (car cc-pub) 'verified) (= *p107-c-verified* 2) (= *p107-c-applied* 2)))

;;; Nested calls: `top` calls `mid`, which called `clear` when its own summary was
;;; verified. A top-level call must still consume only `mid`'s summary row.
(define cc-mid (list 'c107 'mid (list 'b) '(b 1)
  (list '(call clear)) '(not (v b)) (list 'b)))
(define cc-lib3 (list cc-clear-unit
  (list 'unit107 'mid cc-mid (p107-nth (p107-c-verify-lib cc-mid cc-lib) 1))))
(define cc-top (list 'c107 'top (list 'a 'b) '(v b)
  (list '(call mid)) '(not (v b)) (list 'b)))
(check "nested calls verify through checked summaries"
  (equal (car (p107-c-verify-lib cc-top cc-lib3)) 'verified))
(p107-c-reset-stats)
(check "nested call applies one row and re-runs no callee body"
  (and (equal (p107-c-run (list '(call mid)) (list (list 'a 1) (list 'b 1)) cc-lib3)
              '(ok ((a 1) (b 0))))
       (= *p107-c-applied* 1) (= *p107-c-verified* 0) (= *p107-c-call-runs* 1)))

;;; Evidence binds the result to the exact library it was checked against.
(define cc-ev (p107-c-evidence cc-caller cc-lib))
(check "evidence re-checks in the same library"
  (equal (p107-c-check-evidence cc-ev cc-lib) '(ok)))
(define cc-clear2 (list 'c107 'clear (list 'b) '(b 1)
  (list '(assign b 1)) '(v b) (list 'b)))
(define cc-lib2 (list (list 'unit107 'clear cc-clear2
  (p107-nth (p107-c-verify cc-clear2) 1))))
(check "a changed callee makes old evidence stale"
  (equal (p107-c-check-evidence cc-ev cc-lib2) '(invalid stale-library)))
(check "old caller table is rejected under the changed callee"
  (not (p107-c-check-lib cc-caller cc-caller-cases cc-lib2)))

;;; A callee precondition counterexample is `refuted`, not `invalid`, and the
;;; input plus cause survive from run to verify.
(define cc-need (list 'c107 'needflag (list 'flag) '(v flag)
  (list '(assign flag 1)) '(v flag) (list 'flag)))
(define cc-need-unit (list 'unit107 'needflag cc-need
  (p107-nth (p107-c-verify cc-need) 1)))
(define cc-need-lib (list cc-need-unit))
(define cc-need-caller (list 'c107 'needcaller (list 'flag) '(b 1)
  (list '(call needflag)) '(v flag) (list 'flag)))
(define cc-need-r (p107-c-verify-lib cc-need-caller cc-need-lib))
(check "direct call precondition failure is refuted"
  (equal (p107-c-run (list '(call needflag)) (list (list 'flag 0)) cc-need-lib)
         '(refuted call-precondition needflag)))
(check "verify-lib preserves the refuted call-precondition tag"
  (and (equal (car cc-need-r) 'refuted)
       (equal (p107-nth cc-need-r 1) (list 0))
       (equal (p107-nth cc-need-r 2) 'call-precondition)
       (equal (p107-nth cc-need-r 3) 'needflag)))
(check "refuted is never wrapped as invalid"
  (not (equal (car cc-need-r) 'invalid)))

;;; Library boundary: forged/empty summaries, duplicate names, forward and
;;; self calls, and interface mismatches are all rejected.
(define cc-forged-lib (list (list 'unit107 'clear cc-clear2 cc-clear-cases)))
(check "a summary that does not match its contract is rejected"
  (equal (p107-c-lib-check cc-forged-lib) '(invalid summary-mismatch clear)))
(check "public verify refuses an unchecked/forged library"
  (equal (p107-c-verify-lib cc-caller cc-forged-lib) '(invalid library summary-mismatch clear)))
(check "public check refuses a forged library"
  (not (p107-c-check-lib cc-caller cc-caller-cases cc-forged-lib)))
(check "an empty summary for a non-inapplicable contract is rejected"
  (equal (p107-c-lib-check (list (list 'unit107 'needflag cc-need ())))
         '(invalid summary-mismatch needflag)))
(check "duplicate unit names are rejected"
  (equal (p107-c-lib-check (list cc-clear-unit cc-clear-unit))
         '(invalid duplicate-unit clear)))
(define cc-vac (list 'c107 'vac (list 'x) (list 'and '(v x) '(not (v x)))
  (list '(assign x 1)) '(b 1) (list 'x)))
(check "an inapplicable unit with an empty summary is accepted"
  (equal (car (p107-c-lib-check (list (list 'unit107 'vac cc-vac ())))) 'ok))
(check "the checker accepts the empty table of an inapplicable contract"
  (p107-c-check cc-vac ()))
(define cc-forward (list 'c107 'forward (list 'b) '(b 1)
  (list '(call later)) '(b 1) (list 'b)))
(check "a forward dependency is rejected"
  (p107-member? 'unknown-unit
    (p107-c-lib-check (list (list 'unit107 'forward cc-forward ())))))
(define cc-self (list 'c107 'selfc (list 'b) '(b 1)
  (list '(call selfc)) '(b 1) (list 'b)))
(check "a self dependency is rejected"
  (p107-member? 'unknown-unit
    (p107-c-lib-check (list (list 'unit107 'selfc cc-self ())))))
(define cc-iface (list 'c107 'iface (list 'a) '(b 1)
  (list '(call clear)) '(b 1) (list 'a)))
(check "a callee variable missing from the caller is an interface error"
  (let ((r (p107-c-verify-lib cc-iface cc-lib)))
    (and (equal (car r) 'invalid) (p107-member? 'interface r))))
(define cc-unknown (list 'c107 'unk (list 'a) '(b 1)
  (list '(call nope)) '(b 1) (list 'a)))
(check "an unknown unit at call time is invalid"
  (let ((r (p107-c-verify-lib cc-unknown cc-lib)))
    (and (equal (car r) 'invalid) (p107-member? 'unknown-unit r))))

;;; Inherited IR weaknesses from the 0.0112 review: distinct variables and
;;; exact arity are now enforced, and the checker compares tables exactly.
(check "duplicate declared variables are invalid"
  (not (p107-c-valid? (list 'c107 'dupv (list 'x 'x) '(b 1)
    (list '(assign x 1)) '(v x) (list 'x)))))
(check "extra expression arity is invalid"
  (not (p107-c-valid? (list 'c107 'dupa (list 'x) '(b 1)
    (list '(assign x 1)) '(b 1 0) (list 'x)))))
(check "a call with extra arguments is not a valid body"
  (not (p107-c-valid? (list 'c107 'dupc (list 'x) '(b 1)
    (list (list 'call 'x 'y)) '(b 1) (list 'x)))))
(check "the checker rejects a duplicated input row of the right length"
  (not (p107-c-check (list 'c107 'duprow (list 'x 'y) '(b 1)
    (list '(assign x 1)) '(v x) (list 'x))
    (list (list 'case (list 1 1) (list 1 1)) (list 'case (list 1 1) (list 1 1))
          (list 'case (list 1 0) (list 1 0)) (list 'case (list 0 0) (list 0 0))))))


;;; ---------- 12. evidence RESULT is validated, not just its table ----------
(check "evidence with an integer RESULT is cleanly rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-caller 1 ()) ())
         '(invalid evidence-result)))
(check "evidence with a dotted RESULT is cleanly rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-caller (cons 'verified 1) ()) ())
         '(invalid evidence-result)))
(check "evidence with a symbol RESULT is cleanly rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-caller 'verified ()) ())
         '(invalid evidence-result)))
(check "evidence with an empty RESULT is cleanly rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-caller () ()) ())
         '(invalid evidence-result)))
(check "a refuted tag over correct cases is rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-caller
          (list 'refuted cc-caller-cases) cc-lib) cc-lib)
         '(invalid evidence-result)))
(check "an unknown tag over correct cases is rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-caller
          (list 'unknown cc-caller-cases) cc-lib) cc-lib)
         '(invalid evidence-result)))
(check "verified evidence with an extra RESULT field is rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-caller
          (list 'verified cc-caller-cases 'extra) cc-lib) cc-lib)
         '(invalid evidence-result)))
(check "verified evidence for an inapplicable contract is rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-vac (list 'verified ()) ()) ())
         '(invalid evidence-mismatch)))
(check "verified evidence with a wrong table is rejected"
  (equal (p107-c-check-evidence (list 'evidence cc-caller
          (list 'verified ()) cc-lib) cc-lib)
         '(invalid evidence-mismatch)))
(check "the real evidence still passes"
  (equal (p107-c-check-evidence cc-ev cc-lib) '(ok)))

;;; ---------- 13. bounded finite Boolean input ----------
(define-function cc-repeat (s n) (if (= n 0) () (cons s (cc-repeat s (- n 1)))))
(define-function cc-deep (n) (if (= n 0) '(b 1) (list 'not (cc-deep (- n 1)))))
(define cc-vars8 '(v1 v2 v3 v4 v5 v6 v7 v8))
(define cc-vars9 '(v1 v2 v3 v4 v5 v6 v7 v8 v9))
(define cc-vars14 '(v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14))
(define cc-id8 (list 'c107 'id8 cc-vars8 '(b 1) () '(b 1) ()))
(define cc-id9 (list 'c107 'id9 cc-vars9 '(b 1) () '(b 1) ()))
(define cc-id14 (list 'c107 'id14 cc-vars14 '(b 1) () '(b 1) ()))
(check "8 variables (256 states) verify" (equal (car (p107-c-verify cc-id8)) 'verified))
(check "8 variables produce 256 cases"
  (= 256 (p107-len (p107-nth (p107-c-verify cc-id8) 1))))
(check "9 variables are a clean variable-limit rejection"
  (equal (p107-c-verify cc-id9) '(invalid unsupported-limit vars)))
(check "14 variables are a clean variable-limit rejection"
  (equal (p107-c-verify cc-id14) '(invalid unsupported-limit vars)))
(define cc-stmts32 (list 'c107 's32 (list 'x) '(b 1)
  (cc-repeat '(assign x 1) 32) '(v x) (list 'x)))
(check "32 statements are accepted" (equal (car (p107-c-verify cc-stmts32)) 'verified))
(check "33 statements are a clean statement-limit rejection"
  (equal (p107-c-verify (list 'c107 's33 (list 'x) '(b 1)
          (cc-repeat '(assign x 1) 33) '(v x) (list 'x)))
         '(invalid unsupported-limit statements)))
(check "an over-long if branch is a clean statement-limit rejection"
  (equal (p107-c-verify (list 'c107 'if33 (list 'x) '(b 1)
          (list (list 'if '(v x) (cc-repeat '(assign x 1) 33) ())) '(v x) (list 'x)))
         '(invalid unsupported-limit statements)))
(define cc-d2 (list 'c107 'd2 (list 'x) (cc-deep 2) () (cc-deep 2) ()))
(check "nested expressions within the depth limit verify"
  (equal (car (p107-c-verify cc-d2)) 'verified))
(check "excessive expression depth is a clean depth-limit rejection"
  (equal (p107-c-verify (list 'c107 'd20 (list 'x) (cc-deep 20) () (cc-deep 20) ()))
         '(invalid unsupported-limit depth)))
(define cc-if32 (cc-repeat (list 'if '(v x) (list '(assign x 1)) (list '(assign x 0))) 32))
(check "an over-large IR is a clean node-limit rejection"
  (equal (p107-c-verify (list 'c107 'n32 (list 'x) '(b 1) cc-if32 '(v x) (list 'x)))
         '(invalid unsupported-limit nodes)))
(define cc-units17 (p107-map (lambda (i) cc-clear-unit) (p107-range 17)))
(check "17 library units are a clean unit-limit rejection"
  (equal (p107-c-lib-check cc-units17) '(invalid unsupported-limit units)))
(define cc-many-cases (p107-map (lambda (i) (list 'case (list 0) (list 0))) (p107-range 257)))
(check "257 summary rows are a clean case-limit rejection"
  (equal (p107-c-lib-check (list (list 'unit107 'clear cc-clear cc-many-cases)))
         '(invalid unsupported-limit cases)))
(check "the public table checker bounds case count"
  (not (p107-c-check cc-clear cc-many-cases)))
(define cc-long-row (list 'case (p107-map (lambda (i) 0) (p107-range 1000)) (list 1)))
(check "an over-long case row is rejected without full traversal"
  (not (p107-c-check cc-clear (list cc-long-row))))


;;; ---------- 14. Shen-inspired surface notation (contracts/units) ----------
(define sc-form
  '(contract surfclear (b)
     (pre (b 1))
     (body ((assign b 0)))
     (post (not (v b)))
     (frame (b))))
(define sc-r (p107-sc sc-form))
(check "surface contract expands" (equal (car sc-r) 'ok))
(define sc-c (p107-nth sc-r 1))
(check "surface contract equals canonical"
  (equal sc-c (list 'c107 'surfclear (list 'b) '(b 1)
                    '((assign b 0)) '(not (v b)) (list 'b))))
(check "surface contract revalidates and verifies"
  (equal (car (p107-c-verify sc-c)) 'verified))
(check "surface contract round-trips"
  (equal (p107-sc (p107-sc-write sc-c)) (list 'ok sc-c)))
(check "surface contract rejects a dotted value"
  (equal (p107-sc (cons 'contract 'x)) '(invalid surface-shape)))
(check "surface contract rejects a missing field"
  (equal (p107-sc '(contract x (b) (pre (b 1)) (body ()) (post (b 1))))
         '(invalid surface-shape)))
(check "surface contract rejects an extra field"
  (equal (p107-sc (p107-append sc-form (list '(extra 1))))
         '(invalid surface-shape)))
(check "surface contract rejects an invalid body"
  (equal (p107-sc '(contract bad (b) (pre (b 1)) (body ((assign q 1)))
                             (post (b 1)) (frame (b))))
         '(invalid contract)))
(define su-form (list 'unit 'surfclear sc-form
                      (list (list 'case (list 1) (list 0)))))
(define su-r (p107-su su-form))
(check "surface unit expands" (equal (car su-r) 'ok))
(define su-u (p107-nth su-r 1))
(check "surface unit equals canonical"
  (equal su-u (list 'unit107 'surfclear sc-c
                    (list (list 'case (list 1) (list 0))))))
(check "surface unit round-trips"
  (equal (p107-su (p107-su-write su-u)) (list 'ok su-u)))
(check "surface unit enforces the repeated name"
  (equal (p107-su (list 'unit 'other sc-form ())) '(invalid surface-shape)))


;;; ---------- 15. surface notation for checked definitions ----------
(define sd-form
  '(define surfp (x)
     (pattern ((atom p ((var x)))))
     (body ((atom p ((var x)))))))
(define sd-r (p107-sd sd-form))
(check "surface definition expands" (equal (car sd-r) 'ok))
(define sd-d (p107-nth sd-r 1))
(check "surface definition equals canonical"
  (equal sd-d (list 'def107 'surfp (list 'x)
                    '((atom p ((var x)))) '((atom p ((var x)))))))
(check "surface definition passes the canonical validator" (p107-def? sd-d))
(check "surface definition round-trips"
  (equal (p107-sd (p107-sd-write sd-d)) (list 'ok sd-d)))
(define sdc-form
  '(define callp (x)
     (pattern ((atom q ((var x)))))
     (body ((call d1 ((var x)))))))
(define sdc-r (p107-sd sdc-form))
(check "surface definition maps call to call107"
  (equal (p107-nth sdc-r 1)
         (list 'def107 'callp (list 'x)
               '((atom q ((var x)))) '((call107 d1 ((var x)))))))
(check "surface definition call form round-trips"
  (equal (p107-sd (p107-sd-write (p107-nth sdc-r 1))) (list 'ok (p107-nth sdc-r 1))))
(check "surface definition rejects a missing field"
  (equal (p107-sd '(define x (y) (pattern ((atom p ((var y)))))))
         '(invalid surface-shape)))
(check "canonical definition body steps are validated"
  (not (p107-def? (list 'def107 'bad (list 'x)
                        '((atom p ((var x)))) '((assign x 1))))))
(check "surface definition rejects an invalid body"
  (equal (p107-sd '(define bad (x) (pattern ((atom p ((var x)))))
                            (body ((assign x 1)))))
         '(invalid definition)))


;;; ---------- 16. total public patterns and exact call arity ----------
(check "malformed answer pattern is rejected"
  (equal (dlm 'answer 's 'not-a-pattern) '(rejected107 pattern)))
(check "malformed plan pattern is rejected"
  (equal (dlm 'plan 'not-a-pattern) '(rejected107 pattern)))
(check "malformed revise pattern is rejected"
  (equal (dlm 'revise 'missing 'not-a-pattern) '(rejected107 pattern)))
(check "a dotted pattern is rejected at the command boundary"
  (equal (car (dlm 'plan (cons 'atom 'x))) 'rejected107))
(check "the plan API refuses a malformed pattern"
  (equal (p107-nth (p107-plan *p107-state* 'not-a-pattern) 2) 'invalid))
(check "the answer API refuses a malformed pattern"
  (equal (p107-nth (p107-answer *p107-state* 'demo 'not-a-pattern 200000) 2) 'invalid))
(check "query-pattern rejects a dotted list"
  (not (p107-query-pattern? (cons (p107-atom 'q ()) 'x))))
(check "query-pattern rejects a disconnected pattern"
  (not (p107-query-pattern?
         (list (p107-atom 'q (list (p107-var 'x)))
               (p107-atom 'r (list (p107-var 'y)))))))

;;; 0.0110 review F5: admission and execution must use the same arity rule.
(define f5-d1 (p107-def 'f5d1 (list (p107-var 'x))
  (list (p107-atom 'q (list (p107-var 'x))))
  (list (p107-atom 'q (list (p107-var 'x))))))
(define f5-bad (p107-def 'f5bad (list (p107-var 'y))
  (list (p107-atom 'q (list (p107-var 'y))))
  (list (p107-call 'f5d1 (list (p107-var 'y) (p107-var 'y))))))
(define f5-ok (p107-def 'f5ok (list (p107-var 'y))
  (list (p107-atom 'q (list (p107-var 'y))))
  (list (p107-call 'f5d1 (list (p107-var 'y))))))
(check "admission rejects extra actuals" (not (p107-def-ok? f5-bad (list f5-d1))))
(check "admission accepts exact arity" (p107-def-ok? f5-ok (list f5-d1)))
(check "expansion rejects extra actuals"
  (equal (p107-expand (p107-def-body f5-bad) (list f5-d1) 0) 'expand-failed))


;;; ---------- 17. assert: a proof obligation inside a body ----------
(define ca-ok (list 'c107 'caok (list 'b) '(b 1)
  (list '(assert (b 1)) '(assign b 0) '(assert (not (v b))))
  '(not (v b)) (list 'b)))
(check "a true assert verifies" (equal (car (p107-c-verify ca-ok)) 'verified))
(define ca-bad (list 'c107 'cabad (list 'b) '(b 1)
  (list '(assert (not (v b))) '(assign b 1)) '(v b) (list 'b)))
(define ca-bad-r (p107-c-verify ca-bad))
(check "a false assert is refuted"
  (and (equal (car ca-bad-r) 'refuted) (equal (p107-nth ca-bad-r 2) 'assert)))
(check "the assert counterexample carries its input"
  (equal (p107-nth ca-bad-r 1) (list 1)))
(define ca-if-ok (list 'c107 'caifok (list 'c 'b) '(b 1)
  (list (list 'if '(v c)
              (list '(assert (v c)))
              (list '(assert (not (v c))))))
  '(b 1) ()))
(check "assert is allowed in both if branches"
  (equal (car (p107-c-verify ca-if-ok)) 'verified))
(define ca-inv (list 'c107 'cainv (list 'b) '(b 1)
  (list '(assert (v q))) '(b 1) (list 'b)))
(check "assert on an undeclared variable is invalid"
  (equal (car (p107-c-verify ca-inv)) 'invalid))
(check "assert with extra fields is invalid"
  (equal (car (p107-c-verify (list 'c107 'cabad2 (list 'b) '(b 1)
    (list '(assert (b 1) extra)) '(b 1) (list 'b)))) 'invalid))
(define ca-form
  '(contract surfassert (b)
     (pre (b 1))
     (body ((assert (b 1)) (assign b 0)))
     (post (not (v b)))
     (frame (b))))
(define ca-c (p107-nth (p107-sc ca-form) 1))
(check "surface contract accepts assert"
  (equal (car (p107-c-verify ca-c)) 'verified))

(if (= *failures* 0) (print "ALL-CORE-TESTS-PASSED\n") (print "FAILURES " *failures* "\n"))
