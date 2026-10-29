;;; Explicit synthetic workload, not acquired web observations.
(basis90 'init '(r s t u v))
(basis90 'observe 'train '((atom r (a b)) (atom r (p q))
  (atom s (b c)) (atom s (q z)) (atom t (c d)) (atom t (z w))
  (atom u (c e)) (atom u (d f)) (atom v (h a)) (atom v (g p))))
(basis90 'task 'rst '(join90 (join90 (rel90 r) (rel90 s)) (rel90 t)))
(basis90 'task 'rsu '(join90 (join90 (rel90 r) (rel90 s)) (rel90 u)))
(basis90 'task 'vrs '(join90 (rel90 v) (join90 (rel90 r) (rel90 s))))
