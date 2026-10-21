;;; -*- mode: lisp; coding: us-ascii -*-
;;; Opt-in, cooperative tasks in the EXISTING reader. No second parser or REPL.
;;; Task data live in the normal global environment and are traced by the GC.
(define-function repl-task-value (name)
  (maybe-variable-value *globals* (string->symbol name)))

(define-vm-function repl-idle-task (expression (milliseconds <long> 1000))
  (unless (or (not expression) (pair? expression))
    (error "repl-idle-task: expected an expression or ()"))
  (unless (and (<= 20 milliseconds) (<= milliseconds 60000))
    (error "repl-idle-task: interval must be 20..60000 ms"))
  (set-variable-value *globals* (string->symbol "*repl-task-interval*") (box <long> milliseconds))
  (set-variable-value *globals* (string->symbol "*repl-task-expression*") expression)
  expression)

(define-record <cooperative-input> <stream> (input output))

(define-function cooperative-input (input output)
  (make <cooperative-input> (input input) (output output)))

(define-method $peek <cooperative-input> ()
  (gc/let* ((task (repl-task-value "*repl-task-expression*")))
    (while (not (platform/input-ready? self.input
                  (if task (unbox <long> (repl-task-value "*repl-task-interval*")) -1)))
      (when task
        ($put self.output ?\n)
        (expand-encode-eval task)
        ($put-all self.output "maru> ")
        (platform/flush-streams))
      (set task (repl-task-value "*repl-task-expression*"))))
  ($peek self.input))

(define-method $next <cooperative-input> ()
  ($peek self)
  ($next self.input))

(define-method $at-end? <cooperative-input> ()
  (= +end+ ($peek self)))
