;;; d107-read.l — leveled reading with a support check on every sentence.
;;; A readable fact whose proof does not check is withheld (abstain), never
;;; reported as if it were certified. Levels follow the 0.0062 vocabulary:
;;; N1 relation, N2 meaning, N3 idiom. N4-N9 are not implemented in M1.

(define-function p107-human (x) (if (string? x) x (symbol->string x)))
(define-function p107-cap (s)
  (if (= 0 (string-length s)) s
    (let* ((c (string-at s 0)) (r (string (string-length s))) (i 0))
      (list-do ch (p107-map (lambda (k) (string-at s k)) (p107-range (string-length s)))
        (set (string-at r i) (if (and (= i 0) (>= ch 97) (<= ch 122)) (- ch 32) ch))
        (set i (+ i 1)))
      r)))
(define-function p107-sentence (s) (concat-strings s "."))

(define-function p107-readable-level (p)
  (cond ((equal p 'calls) 1)
        ((equal p 'has_layer) 1)
        ((equal p 'method_of) 1)
        ((equal p 'meaning) 2)
        ((equal p 'calls_concept) 3)
        (else 0)))

(define-function p107-text (a)
  (let ((p (p107-pred a)) (xs (p107-args a)))
    (cond
      ((equal p 'calls)
        (p107-sentence (concat-strings (p107-human (p107-nth xs 0))
          (concat-strings " calls " (p107-human (p107-nth xs 1))))))
      ((equal p 'has_layer)
        (p107-sentence (concat-strings (p107-human (p107-nth xs 0))
          (concat-strings " contains a " (concat-strings (p107-human (p107-nth xs 1)) " layer")))))
      ((equal p 'method_of)
        (p107-sentence (concat-strings (p107-human (p107-nth xs 0))
          (concat-strings " defines " (p107-human (p107-nth xs 1))))))
      ((equal p 'meaning)
        (p107-sentence (concat-strings (p107-human (p107-nth xs 0))
          (concat-strings " is about " (p107-human (p107-nth xs 1))))))
      ((equal p 'calls_concept)
        (p107-sentence (concat-strings (p107-human (p107-nth xs 0))
          (concat-strings " calls " (p107-human (p107-nth xs 1))))))
      (else ""))))

(define-function p107-read (s scope budget)
  (let* ((c (p107-closure s scope budget))
         (status (p107-nth c 0)) (table (p107-nth c 1))
         (out ()) (skipped 0))
    (list-do f table
      (let* ((a (p107-nth f 2)) (lvl (p107-readable-level (p107-pred a))))
        (if (> lvl 0)
          (if (p107-proof-ok? (p107-nth f 3) a table *p107-rules*)
            (set out (p107-append out (list (list 'sentence107 lvl (p107-text a) a (p107-nth f 3)))))
            (set skipped (+ skipped 1))))))
    (list 'reading107 scope status (p107-len table) out skipped)))

(define-function p107-level-count (sentences lvl)
  (let ((n 0)) (list-do x sentences (if (= (p107-nth x 1) lvl) (set n (+ n 1)))) n))
(define-function p107-levels (sentences)
  (let ((out ())) (list-do l (p107-range 10)
    (let ((n (p107-level-count sentences l))) (if (> n 0) (set out (p107-append out (list (list 'level l n)))))))
    out))