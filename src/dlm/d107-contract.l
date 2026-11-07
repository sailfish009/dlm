;;; d107-contract.l — Silicon-shaped contract layer on the minimal core.
;;;
;;; Definition order (Maru resolves names when a definition is created; there
;;; are no forward references and no mutual recursion):
;;;
;;;   Boolean IR + env  ->  update-all / summary application  ->  core evaluator
;;;   ->  universal scan  ->  prefix library checker  ->  public boundary
;;;
;;; Trust boundary:
;;;   * `p107-c-run` takes an EXPLICIT, already-checked library. There is no
;;;     ambient global, so the evaluator cannot silently read a library other
;;;     than the one the checker validated.
;;;   * A raw unit is (unit107 NAME CONTRACT CASES). `p107-c-lib-check`
;;;     verifies units in prefix order and requires CASES to equal the table the
;;;     verifier recomputes under that prefix. There is no `admitted` flag to
;;;     forge and no digest to trust.
;;;   * `p107-c-verify-lib` / `p107-c-check-lib` validate first and only then
;;;     run, so the prefix the evaluator sees is exactly the checked prefix.
;;;   * Evidence is (evidence CONTRACT RESULT LIB). The RESULT must be exactly
;;;     (verified CASES); `p107-c-check-evidence` recomputes the full result
;;;     under LIB and requires exact equality. A changed library reports
;;;     `stale-library` instead of reusing old proof.
;;;
;;; Result tags are propagated, never coarsened:
;;;   invalid  = malformed contract / interface / unit / unsupported size
;;;   refuted  = a valid input that violates Pre, Post, frame, or a callee Pre
;;;   unknown  = resource exhaustion (reserved; not produced by this verifier)
;;;
;;; Bounded finite Boolean: the verifier never enumerates outside the limits
;;; below. Over-limit input is (invalid unsupported-limit KIND), not a stack
;;; overflow. `unknown` is propagated by the evaluator but this layer has no
;;; budget scheduler, so it is never produced here.
;;;
;;; Counters (`*p107-c-*`) make reuse auditable: a `(call NAME)` applies one
;;; summary row and never re-executes the callee body.

(define *p107-c-applied* 0)    ; summary rows applied by (call NAME)
(define *p107-c-verified* 0)   ; contracts verified by p107-c-verify-with
(define *p107-c-call-runs* 0)  ; (call NAME) statements executed

;;; ------------------------------------------------------------------ Boolean IR

(define-function p107-b? (x) (or (= x 0) (= x 1)))
(define-function p107-c-env (vars vals)
  (if (not vars) ()
    (cons (list (car vars) (car vals)) (p107-c-env (cdr vars) (cdr vals)))))
