;;;; screamer_search.lisp — external backtracking search (Screamer, SBCL) driven by
;;;; the native C transformer (bin/serve).  Plain helpers live in CL-USER; only the
;;;; nondeterministic search functions live in a Screamer package (its DEFUN is
;;;; CPS-transformed, so unsupported forms must stay outside).
(require :asdf)
(push #p"/research/screamer/" asdf:*central-registry*)
(asdf:load-system :screamer)

(in-package :cl-user)

(defparameter *dump* "out/hard_worlds.txt")
(defparameter *weights* "probes/w_11.bin")
(defparameter *cap* 2000)
(defvar *server* nil)
(defvar *binary-path* nil)
(defvar *rules* nil)
(defvar *worlds* nil)
(defvar *cands* 0)
(defvar *branch* 3)
(defvar *states* 0)
(defvar *best* 0)
(defvar *best-seq* nil)

(defun all-rules ()
  (let ((out '()))
    (dotimes (h 6)
      (dotimes (b 6) (when (/= b h) (push (cons h (list b)) out)))
      (dotimes (b1 6)
        (dotimes (b2 6)
          (when (and (< b1 b2) (/= h b1) (/= h b2)) (push (cons h (list b1 b2)) out)))))
    (coerce (nreverse out) 'vector)))

(defun split (str sep)
  (let ((out '()) (start 0))
    (loop for i from 0 to (length str)
          when (or (= i (length str)) (char= (char str i) sep))
            do (when (> i start) (push (subseq str start i) out))
               (setf start (1+ i)))
    (nreverse out)))

(defun parse-dump (path)
  (let ((worlds '()))
    (with-open-file (s path)
      (loop for line = (read-line s nil nil) while line do
        (let* ((tk (split line #\Space))
               (tag (first tk))
               (rest (rest tk)))
          (cond
            ((equal tag "W")
             (push (list :split (parse-integer (nth 0 rest)) :idx (parse-integer (nth 1 rest))
                         :ngoals (parse-integer (nth 2 rest))
                         :facts nil :theory nil :cands nil :goals nil)
                   worlds))
            ((equal tag "F") (setf (getf (first worlds) :facts) (mapcar #'parse-integer rest)))
            ((equal tag "T") (setf (getf (first worlds) :theory) (mapcar #'parse-integer rest)))
            ((equal tag "C") (setf (getf (first worlds) :cands) (mapcar #'parse-integer rest)))
            ((equal tag "G")
             (setf (getf (first worlds) :goals)
                   (mapcar (lambda (tok) (mapcar #'parse-integer (split tok #\:))) rest)))
            (t nil)))))
    (coerce (nreverse worlds) 'vector)))

(defun apply-rule (facts rule)
  (let ((h (car rule)) (body (cdr rule)) (out (copy-list facts)) (changed nil)
        (bm 0))
    (dolist (p body) (setf bm (logior bm (ash 1 p))))
    (dotimes (e 6)
      (let ((m (nth e facts)))
        (when (and (= (logand m bm) bm) (zerop (logand m (ash 1 h))))
          (setf (nth e out) (logior m (ash 1 h)) changed t))))
    (values out changed)))

(defun closure (facts rule-ids)
  (loop with f = (copy-list facts) with changed = t
        while changed do
          (setf changed nil)
          (dolist (id rule-ids)
            (multiple-value-bind (nf ch) (apply-rule f (aref *rules* id))
              (when ch (setf f nf changed t))))
        finally (return f)))

(defun goals-proved (w rule-ids)
  (let ((f (closure (getf w :facts) rule-ids)) (n 0))
    (dolist (g (getf w :goals))
      (when (logbitp (first g) (nth (second g) f)) (incf n)))
    n))

(defun start-server ()
  (setf *server* (sb-ext:run-program *binary-path* (list "--serve" *weights*)
                                     :input :stream :output :stream :wait nil :search nil
                                     :external-format :ascii)))

(defun c-order (widx rule-ids)
  (let ((in (sb-ext:process-input *server*))
        (out (sb-ext:process-output *server*)))
    (format in "~d ~d~{ ~d~}~%" widx (length rule-ids) rule-ids)
    (finish-output in)
    (let* ((tk (split (read-line out) #\Space))
           (n (parse-integer (first tk)))
           (pairs '()))
      (loop for i from 0 below n
            for id = (parse-integer (nth (1+ (* 2 i)) tk))
            for sc = (read-from-string (nth (+ 2 (* 2 i)) tk))
            do (push (cons id sc) pairs))
      (nreverse pairs))))

;;; ---- nondeterministic part (Screamer package: DEFUN is CPS-transformed) ----
(in-package :screamer-user)
(define-screamer-package :pst-nd)
(in-package :pst-nd)

(defun try-rules (w idx rule-ids depth xs)
  (if xs
      (either (screamer-dfs w idx (append rule-ids (list (car xs))) (1+ depth))
              (try-rules w idx rule-ids depth (cdr xs)))
      (fail)))

(defun screamer-dfs (w idx rule-ids depth)
  (incf cl-user::*states*)
  (if (>= depth 4)
      (let ((g (cl-user::goals-proved w rule-ids)))
        (when (> g cl-user::*best*) (setf cl-user::*best* g cl-user::*best-seq* (reverse rule-ids)))
        (local g))
      (let ((order (cl-user::c-order idx rule-ids)))
        (let* ((ids (mapcar #'car (sort (copy-list order) #'> :key #'cdr)))
               (keep (if (>= cl-user::*branch* (length ids)) ids
                         (subseq ids 0 cl-user::*branch*))))
          (incf cl-user::*cands* (length order))   ; same unit as the C cand counter
          (try-rules w idx rule-ids depth keep)))))

(defun run-dfs (w idx theory)
  ;; enumerate every leaf (DFS + backtracking) up to the candidate cap
  (let ((vals (all-values (screamer-dfs w idx theory 0))))
    (declare (ignore vals))
    cl-user::*best*))

;;; ---- driver (plain CL) ----
(in-package :cl-user)

(defun run-world (idx w)
  (setf *best* 0 *best-seq* nil *states* 0 *cands* 0)
  (handler-case (pst-nd::run-dfs w idx (getf w :theory))
    (error (e) (format t "  world ~d error: ~a~%" idx e)))
  (format t "SCREAMER world=~d best=~d/~d states=~d cands=~d seq=~a~%"
          idx *best* (getf w :ngoals) *states* *cands* *best-seq*))

(defvar *world-cap* nil)
(defun main ()
  (let ((args (uiop:command-line-arguments)))
    (setf *world-cap* (if (fifth args) (parse-integer (fifth args)) 20))
    (setf *binary-path* (or (first args) "bin/serve")
          *dump* (or (second args) "out/hard_worlds.txt")
          *weights* (or (third args) "probes/w_11.bin")
          *branch* (if (fourth args) (parse-integer (fourth args)) 3)))
  (setf *rules* (all-rules) *worlds* (parse-dump *dump*))
  (start-server)
  (let ((n (min *world-cap* (length *worlds*))) (tot 0) (gt 0) (cands 0))
    (dotimes (i n)
      (let ((w (aref *worlds* i)))
        (run-world i w)
        (incf tot *best*) (incf gt (getf w :ngoals)) (incf cands *cands*)))
    (format t "SCREAMER-SUMMARY worlds=~d branch=~d best_frac=~,4f cands_total=~d~%"
            n *branch* (/ (float tot) gt) cands))
  (sb-ext:process-close *server*))

(main)
