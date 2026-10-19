;;; -*- mode: lisp; coding: us-ascii -*-
(define gr-proof-node ())

(define-function gr-proof-premises (graph ids visited fuel)
  (if ids
      (let ((proof (gr-proof-node graph (car ids) visited fuel)))
        (and proof
          (let ((rest (gr-proof-premises graph (cdr ids) visited fuel)))
            (and rest (list 'ok (cons proof (dlm-nth rest 1)))))))
    (list 'ok ())))

;;; The support graph may contain recursive edges; witnesses must be acyclic.
(set gr-proof-node
  (lambda (graph id visited fuel)
    (and (> fuel 0) (not (dlm-member? id visited))
      (let ((answer ()) (atom (dlm-nth (gr-node (dlm-nth graph 4) id) 3)))
        (list-do support (dlm-nth graph 6)
          (when (and (not answer) (= (dlm-nth support 1) id))
            (if (= (dlm-nth support 2) 'fact)
                (let ((observation (gr-record (dlm-nth graph 2) (dlm-nth support 3))))
                  (when (and observation (= (dlm-nth observation 2) 'positive)
                             (equal atom (dlm-nth observation 3)))
                    (set answer (dlm-fact-proof atom))))
              (let ((record (gr-record (dlm-nth graph 3) (dlm-nth support 3)))
                    (premises (gr-proof-premises graph (dlm-nth support 4)
                                                (cons id visited) (- fuel 1))))
                (when (and record premises)
                  (let ((proof (dlm-rule-proof atom (dlm-nth record 2) (dlm-nth premises 1))))
                    (when (dlm-verify-proof proof (gr-facts graph) (gr-rules graph))
                      (set answer proof))))))))
        answer))))

(define-function gr-query (graph target)
  (if (not (and (dlm-atom? target) (dlm-ground? target))) (list 'graph-error 'invalid-query)
    (let* ((node (gr-find (dlm-nth graph 4) 'claim target))
           (id (and node (dlm-nth node 1)))
           (active (and node (dlm-member? id (dlm-nth graph 5))))
           (proof (and active (gr-proof-node graph id () 1000))) (negative ()))
      (list-do observation (dlm-nth graph 2)
        (when (and (= (dlm-nth observation 2) 'negative)
                   (equal (dlm-nth observation 3) target))
          (set negative (dlm-add negative (dlm-nth observation 1)))))
      (assert (or (not active) (and proof (dlm-verify-proof proof (gr-facts graph) (gr-rules graph))))
              "graph witness failed independent Horn verification")
      (list 'answer (if proof (if negative 'conflict 'entailed)
                       (if negative 'contradicted
                         (if (= (dlm-nth graph 9) 'complete) 'unknown 'incomplete)))
            target proof negative (dlm-nth graph 9)))))

(define-function gr-supports-for (graph target)
  (let ((node (gr-find (dlm-nth graph 4) 'claim target)) (result ()))
    (when node
      (list-do support (dlm-nth graph 6)
        (if (= (dlm-nth support 1) (dlm-nth node 1))
            (set result (dlm-append result (list support))))))
    result))

(define-function gr-dependents (graph id)
  (let ((result ()))
    (list-do support (dlm-nth graph 6)
      (when (dlm-member? id (dlm-nth support 4))
        (set result (dlm-add result (dlm-nth support 1)))))
    result))

;;; Directed binary relation paths are search candidates, not composed claims.
;;; Queue entries: (CURRENT ENTITY-PATH CLAIM-ID-PATH). No repeated entity.
(define-function gr-paths (graph source target predicates depth budget limit)
  (if (not (and (is <long> depth) (<= 0 depth) (is <long> budget) (<= 0 budget)
                (is <long> limit) (< 0 limit))) (list 'graph-error 'invalid-path-budget)
    (let ((agenda (list (list source (list source) ()))) (paths ()) (steps 0) (cut false))
      (while (and agenda (< steps budget) (< (dlm-length paths) limit))
        (let* ((entry (car agenda)) (current (car entry)) (vertices (dlm-nth entry 1))
               (edges (dlm-nth entry 2)))
          (set agenda (cdr agenda))
          (set steps (+ steps 1))
          (if (equal current target)
              (set paths (dlm-append paths (list (list 'path vertices edges))))
            (list-do pred predicates
              (list-do id (dlm-nth (dlm-assoc (list pred 0 current) (dlm-nth graph 8)) 1)
                (let ((args (dlm-args (dlm-nth (gr-node (dlm-nth graph 4) id) 3))))
                  (when (and (= (dlm-length args) 2) (not (dlm-member? (dlm-nth args 1) vertices)))
                    (if (< (dlm-length edges) depth)
                        (set agenda (dlm-append agenda (list (list (dlm-nth args 1)
                          (dlm-append vertices (list (dlm-nth args 1)))
                          (dlm-append edges (list id))))))
                      (set cut true)))))))))
      (list 'paths (if (or agenda cut (= (dlm-nth graph 9) 'incomplete)) 'incomplete 'complete)
            paths steps))))

;;; Adopt a proposed rule only relative to the supplied finite evidence.
;;; A score never authorizes a rule that derives explicit counterobservations.
(define-function gr-admit-rule (graph record budget)
  (let ((candidate (gr-apply graph (list 'rule record) budget)))
    (if (= (car candidate) 'graph-error) candidate
      (if (= (dlm-nth candidate 9) 'incomplete) (list 'graph-error 'incomplete-evaluation)
        (let ((conflict false))
          (list-do observation (dlm-nth candidate 2)
            (when (and (= (dlm-nth observation 2) 'negative)
              (dlm-member? (dlm-nth observation 3) (gr-closure candidate)))
              (set conflict true)))
          (if conflict (list 'graph-error 'counterevidence) candidate))))))

(define-function gr-from-episode (episode rules budget)
  (let ((graph (gr-new)) (index 0))
    (list-do atom (dlm-nth episode 2)
      (set graph (gr-apply graph
        (list 'observe (list 'observation
          (string->symbol (concat-strings "o" (number->string index))) 'positive atom
          (list 'provenance (dlm-nth episode 1) () 'observed))) budget))
      (set index (+ index 1)))
    (set index 0)
    (list-do rule rules
      (set graph (gr-admit-rule graph
        (list 'rule-record (string->symbol (concat-strings "r" (number->string index)))
              rule '(provenance experience () learned)) budget))
      (set index (+ index 1)))
    graph))
