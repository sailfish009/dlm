;;; -*- mode: lisp; coding: us-ascii -*-
;;; Small POSIX file operations for native, transactional session snapshots.
;;; Constants are Linux x86-64 syscall ABI values, not libc dependencies.
(define-constant linux/session-SYS-flock 73)
(define-constant linux/session-SYS-rename 82)
(define-constant linux/session-SYS-unlink 87)
(define-constant linux/session-LOCK-EX-NB 6)

;; () means ENOENT only; other failures are negative errno values.
(define-vm-function file-open-read ((path <string>))
  (let ((fd (posix/open (string->C-string path) linux/O_RDONLY posix/default-file-mode)))
    (if (>= fd 0) (box <lower-cell> fd)
      (if (= fd (- linux/ENOENT)) () (box <long> fd)))))

(define-vm-function file-lock ((path <string>))
  (let ((fd (posix/open (string->C-string path)
                       (bitwise-or linux/O_RDWR linux/O_CREAT) posix/default-file-mode)))
    (if (< fd 0) ()
      (if (= 0 (syscall linux/session-SYS-flock fd linux/session-LOCK-EX-NB))
          (box <lower-cell> fd)
        (begin (posix/close fd) ())))))

(define-vm-function file-replace ((from <string>) (to <string>))
  (to-upper-boolean (= 0 (syscall linux/session-SYS-rename
    (string->C-string from) (string->C-string to)))))

(define-vm-function file-remove ((path <string>))
  (to-upper-boolean (= 0 (syscall linux/session-SYS-unlink (string->C-string path)))))
