;;; d107-plan.l — support from current observations, active basis, plans, answers.
;;; Loaded after the session (it needs observation accessors) and before learning.

;;; ---------- support from the CURRENT observations ----------
(define-function p107-subsets (xs n)
  (cond ((= n 0) (list ())) ((not xs) ()) (else
    (p107-append
      (p107-map (lambda (r) (cons (car xs) r)) (p107-subsets (cdr xs) (- n 1)))
      (p107-subsets (cdr xs) n)))))
(define-function p107-apply-sub (terms sub)
  (p107-map (lambda (t) (let ((h (p107-assoc t sub))) (if h (p107-nth h 1) t))) terms))
(define-function p107-join (atoms facts sub used)
  ;; returns (rows . used-ids) as a list of (sub . used)
  (if (not atoms) (list (list sub used))
    (let ((out ()))
      (list-do f facts
        (if (not (p107-member? (p107-nth f 1) used))
          (let ((s2 (p107-match (car atoms) (p107-nth f 2) sub)))
            (if s2
              (list-do r (p107-join (cdr atoms) facts s2 (cons (p107-nth f 1) used))
                (set out (p107-append out (list r))))))))
      out)))
(define-function p107-rows (pattern facts)
  (p107-join pattern facts (p107-subst ()) ()))
(define-function p107-record-support (pattern obs-list)
  ;; one observation = one record; support counts records with >=1 distinct-fact match
  (let ((n 0))
    (list-do o obs-list
      (let ((facts (p107-facts-of o)))
        (if (p107-rows pattern facts) (set n (+ n 1)))))
    n))
(define-function p107-support (s pattern)
  (p107-record-support pattern (p107-obs-list s)))

;;; ---------- active basis and plan ----------
(define-function p107-active? (s d) (>= (p107-support s (p107-def-pattern d)) 2))
(define-function p107-active-defs (s)
  (p107-filter (lambda (d) (p107-active? s d)) (p107-defs-of s)))
(define-function p107-cover (s pattern)
  (let ((key (p107-conj-key pattern)) (out ()))
    (list-do d (p107-active-defs s)
      (if (and (not out) (equal key (p107-conj-key (p107-def-pattern d))))
        (set out d)))
    out))
