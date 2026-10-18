;;; -*- mode: lisp; coding: us-ascii -*-
(define *csp-problems*
  (list
    (list 'anchored-coloring
      '((a (red green blue)) (b (red green blue))
        (c (red green blue)) (d (red)))
      '((neq a b) (neq b c) (neq c d) (neq a d)))
    (list 'unsatisfiable-triangle
      '((a (red green)) (b (red green)) (c (red green)))
      '((neq a b) (neq b c) (neq a c)))
    (list 'role-candidates
      '((subject (pump valve)) (relation (uses used-by)) (object (pump valve)))
      '((neq subject object)
        (table relation object ((uses valve) (used-by pump)))))))

(define-function csp-same-solutions? (a b)
  (and (not (dlm-difference (dlm-nth a 2) (dlm-nth b 2)))
       (not (dlm-difference (dlm-nth b 2) (dlm-nth a 2)))))

(define-function csp-check (test name)
  (if test (println "PASS: " name) (error "FAIL: " name)))

(define *csp-dfs-nodes* 0)
(define *csp-prop-nodes* 0)
(list-do problem *csp-problems*
  (let* ((domains (dlm-nth problem 1)) (constraints (dlm-nth problem 2))
         (dfs (csp-solve domains constraints 10000 'dfs))
         (prop (csp-solve domains constraints 10000 'propagate))
         (mrv (csp-solve domains constraints 10000 'propagate-mrv)))
    (println (car problem) " DFS " dfs)
    (println (car problem) " PROP " prop)
    (println (car problem) " MRV " mrv)
    (csp-check (and (= (dlm-nth dfs 1) 'complete)
                    (= (dlm-nth prop 1) 'complete)
                    (= (dlm-nth mrv 1) 'complete)) "all arms complete")
    (csp-check (and (csp-same-solutions? dfs prop) (csp-same-solutions? dfs mrv))
               "propagation preserves complete solution set")
    (set *csp-dfs-nodes* (+ *csp-dfs-nodes* (dlm-nth dfs 3)))
    (set *csp-prop-nodes* (+ *csp-prop-nodes* (dlm-nth prop 3)))))
(println "TOTAL-NODES " (list 'dfs *csp-dfs-nodes* 'propagate *csp-prop-nodes*))
(csp-check (< *csp-prop-nodes* *csp-dfs-nodes*) "propagation reduces expanded nodes")
