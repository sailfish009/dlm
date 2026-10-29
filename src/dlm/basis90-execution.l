;;; Runtime tables belong to ONE execution batch and ONE immutable episode.
;;; No answer is stored as a new observation. Unknown is never an empty relation.
;;; runtime90: remaining used cache basis-calls cache-hits joins scans used-bases.
(define-function b90-runtime (fuel) (list 'runtime90 fuel 0 () 0 0 0 0 ()))
(define-function b90-spend (r)
  (s79-field (s79-field r 1 (- (dlm-nth r 1) 1)) 2 (+ (dlm-nth r 2) 1)))
(define-function b90-metric (r i) (s79-field r i (+ (dlm-nth r i) 1)))
(define-function b90-value (status pairs r) (list 'value90 status pairs r))
(define-function b90-scan (name facts r)
  (let ((pairs ()) (status 'complete))
    (list-do f facts
      (if (= status 'complete)
        (if (= (dlm-nth r 1) 0) (set status 'unknown)
          (begin (set r (b90-metric (b90-spend r) 7))
            (if (equal name (dlm-nth f 1)) (set pairs (dlm-add pairs (dlm-nth f 2))))))))
    (b90-value status (if (= status 'complete) pairs ()) r)))
(define-function b90-join (left right r)
  (let ((pairs ()) (status 'complete))
    (list-do a left (list-do b right
      (if (= status 'complete)
        (if (= (dlm-nth r 1) 0) (set status 'unknown)
          (begin (set r (b90-metric (b90-spend r) 6))
            (if (equal (dlm-nth a 1) (car b)) (set pairs (dlm-add pairs (list (car a) (dlm-nth b 1))))))))))
    (b90-value status (if (= status 'complete) pairs ()) r)))
(define b90-evaluate ())
(set b90-evaluate (lambda (e facts lib r memo)
  (if (= (dlm-nth r 1) 0) (b90-value 'unknown () r)
    (let ((cached ()) (result ()) (cacheable (or memo (not (= (car e) 'join90)))))
      (set r (b90-spend r))
      (if (= (car e) 'use90)
        (begin (set r (b90-metric r 4))
          (set r (s79-field r 8 (dlm-add (dlm-nth r 8) (dlm-nth e 1))))))
      (if cacheable (set cached (dlm-assoc e (dlm-nth r 3))))
      (if cached (b90-value 'complete (dlm-nth cached 1) (b90-metric r 5))
        (begin
          (set result
            (cond
              ((= (car e) 'rel90) (b90-scan (dlm-nth e 1) facts r))
              ((= (car e) 'use90)
                (b90-evaluate (dlm-nth (b90-module lib (dlm-nth e 1)) 2) facts lib r memo))
              (else
                (let ((a (b90-evaluate (dlm-nth e 1) facts lib r memo)))
                  (if (not (= (dlm-nth a 1) 'complete)) a
                    (let ((b (b90-evaluate (dlm-nth e 2) facts lib (dlm-nth a 3) memo)))
                      (if (not (= (dlm-nth b 1) 'complete)) b
                        (b90-join (dlm-nth a 2) (dlm-nth b 2) (dlm-nth b 3)))))))))
          (if (and cacheable (= (dlm-nth result 1) 'complete))
            (let ((r2 (dlm-nth result 3)))
              (set result (s79-field result 3 (s79-field r2 3
                (s79-put (dlm-nth r2 3) e (dlm-nth result 2))))))) result))))))
(define-function b90-metrics (r)
  (list 'metrics90 (dlm-nth r 2) (dlm-nth r 4) (dlm-nth r 5)
        (dlm-nth r 6) (dlm-nth r 7) (dlm-nth r 8)))
(define-function b90-execute (s episode names fuel arm)
  (if (not (and (b90-state? s)
                (b90-name? episode) (b90-find (dlm-nth s 3) episode) (b90-names? names 16)
                (is <long> fuel) (>= fuel 0) (<= fuel 200000)
                (dlm-member? arm '(raw append basis memo)))) '(rejected90 execution-input)
    (let ((tasks ()) (ok true) (answers ()) (status 'complete) (r (b90-runtime fuel))
          (facts (dlm-nth (b90-find (dlm-nth s 3) episode) 2)))
      (if names
        (list-do id names (let ((task (b90-find (dlm-nth s 5) id)))
          (if task (set tasks (dlm-append tasks (list task))) (set ok false))))
        (set tasks (dlm-nth s 5)))
      (if (not ok) '(rejected90 task-id)
        (begin
          (list-do task tasks
            (if (= status 'complete)
              (let* ((expr (if (= arm 'basis) (dlm-nth task 3)
                            (if (= arm 'memo) (b90-expression (b90-tokens (dlm-nth task 2))) (dlm-nth task 2))))
                     (v (b90-evaluate expr facts (dlm-nth s 4) r (= arm 'memo))))
                (set r (dlm-nth v 3)) (set status (dlm-nth v 1))
                (if (= status 'complete) (set answers (dlm-append answers
                  (list (list 'answer90 (dlm-nth task 1) (dlm-nth v 2)))))))))
          (list 'execution90 status answers (b90-metrics r)))))))
;;; Held-out queries are transient. No task/support/audit/statistics publication.
(define-function b90-query (s episode expression fuel arm)
  (if (not (and (b90-state? s) (b90-word expression (dlm-nth s 2) () 8)))
    '(rejected90 query)
    (let* ((task (list 'task90 'query90 expression (b90-plan expression (dlm-nth s 2) (dlm-nth s 4))))
           (view (s79-field s 5 (list task))))
      (b90-execute view episode '(query90) fuel arm))))