(define-function p107-plan (s pattern)
  (let ((d (p107-cover s pattern)))
    (if d (list 'plan107 pattern (p107-len pattern) (p107-len (p107-def-body d))
                (p107-def-body d) (p107-def-id d))
      (list 'plan107 pattern (p107-len pattern) (p107-len pattern) pattern ()))))
;;; ---------- executing the PLAN (calls counted), not the raw pattern ----------
(define *p107-calls* 0)
(define *p107-steps* 0)
(define *p107-unknown* false)

(define-function p107-sub-terms (terms sub)
  (p107-map (lambda (t) (p107-subst-term t sub)) terms))
(define-function p107-bind-formals (vars terms)
  (if (not vars) (if terms 'bind-failed ())
    (if (not terms) 'bind-failed
      (let ((rest (p107-bind-formals (cdr vars) (cdr terms))))
        (if (equal rest 'bind-failed) 'bind-failed
          (cons (list (car vars) (car terms)) rest))))))
(define-function p107-expand-call (d terms)
  (let ((bind (p107-bind-formals (p107-def-vars d) terms)))
    (if (equal bind 'bind-failed) 'bind-failed
      (p107-map (lambda (a) (p107-atom (p107-pred a)
        (p107-map (lambda (t) (let ((h (p107-assoc t bind))) (if h (p107-nth h 1) t))) (p107-args a))))
        (p107-def-body d)))))

(define-function p107-exec-atoms (atoms facts sub used budget)
  (cond
    ((not atoms) (list (cons sub used)))
    ((> *p107-steps* budget) (begin (set *p107-unknown* true) 'unknown))
    (else
      (let ((out ()) (i 0) (n (p107-len facts)) (bad false))
        (while (and (< i n) (not bad))
          (let ((f (p107-nth facts i)))
            (if (not (p107-member? (p107-nth f 1) used))
              (let ((s2 (p107-match (car atoms) (p107-nth f 2) sub)))
                (if s2
                  (begin
                    (set *p107-steps* (+ *p107-steps* 1))
                    (let ((r (p107-exec-atoms (cdr atoms) facts s2 (cons (p107-nth f 1) used) budget)))
                      (if (or (equal r 'unknown) (equal r 'invalid)) (set bad true)
                        (set out (p107-append out r)))))))))
          (set i (+ i 1)))
        (if bad 'unknown out)))))

(define-function p107-step-apply (step row defs facts budget)
  (if (p107-call? step)
    (let* ((id (p107-nth step 1)) (terms (p107-sub-terms (p107-nth step 2) (car row)))
           (d (p107-find-def defs id)))
      (if (not d) 'invalid
        (let ((atoms (p107-expand-call d terms)))
          (if (equal atoms 'bind-failed) 'invalid
            (begin (set *p107-calls* (+ *p107-calls* 1))
              (p107-exec-atoms atoms facts (car row) (cdr row) budget))))))
    (p107-exec-atoms (list step) facts (car row) (cdr row) budget)))

(define-function p107-apply-rows (step rows defs facts budget)
  (cond ((not rows) ())
        ((equal rows 'unknown) 'unknown)
        ((equal rows 'invalid) 'invalid)
        (else
          (let ((r (p107-step-apply step (car rows) defs facts budget)))
            (cond ((equal r 'unknown) 'unknown)
                  ((equal r 'invalid) 'invalid)
                  (else (p107-append r (p107-apply-rows step (cdr rows) defs facts budget))))))))

(define-function p107-exec (steps defs facts sub used budget)
  ;; iterate the plan left to right; a call executes the unit's OWN body
  (let ((rows (list (cons sub used))) (i 0) (state 'ok))
    (while (and (< i (p107-len steps)) (equal state 'ok))
      (let ((next (p107-apply-rows (p107-nth steps i) rows defs facts budget)))
        (if (or (equal next 'unknown) (equal next 'invalid)) (set state next) (set rows next)))
      (set i (+ i 1)))
    (if (equal state 'ok) rows state)))

(define-function p107-instantiate (steps defs sub)
  ;; ground atoms produced by the plan; this is what the answer is computed from
  (if (not steps) ()
    (if (p107-call? (car steps))
      (let* ((d (p107-find-def defs (p107-nth (car steps) 1)))
             (terms (p107-sub-terms (p107-nth (car steps) 2) sub)))
        (if (not d) 'invalid
          (let ((atoms (p107-expand-call d terms)))
            (if (equal atoms 'bind-failed) 'invalid
              (let ((rest (p107-instantiate (cdr steps) defs sub)))
                (if (equal rest 'invalid) 'invalid
                  (p107-append (p107-map (lambda (a) (p107-subst-atom a sub)) atoms) rest)))))))
      (let ((rest (p107-instantiate (cdr steps) defs sub)))
        (if (equal rest 'invalid) 'invalid
          (cons (p107-subst-atom (car steps) sub) rest))))))

(define-function p107-remove-nth (xs n)
  (if (not xs) ()
    (if (= n 0) (cdr xs) (cons (car xs) (p107-remove-nth (cdr xs) (- n 1))))))

(define-function p107-match-ground (pattern ground sub)
  ;; greedily align each query atom with one ground atom; returns a binding or 'no
  (if (not pattern) sub
    (let ((out 'no) (i 0))
      (while (and (< i (p107-len ground)) (equal out 'no))
        (let ((s2 (p107-match (car pattern) (p107-nth ground i) sub)))
          (if s2
            (let ((r (p107-match-ground (cdr pattern) (p107-remove-nth ground i) s2)))
              (if (not (equal r 'no)) (set out r)))))
        (set i (+ i 1)))
      out)))

(define-function p107-row-values (sub vars)
  (p107-map (lambda (v) (let ((h (p107-assoc v (p107-pairs sub)))) (if h (p107-nth h 1) v))) vars))
(define-function p107-sort-rows (rows)
  (if (not rows) ()
    (let ((head (car rows)) (less ()) (more ()))
      (list-do r (cdr rows)
        (if (> (string-compare (p107-serialize r) (p107-serialize head)) 0)
          (set more (p107-append more (list r)))
          (set less (p107-append less (list r)))))
      (p107-append (p107-sort-rows less) (p107-append (list head) (p107-sort-rows more))))))

(define-function p107-witnesses-ok? (ids table)
  ;; every witness must be an actual fact of this scope/closure
  (if (not ids) true
    (let ((f (p107-fact-by-id (car ids) table)))
      (and f (p107-witnesses-ok? (cdr ids) table)))))

(define-function p107-answer-plan (s scope pattern budget use-plan)
  (let* ((c (p107-closure s scope budget)) (status (p107-nth c 0)) (table (p107-nth c 1))
         (vars (p107-all-vars pattern))
         (plan (p107-plan s pattern))
         (steps (if use-plan (p107-nth plan 4) pattern))
         (cover (if use-plan (p107-nth plan 5) ())))
    (if (not (= status 'complete)) (list 'answer107 pattern status vars () 0 0 cover)
      (begin
        (set *p107-calls* 0) (set *p107-steps* 0) (set *p107-unknown* false)
        (let ((rows (p107-exec steps (p107-defs-of s) table (p107-subst ()) () budget)))
          (cond
            ((equal rows 'invalid) (list 'answer107 pattern 'invalid vars () *p107-calls* *p107-steps* cover))
            ((or (equal rows 'unknown) *p107-unknown*)
              (list 'answer107 pattern 'unknown vars () *p107-calls* *p107-steps* cover))
            (else
              (let ((out ()) (bad false))
                (list-do r rows
                  (let ((ground (p107-instantiate steps (p107-defs-of s) (car r))))
                    (if (or (equal ground 'invalid) (not (p107-witnesses-ok? (cdr r) table))) (set bad true)
                      (let ((q (p107-match-ground pattern ground (p107-subst ()))))
                        (if (equal q 'no) (set bad true)
                          (set out (p107-append out (list (list 'row107
                            (p107-row-values q vars) (p107-sort-keys (cdr r)))))))))))
                (list 'answer107 pattern (if bad 'invalid 'complete) vars
                      (p107-sort-rows out) *p107-calls* *p107-steps* cover)))))))))
(define-function p107-answer (s scope pattern budget) (p107-answer-plan s scope pattern budget true))
(define-function p107-answer-raw (s scope pattern budget) (p107-answer-plan s scope pattern budget false))
