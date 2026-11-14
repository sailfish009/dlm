;;; fx.l — Q16 fixed-point kernels for the tiny transformer port.
;;; all values are integers; real value = X / 65536.

(define-function fx-one () 65536)

(define-function fx-mul (a b)
  (bitwise-shift (* a b) -16))

(define-function fx-div (a b)
  (if (= b 0) 0 (/ (bitwise-shift a 16) b)))

(define-function fx-isqrt-up (hi n)
  (if (> (* hi hi) n) hi (fx-isqrt-up (* hi 2) n)))

(define-function fx-isqrt-search (lo hi n)
  (if (<= (- hi lo) 1) lo
    (let ((mid (/ (+ lo hi) 2)))
      (if (<= (* mid mid) n)
          (fx-isqrt-search mid hi n)
          (fx-isqrt-search lo mid n)))))

(define-function fx-isqrt (n)
  (if (<= n 0) 0
    (fx-isqrt-search 0 (fx-isqrt-up 1 n) n)))

(define-function fx-sqrt (x)
  (if (<= x 0) 0 (fx-isqrt (bitwise-shift x 16))))

;;; exp for x <= 0; exp(-16) .. exp(0) table with linear interpolation
(define-function fx-exp (x)
  (if (>= x 0) 65536
    (let* ((t (bitwise-shift (- x) 5)) ; -x * 32
           (i (bitwise-shift t -16))
           (frac (- t (bitwise-shift i 16))))
      (if (>= i 512) 0
        (let ((y0 (l-nth exp-table i))
              (y1 (l-nth exp-table (+ i 1))))
          (+ y0 (fx-mul (- y1 y0) frac)))))))

(define-function v-sum (xs)
  (if xs (+ (car xs) (v-sum (cdr xs))) 0))

(define-function v-add (a b) (map + a b))
(define-function v-sub (a b) (map - a b))
(define-function v-scale (a s) (map (lambda (x) (fx-mul x s)) a))
(define-function v-dot (a b)
  (v-sum (map (lambda (x y) (fx-mul x y)) a b)))
(define-function v-mean (x) (/ (v-sum x) (list-length x)))
(define-function v-var (x mu)
  (/ (v-sum (map (lambda (v) (fx-mul (- v mu) (- v mu))) x))
     (list-length x)))

(define-function mat-vec (rows x)
  (map (lambda (row) (v-dot row x)) rows))

(define-function v-softmax (scores)
  (let* ((m (apply max scores))
         (ex (map (lambda (s) (fx-exp (- s m))) scores))
         (z (v-sum ex)))
    (if (= z 0) (map (lambda (s) 0) scores)
        (map (lambda (e) (/ (bitwise-shift e 16) z)) ex))))

(define-function layernorm (x gamma beta)
  (let* ((mu (v-mean x))
         (var (v-var x mu))
         (inv (fx-div 65536 (fx-sqrt (+ var 1)))))
    (map (lambda (xi gi bi)
           (+ (fx-mul (fx-mul (- xi mu) inv) gi) bi))
         x gamma beta)))