(define-function p107-c-update (env v x)
  (let ((out ()) (found false))
    (list-do p env
      (if (equal (car p) v) (begin (set out (p107-append out (list (list v x)))) (set found true))
        (set out (p107-append out (list p)))))
    (if found out 'missing-var)))
(define-function p107-c-get (env v) (let ((h (p107-assoc v env))) (if h (p107-nth h 1) 'missing-var)))
(define-function p107-c-index (vars env) (p107-map (lambda (v) (p107-c-get env v)) vars))

;;; ------------------------------------------------------------------ limits
;;; Supported language, stated as data. 2^MAX_VARS = MAX_STATES.
(define *p107-c-max-vars* 8)     ; 256 Boolean states
(define *p107-c-max-states* 256)
(define *p107-c-max-stmts* 32)   ; statements in a body or an if branch
(define *p107-c-max-nodes* 512)  ; cons cells in one contract
(define *p107-c-max-depth* 16)   ; expression nesting
(define *p107-c-max-units* 16)   ; units in one library
(define *p107-c-max-cases* 256)  ; rows in one summary table

;;; Bounded length: recursion stops at n+1, so deciding that a list is too long
;;; cannot itself exhaust the call stack.
(define-function p107-c-len<= (xs n)
  (if (not (pair? xs)) true
    (if (= n 0) false
      (p107-c-len<= (cdr xs) (- n 1)))))

(define-function p107-c-pow2 (n)
  (let ((r 1) (i 0)) (while (< i n) (set r (* r 2)) (set i (+ i 1))) r))

;;; Depth is tested *before* descending further.
(define-function p107-c-too-deep? (x d)
  (or (> d *p107-c-max-depth*)
      (and (pair? x)
           (or (p107-c-too-deep? (car x) (+ d 1))
               (p107-c-too-deep? (cdr x) (+ d 1))))))

(define-function p107-c-nodes (x)
  (if (pair? x) (+ 1 (p107-c-nodes (car x)) (p107-c-nodes (cdr x))) 1))

;;; ------------------------------------------------------------------ expressions

(define-function p107-c-var? (x vars) (and (symbol? x) (p107-member? x vars)))

;;; Exact arity is required: (b 1), (v x), (not E), (and E1 E2), (or E1 E2).
;;; Depth is bounded before recursing, so a deeply nested term is rejected
;;; rather than exhausting the call stack.
(define-function p107-c-expr-depth? (e vars d)
  (and (<= d *p107-c-max-depth*)
       (cond ((not (pair? e)) false)
             ((equal (car e) 'b) (and (p107-shape? e 2) (p107-b? (p107-nth e 1))))
             ((equal (car e) 'v) (and (p107-shape? e 2) (p107-c-var? (p107-nth e 1) vars)))
             ((equal (car e) 'not) (and (p107-shape? e 2)
                                        (p107-c-expr-depth? (p107-nth e 1) vars (+ d 1))))
             ((or (equal (car e) 'and) (equal (car e) 'or))
              (and (p107-shape? e 3)
                   (p107-c-expr-depth? (p107-nth e 1) vars (+ d 1))
                   (p107-c-expr-depth? (p107-nth e 2) vars (+ d 1))))
             (else false))))
(define-function p107-c-expr? (e vars) (p107-c-expr-depth? e vars 0))

(define-function p107-c-val (e env)
  (cond ((equal (car e) 'b) (p107-nth e 1))
        ((equal (car e) 'v) (p107-c-get env (p107-nth e 1)))
        ((equal (car e) 'not) (- 1 (p107-c-val (p107-nth e 1) env)))
        ((equal (car e) 'and) (if (and (= (p107-c-val (p107-nth e 1) env) 1)
                                       (= (p107-c-val (p107-nth e 2) env) 1)) 1 0))
        (else (if (or (= (p107-c-val (p107-nth e 1) env) 1)
                      (= (p107-c-val (p107-nth e 2) env) 1)) 1 0))))

(define-function p107-c-states (vars)
  (if (not vars) (list ())
    (let ((out ()) (rest (p107-c-states (cdr vars))))
      (list-do r rest
        (set out (p107-append out (list (cons (list (car vars) 1) r) (cons (list (car vars) 0) r)))))
      out)))

;;; ------------------------------------------------------------------ contract IR

(define-function p107-c-flat-stmt? (s vars)
  ;; branch bodies may assign or assert; nested if stays out of this step
  (or (and (p107-shape? s 3) (equal (car s) 'assign)
           (p107-c-var? (p107-nth s 1) vars) (p107-b? (p107-nth s 2)))
      (and (p107-shape? s 2) (equal (car s) 'assert)
           (p107-c-expr? (p107-nth s 1) vars))))
(define-function p107-c-flat? (body vars)
  (and (p107-list? body)
       (p107-c-len<= body *p107-c-max-stmts*)
       (not (p107-any? (lambda (s) (not (p107-c-flat-stmt? s vars))) body))))
(define-function p107-c-stmt? (s vars)
  (cond ((not (pair? s)) false)
        ((equal (car s) 'assign)
         (and (p107-shape? s 3) (p107-c-var? (p107-nth s 1) vars) (p107-b? (p107-nth s 2))))
        ((equal (car s) 'assert)
         (and (p107-shape? s 2) (p107-c-expr? (p107-nth s 1) vars)))
        ((equal (car s) 'if)
         (and (p107-shape? s 4)
              (p107-c-len<= (p107-nth s 2) *p107-c-max-stmts*)
              (p107-c-len<= (p107-nth s 3) *p107-c-max-stmts*)
              (p107-c-expr? (p107-nth s 1) vars)
              (p107-c-flat? (p107-nth s 2) vars) (p107-c-flat? (p107-nth s 3) vars)))
        ((equal (car s) 'call)
         (and (p107-shape? s 2) (symbol? (p107-nth s 1))))
        (else false)))
(define-function p107-c-body? (body vars)
  (and (p107-list? body)
       (p107-c-len<= body *p107-c-max-stmts*)
       (not (p107-any? (lambda (s) (not (p107-c-stmt? s vars))) body))))

;;; Declared variables must be distinct: the input space is a product of
;;; distinct Boolean variables, not a multiset.
(define-function p107-c-distinct? (xs)
  (if (not (pair? xs)) true
    (and (not (p107-member? (car xs) (cdr xs))) (p107-c-distinct? (cdr xs)))))

;;; Size checks that need list shape but must stay total on malformed input.
;;; A branch or body longer than the statement limit is reported as a limit,
;;; not traversed.
(define-function p107-c-branch-len-ok? (body)
  (if (not (pair? body)) true
    (let ((s (car body)))
      (and (or (not (and (p107-shape? s 4) (equal (car s) 'if)))
               (and (p107-c-len<= (p107-nth s 2) *p107-c-max-stmts*)
                    (p107-c-len<= (p107-nth s 3) *p107-c-max-stmts*)))
           (p107-c-branch-len-ok? (cdr body))))))

(define-function p107-c-body-too-deep? (body)
  (if (not (pair? body)) false
    (let ((s (car body)))
      (or (and (p107-shape? s 4) (equal (car s) 'if)
               (p107-c-too-deep? (p107-nth s 1) 0))
          (p107-c-body-too-deep? (cdr body))))))

(define-function p107-c-limit (c)
  (if (not (and (p107-shape? c 7) (equal (car c) 'c107))) ()
    (let ((vars (p107-nth c 2)) (body (p107-nth c 4)) (frame (p107-nth c 6)))
      (cond
        ((not (p107-list? vars)) ())
        ((not (p107-c-len<= vars *p107-c-max-vars*)) 'vars)
        ((> (p107-c-pow2 (p107-len vars)) *p107-c-max-states*) 'states)
        ((not (p107-list? body)) ())
        ((not (p107-c-len<= body *p107-c-max-stmts*)) 'statements)
        ((not (p107-c-len<= frame *p107-c-max-vars*)) 'frame)
        ((not (p107-c-branch-len-ok? body)) 'statements)
        ((p107-c-too-deep? (p107-nth c 3) 0) 'depth)
        ((p107-c-too-deep? (p107-nth c 5) 0) 'depth)
        ((p107-c-body-too-deep? body) 'depth)
        ((> (p107-c-nodes c) *p107-c-max-nodes*) 'nodes)
        (else ())))))

(define-function p107-c-valid? (c)
  (and (equal (p107-c-limit c) ())
       (p107-shape? c 7) (equal (car c) 'c107) (symbol? (p107-nth c 1))
       (p107-list? (p107-nth c 2))
       (p107-c-distinct? (p107-nth c 2))
       (not (p107-any? (lambda (v) (not (and (symbol? v) (not (equal v ()))))) (p107-nth c 2)))
       (p107-c-expr? (p107-nth c 3) (p107-nth c 2))
       (p107-c-body? (p107-nth c 4) (p107-nth c 2))
       (p107-c-expr? (p107-nth c 5) (p107-nth c 2))
       (p107-list? (p107-nth c 6))
       (p107-c-distinct? (p107-nth c 6))
       (not (p107-any? (lambda (v) (not (p107-member? v (p107-nth c 2)))) (p107-nth c 6)))))

;;; ------------------------------------------------------------------ library

;;; Raw unit: (unit107 NAME CONTRACT CASES). A checked library is simply the
;;; prefix of units that passed p107-c-lib-check; the record carries no marker.
(define-function p107-c-unit-ok? (m)
  (and (p107-shape? m 4) (equal (car m) 'unit107)
       (symbol? (p107-nth m 1))
       (p107-list? (p107-nth m 3))
       (p107-c-len<= (p107-nth m 3) *p107-c-max-cases*)
       (p107-c-valid? (p107-nth m 2))
       (equal (p107-nth m 1) (p107-nth (p107-nth m 2) 1))))

(define-function p107-c-lib-find (lib name)
  (if (not (pair? lib)) ()
    (let ((m (car lib)))
      (if (and (p107-shape? m 4) (equal (p107-nth m 1) name)) m
        (p107-c-lib-find (cdr lib) name)))))

;;; Apply a checked summary row to the caller environment. The callee contract
;;; variables must already exist in the caller state and be Boolean; a missing
;;; eligible row means the caller does not establish the callee Pre.
(define-function p107-c-update-all (vars vals env)
  (if (not vars) env
    (let ((e (p107-c-update env (car vars) (car vals))))
      (if (equal e 'missing-var) 'missing-var
        (p107-c-update-all (cdr vars) (cdr vals) e)))))

(define-function p107-c-apply (m env)
  (let* ((c (p107-nth m 2)) (name (p107-nth m 1)) (vars (p107-nth c 2))
         (cases (p107-nth m 3)) (ok true) (in ()) (out 'no-row))
    (list-do v vars
      (let ((val (p107-c-get env v)))
        (if (or (not (is <long> val)) (not (p107-b? val))) (set ok false))))
    (if (not ok) (list 'invalid 'interface name)
      (begin
        (set in (p107-c-index vars env))
        (list-do k cases
          (if (and (equal out 'no-row) (p107-shape? k 3) (equal (p107-nth k 1) in))
            (set out (p107-nth k 2))))
        (cond
          ((equal out 'no-row) (list 'refuted 'call-precondition name))
          ((or (not (p107-list? out)) (not (= (p107-len out) (p107-len vars))))
           (list 'invalid 'summary-row name))
          (else
            (let ((e2 (p107-c-update-all vars out env)))
              (if (equal e2 'missing-var) (list 'invalid 'interface name)
                (begin
                  (set *p107-c-applied* (+ *p107-c-applied* 1))
                  (list 'ok e2))))))))))

;;; Core evaluator. `lib` is the checked prefix; a (call NAME) consumes its
;;; summary row and never runs the callee body.
(define-function p107-c-run (body env lib)
  (if (not body) (list 'ok env)
    (let ((s (car body)) (rest (cdr body)))
      (cond
        ((not (pair? s)) '(invalid unknown-statement))
        ((equal (car s) 'assign)
          (let ((e2 (p107-c-update env (p107-nth s 1) (p107-nth s 2))))
            (if (equal e2 'missing-var) '(invalid undeclared-assign) (p107-c-run rest e2 lib))))
        ((equal (car s) 'assert)
          (if (= (p107-c-val (p107-nth s 1) env) 1) (p107-c-run rest env lib)
            (list 'refuted 'assert (p107-nth s 1))))
        ((equal (car s) 'if)
          (let* ((g (p107-c-val (p107-nth s 1) env))
                 (br (if (= g 1) (p107-nth s 2) (p107-nth s 3)))
                 (r (p107-c-run br env lib)))
            (if (not (equal (car r) 'ok)) r (p107-c-run rest (p107-nth r 1) lib))))
        ((equal (car s) 'call)
          (begin
            (set *p107-c-call-runs* (+ *p107-c-call-runs* 1))
            (let* ((name (p107-nth s 1)) (m (p107-c-lib-find lib name)))
              (if (not m) (list 'invalid 'unknown-unit name)
                (let ((r (p107-c-apply m env)))
                  (if (equal (car r) 'ok) (p107-c-run rest (p107-nth r 1) lib) r))))))
        (else '(invalid unknown-statement))))))

(define-function p107-c-frame (writes in out)
  (let ((ok true) (i 0) (vars (p107-map car in)))
    (while (< i (p107-len vars))
      (let ((v (p107-nth vars i)))
        (if (and (not (p107-member? v writes)) (not (equal (p107-c-get in v) (p107-c-get out v))))
          (set ok false)))
      (set i (+ i 1)))
    ok))

;;; Universal scan. A bad child result is recorded with its input and its own
;;; tag; it is never rewritten to `invalid`.
(define-function p107-c-scan (c i envs vars cases bad elig lib)
  (if (or (not (equal bad ())) (>= i (p107-len envs))) (list 'scan cases bad elig)
    (let* ((in (p107-nth envs i)) (p (p107-c-val (p107-nth c 3) in)))
      (if (= p 1)
        (let ((r (p107-c-run (p107-nth c 4) in lib)))
          (cond
            ((equal (car r) 'ok)
              (let* ((out (p107-nth r 1)) (q (p107-c-val (p107-nth c 5) out)))
                (if (and (= q 1) (p107-c-frame (p107-nth c 6) in out))
                  (p107-c-scan c (+ i 1) envs vars
                    (p107-append cases (list (list 'case (p107-c-index vars in) (p107-c-index vars out))))
                    () (+ elig 1) lib)
                  (p107-c-scan c (+ i 1) envs vars cases
                    (list 'refuted (p107-c-index vars in) (p107-c-index vars out) q) (+ elig 1) lib))))
            ((equal (car r) 'refuted)
              (p107-c-scan c (+ i 1) envs vars cases
                (cons 'refuted (cons (p107-c-index vars in) (cdr r))) (+ elig 1) lib))
            ((equal (car r) 'unknown)
              (p107-c-scan c (+ i 1) envs vars cases
                (cons 'unknown (cons (p107-c-index vars in) (cdr r))) (+ elig 1) lib))
            (else
              (p107-c-scan c (+ i 1) envs vars cases
                (cons 'invalid (cons (p107-c-index vars in) (cdr r))) (+ elig 1) lib))))
        (p107-c-scan c (+ i 1) envs vars cases bad elig lib)))))

(define-function p107-c-eligible (c)
  (let ((vars (p107-nth c 2)) (envs (p107-c-states (p107-nth c 2))) (out ()) (i 0))
    (while (< i (p107-len envs))
      (if (= (p107-c-val (p107-nth c 3) (p107-nth envs i)) 1)
        (set out (p107-append out (list (p107-c-index vars (p107-nth envs i))))))
      (set i (+ i 1)))
    out))

;;; Internal verifier: assumes `lib` was already accepted by p107-c-lib-check.
;;; The limit check comes first so an over-limit contract is a clean
;;; `(invalid unsupported-limit KIND)` rather than a stack failure.
(define-function p107-c-verify-with (c lib)
  (begin
    (set *p107-c-verified* (+ *p107-c-verified* 1))
    (let ((lim (p107-c-limit c)))
      (if (not (equal lim ())) (list 'invalid 'unsupported-limit lim)
        (if (not (p107-c-valid? c)) '(invalid contract)
          (let* ((vars (p107-nth c 2))
                 (r (p107-c-scan c 0 (p107-c-states vars) vars () () 0 lib)))
            (cond ((not (equal (p107-nth r 2) ())) (p107-nth r 2))
                  ((= (p107-nth r 3) 0) '(inapplicable))
                  (else (list 'verified (p107-nth r 1))))))))))

;;; Prefix validation: each unit is verified under the units before it, and its
;;; declared summary must be exactly the recomputed table. This rejects forged
;;; markers, stale cases, duplicate names, unknown/forward/self calls and
;;; changed callee contracts.
(define-function p107-c-lib-check-from (todo checked)
  (if (not todo) (list 'ok checked)
    (let ((m (car todo)))
      (if (not (p107-shape? m 4)) (list 'invalid 'module-shape)
        (if (not (p107-c-len<= (p107-nth m 3) *p107-c-max-cases*))
          (list 'invalid 'unsupported-limit 'cases)
          (let ((name (p107-nth m 1)))
            (if (p107-c-lib-find checked name) (list 'invalid 'duplicate-unit name)
              (let ((r (p107-c-verify-with (p107-nth m 2) checked)))
                (cond
                  ((equal (car r) 'verified)
                    (if (equal (p107-nth r 1) (p107-nth m 3))
                      (p107-c-lib-check-from (cdr todo) (p107-append checked (list m)))
                      (list 'invalid 'summary-mismatch name)))
                  ((equal (car r) 'inapplicable)
                    (if (equal (p107-nth m 3) ())
                      (p107-c-lib-check-from (cdr todo) (p107-append checked (list m)))
                      (list 'invalid 'summary-mismatch name)))
                  (else (p107-append (list 'invalid 'module name) (cdr r))))))))))))

(define-function p107-c-lib-check (lib)
  (cond ((not (p107-list? lib)) (list 'invalid 'library-shape))
        ((not (p107-c-len<= lib *p107-c-max-units*)) (list 'invalid 'unsupported-limit 'units))
        (else (p107-c-lib-check-from lib ()))))

;;; Public boundary: check the library first, then evaluate against the checked
;;; prefix. The evaluator never sees an unchecked unit through this path.
(define-function p107-c-verify-lib (c lib)
  (let ((chk (p107-c-lib-check lib)))
    (if (equal (car chk) 'ok)
      (p107-c-verify-with c (p107-nth chk 1))
      (p107-append (list 'invalid 'library) (cdr chk)))))

(define-function p107-c-cases-ok? (cases vars)
  (and (p107-c-len<= vars *p107-c-max-vars*)
       (p107-list? vars)
       (p107-c-len<= cases *p107-c-max-cases*)
       (p107-list? cases)
       (not (p107-any? (lambda (k)
         (not (and (p107-shape? k 3) (equal (car k) 'case)
                   (p107-list? (p107-nth k 1)) (p107-list? (p107-nth k 2))
                   (p107-c-len<= (p107-nth k 1) (p107-len vars))
                   (p107-c-len<= (p107-nth k 2) (p107-len vars))
                   (= (p107-len (p107-nth k 1)) (p107-len vars))
                   (= (p107-len (p107-nth k 2)) (p107-len vars))
                   (not (p107-any? (lambda (x) (not (p107-b? x))) (p107-nth k 1)))
                   (not (p107-any? (lambda (x) (not (p107-b? x))) (p107-nth k 2))))))
         cases))
       (p107-c-distinct? (p107-map (lambda (k) (p107-nth k 1)) cases))))

;;; Internal checker: exact table equality, not a set comparison, so a
;;; duplicated input row cannot pass with the same length. This is a recompute
;;; with the same library, not an independently implemented checker.
(define-function p107-c-check-with (c cases lib)
  (and (p107-c-valid? c) (p107-c-cases-ok? cases (p107-nth c 2))
       (let ((r (p107-c-verify-with c lib)))
         (cond ((equal (car r) 'verified) (equal cases (p107-nth r 1)))
               ((equal (car r) 'inapplicable) (equal cases ()))
               (else false)))))

(define-function p107-c-check-lib (c cases lib)
  (let ((chk (p107-c-lib-check lib)))
    (and (equal (car chk) 'ok) (p107-c-check-with c cases (p107-nth chk 1)))))

;;; Compatibility wrappers for the empty library (the 0.0114 fragment).
(define-function p107-c-verify (c) (p107-c-verify-lib c ()))
(define-function p107-c-check (c cases) (p107-c-check-lib c cases ()))

;;; Evidence binds a result to the exact library it was checked against.
;;; Only `(verified CASES)` is admissible. The checker recomputes the full result
;;; under the current library and requires exact equality, so refuted/unknown
;;; tags, a fabricated `verified` for an inapplicable contract, and extra fields
;;; are all rejected.
(define-function p107-c-evidence (c lib)
  (let ((chk (p107-c-lib-check lib)))
    (if (not (equal (car chk) 'ok)) (p107-append (list 'invalid 'library) (cdr chk))
      (let ((r (p107-c-verify-with c (p107-nth chk 1))))
        (if (equal (car r) 'verified) (list 'evidence c r (p107-nth chk 1)) r)))))

(define-function p107-c-check-evidence (ev lib)
  (if (not (and (p107-shape? ev 4) (equal (car ev) 'evidence))) (list 'invalid 'evidence-shape)
    (let* ((c (p107-nth ev 1)) (res (p107-nth ev 2)) (stored (p107-nth ev 3)))
      (cond
        ((not (and (p107-shape? res 2) (equal (car res) 'verified)
                   (p107-list? (p107-nth res 1))
                   (p107-c-len<= (p107-nth res 1) *p107-c-max-cases*)))
         (list 'invalid 'evidence-result))
        ((not (p107-c-len<= stored *p107-c-max-units*)) (list 'invalid 'evidence-result))
        ((not (p107-c-len<= lib *p107-c-max-units*)) (list 'invalid 'unsupported-limit 'units))
        ((not (equal stored lib)) (list 'invalid 'stale-library))
        (else
          (let ((chk (p107-c-lib-check lib)))
            (if (not (equal (car chk) 'ok))
              (p107-append (list 'invalid 'library) (cdr chk))
              (let ((now (p107-c-verify-with c (p107-nth chk 1))))
                (if (equal now res) (list 'ok)
                  (list 'invalid 'evidence-mismatch))))))))))

(define-function p107-c-reset-stats ()
  (begin
    (set *p107-c-applied* 0)
    (set *p107-c-verified* 0)
    (set *p107-c-call-runs* 0)))