;;; -*- mode: lisp; coding: us-ascii -*-
;;; Graph75: observations, rules, interned nodes, active claim ids, supports,
;;; predicate/argument indexes, completion status, metrics, transition events.
;;; Nodes: (node ID KIND VALUE). Supports share ids rather than nested proofs.
(define-function gr-node (catalog id)
  (let ((found ()))
    (list-do node catalog (if (= (dlm-nth node 1) id) (set found node)))
    found))

(define-function gr-find (catalog kind value)
  (let ((found ()))
    (list-do node catalog
      (if (and (= (dlm-nth node 2) kind) (equal (dlm-nth node 3) value))
          (set found node)))
    found))

(define-function gr-intern (catalog kind value)
  (let ((old (gr-find catalog kind value)))
    (if old (list catalog (dlm-nth old 1))
      (let ((id (dlm-length catalog)))
        (list (dlm-append catalog (list (list 'node id kind value))) id)))))

(define-function gr-intern-atom (catalog atom)
  (let ((current (car (gr-intern catalog 'predicate
                      (list (dlm-pred atom) (dlm-length (dlm-args atom)))))))
    (list-do term (dlm-args atom)
      (set current (car (gr-intern current 'entity term))))
    (gr-intern current 'claim atom)))

(define-function gr-index-add (index key id)
  (let ((old (dlm-assoc key index)))
    (cons (list key (dlm-add (dlm-nth old 1) id))
          (dlm-difference index (if old (list old) ())))))

(define-function gr-indexes (catalog active)
  (let ((predicates ()) (arguments ()))
    (list-do id active
      (let* ((atom (dlm-nth (gr-node catalog id) 3)) (pred (dlm-pred atom)) (position 0))
        (set predicates (gr-index-add predicates pred id))
        (list-do term (dlm-args atom)
          (set arguments (gr-index-add arguments (list pred position term) id))
          (set position (+ position 1)))))
    (list predicates arguments)))

(define-function gr-candidates (pattern env indexes)
  (let ((ids (dlm-nth (dlm-assoc (dlm-pred pattern) (car indexes)) 1)) (position 0))
    (list-do term (dlm-subst-terms (dlm-args pattern) env)
      (unless (dlm-var? term)
        (set ids (dlm-intersection ids (dlm-nth (dlm-assoc
          (list (dlm-pred pattern) position term) (dlm-nth indexes 1)) 1))))
      (set position (+ position 1)))
    ids))

;;; Result (JOIN-STATES MATCH-ATTEMPTS); states carry env and shared premise ids.
(define-function gr-join (body catalog indexes states)
  (if body
      (let ((next ()) (attempts 0))
        (list-do state states
          (list-do id (gr-candidates (car body) (car state) indexes)
            (set attempts (+ attempts 1))
            (let ((match (dlm-match (car body) (dlm-nth (gr-node catalog id) 3) (car state))))
              (when match
                (set next (dlm-append next (list (list (dlm-nth match 1)
                  (dlm-append (dlm-nth state 1) (list id))))))))))
        (let ((rest (gr-join (cdr body) catalog indexes next)))
          (list (car rest) (+ attempts (dlm-nth rest 1)))))
    (list states 0)))

;;; No persisted closure is trusted: each transition rebuilds least fixed point.
;;; Catalog ids survive retraction, but inactive nodes are absent from indexes.
(define-function gr-build (observations rules catalog budget events)
  (let ((active ()) (supports ()) (changed (and rules true)) (passes 0) (matches 0))
    (list-do observation observations
      (let ((interned (gr-intern-atom catalog (dlm-nth observation 3))))
        (set catalog (car interned))
        (when (= (dlm-nth observation 2) 'positive)
          (set active (dlm-add active (dlm-nth interned 1)))
          (set supports (dlm-add supports
            (list 'support (dlm-nth interned 1) 'fact (dlm-nth observation 1) ()))))))
    (while (and changed (< passes budget))
      (let ((indexes (gr-indexes catalog active)) (next active))
        (set changed false)
        (set passes (+ passes 1))
        (list-do record rules
          (let* ((rule (dlm-nth record 2))
                 (joined (gr-join (dlm-body rule) catalog indexes (list (list () ())))))
            (set matches (+ matches (dlm-nth joined 1)))
            (list-do state (car joined)
              (let* ((atom (dlm-substitute (dlm-head rule) (car state)))
                     (interned (gr-intern-atom catalog atom)) (id (dlm-nth interned 1)))
                (assert (dlm-ground? atom) "graph rule produced unground claim")
                (set catalog (car interned))
                (unless (dlm-member? id next) (set changed true))
                (set next (dlm-add next id))
                (set supports (dlm-add supports
                  (list 'support id 'rule (dlm-nth record 1) (dlm-nth state 1))))))))
        (set active next)))
    (let ((indexes (gr-indexes catalog active)))
      (list 'graph 75 observations rules catalog active supports
        (car indexes) (dlm-nth indexes 1) (if changed 'incomplete 'complete)
        (list 'metrics passes matches (dlm-length supports)) events))))

(define-function gr-new () (gr-build () () () 0 ()))

(define-function gr-provenance? (value)
  (and (dlm-proper? value 5) (= (dlm-length value) 4)
       (= (car value) 'provenance) (symbol? (dlm-nth value 1))
       (let ((span (dlm-nth value 2)))
         (or (not span)
             (and (dlm-proper? span 4) (= (dlm-length span) 3) (= (car span) 'span)
                  (is <long> (dlm-nth span 1)) (is <long> (dlm-nth span 2))
                  (<= 0 (dlm-nth span 1)) (<= (dlm-nth span 1) (dlm-nth span 2)))))))

(define-function gr-observation? (value)
  (and (dlm-proper? value 6) (= (dlm-length value) 5) (= (car value) 'observation)
       (symbol? (dlm-nth value 1)) (dlm-member? (dlm-nth value 2) '(positive negative))
       (dlm-atom? (dlm-nth value 3)) (dlm-ground? (dlm-nth value 3))
       (gr-provenance? (dlm-nth value 4))
       (= (dlm-nth (dlm-nth value 4) 3) 'observed)))

(define-function gr-rule-record? (value)
  (and (dlm-proper? value 5) (= (dlm-length value) 4) (= (car value) 'rule-record)
       (symbol? (dlm-nth value 1)) (dlm-safe? (dlm-nth value 2))
       (gr-provenance? (dlm-nth value 3))
       (dlm-member? (dlm-nth (dlm-nth value 3) 3) '(given learned))))

(define-function gr-record (records id)
  (let ((found ()))
    (list-do record records (if (equal id (dlm-nth record 1)) (set found record)))
    found))

(define-function gr-without (records id)
  (if records
      (if (equal id (dlm-nth (car records) 1)) (gr-without (cdr records) id)
        (cons (car records) (gr-without (cdr records) id))) ()))

(define-function gr-signatures-valid? (observations rules)
  (let ((atoms ()) (signatures ()) (valid true))
    (list-do observation observations (set atoms (cons (dlm-nth observation 3) atoms)))
    (list-do record rules
      (let ((rule (dlm-nth record 2)))
        (set atoms (dlm-append (cons (dlm-head rule) (dlm-body rule)) atoms))))
    (list-do atom atoms
      (let* ((pred (dlm-pred atom)) (arity (dlm-length (dlm-args atom)))
             (old (dlm-assoc pred signatures)))
        (if old (unless (= arity (dlm-nth old 1)) (set valid false))
          (set signatures (cons (list pred arity) signatures)))))
    valid))

(define-function gr-conflict? (graph)
  (let ((conflict false))
    (list-do observation (dlm-nth graph 2)
      (when (= (dlm-nth observation 2) 'negative)
        (let ((node (gr-find (dlm-nth graph 4) 'claim (dlm-nth observation 3))))
          (when (and node (dlm-member? (dlm-nth node 1) (dlm-nth graph 5)))
            (set conflict true)))))
    conflict))

;;; Invalid proposals return errors without changing the original immutable state.
(define-function gr-apply (graph action budget)
  (if (not (and (is <long> budget) (<= 0 budget) (dlm-proper? action 3)
                (= (dlm-length action) 2))) (list 'graph-error 'invalid-action)
    (let ((observations (dlm-nth graph 2)) (rules (dlm-nth graph 3))
          (kind (car action)) (value (dlm-nth action 1)) (valid true))
      (cond
        ((= kind 'observe)
         (if (gr-observation? value)
             (let ((old (gr-record observations (dlm-nth value 1))))
               (if old (set valid (equal old value))
                 (set observations (dlm-append observations (list value)))))
           (set valid false)))
        ((= kind 'rule)
         (if (gr-rule-record? value)
             (let ((old (gr-record rules (dlm-nth value 1))))
               (if old (set valid (equal old value))
                 (set rules (dlm-append rules (list value)))))
           (set valid false)))
        ((= kind 'retract-observation)
         (set valid (and (gr-record observations value) true))
         (set observations (gr-without observations value)))
        ((= kind 'retract-rule)
         (set valid (and (gr-record rules value) true))
         (set rules (gr-without rules value)))
        ((= kind 'recompute) (set valid (= value 'closure)))
        (else (set valid false)))
      (if (and valid (gr-signatures-valid? observations rules))
          (let ((next (gr-build observations rules (dlm-nth graph 4) budget
                        (dlm-append (dlm-nth graph 11) (list (list 'event action budget))))))
            (if (and (= kind 'rule) (= (dlm-nth (dlm-nth value 3) 3) 'learned)
                     (or (= (dlm-nth next 9) 'incomplete) (gr-conflict? next)))
                (list 'graph-error 'learned-rule-admission-failed) next))
        (list 'graph-error 'invalid-record-or-signature)))))

(define-function gr-replay (events)
  (let ((graph (gr-new)))
    (list-do event events
      (assert (and (= (car event) 'event) (= (dlm-length event) 3)) "invalid graph event")
      (set graph (gr-apply graph (dlm-nth event 1) (dlm-nth event 2)))
      (assert (= (car graph) 'graph) "graph replay rejected action"))
    graph))

(define-function gr-verify-state (graph)
  (assert (and (dlm-proper? graph 13) (= (dlm-length graph) 12)
               (= (car graph) 'graph) (= (dlm-nth graph 1) 75)) "invalid graph snapshot")
  (assert (equal graph (gr-replay (dlm-nth graph 11))) "graph replay mismatch")
  graph)

(define-function gr-facts (graph)
  (let ((facts ()))
    (list-do observation (dlm-nth graph 2)
      (when (= (dlm-nth observation 2) 'positive)
        (set facts (dlm-add facts (dlm-nth observation 3)))))
    facts))

(define-function gr-rules (graph)
  (map (lambda (record) (dlm-nth record 2)) (dlm-nth graph 3)))

(define-function gr-closure (graph)
  (map (lambda (id) (dlm-nth (gr-node (dlm-nth graph 4) id) 3)) (dlm-nth graph 5)))
