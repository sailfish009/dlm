;;; -*- mode: lisp; coding: us-ascii -*-
;;; Acquired documents are unresolved source data, never Horn facts.
;;; External byte fields are hex symbols; the reader never executes their content.
(define-function web-field (document name)
  (dlm-nth (dlm-assoc name (cdr (cdr document))) 1))

(define-function web-document? (document)
  (and (pair? document) (= (car document) 'document)
       (= (dlm-length document) 10)
       (symbol? (dlm-nth document 1))
       (symbol? (web-field document 'url))
       (symbol? (web-field document 'final-url))
       (symbol? (web-field document 'fetched-at))
       (symbol? (web-field document 'media-type))
       (symbol? (web-field document 'sha256))
       (symbol? (web-field document 'raw))
       (symbol? (web-field document 'source-group))
       (= (web-field document 'status) 'acquired-uninterpreted)))

(define-function web-new () (list 'web-state 74 () ()))

(define-function web-same-content? (left right)
  (let ((same true))
    (list-do name '(url sha256 raw source-group)
      (unless (equal (web-field left name) (web-field right name)) (set same false)))
    same))

;;; A source id identifies URL+content hash. Refetch timestamps stay in events.
(define-function web-merge (documents incoming)
  (let ((result documents))
    (list-do document incoming
      (assert (web-document? document) "invalid source document")
      (let ((prior ()))
        (list-do old result
          (if (equal (dlm-nth old 1) (dlm-nth document 1)) (set prior old)))
        (if prior
            (assert (web-same-content? prior document) "source id changed payload")
          (set result (dlm-append result (list document))))))
    result))

(define-function web-ingest (state batch)
  (assert (and (= (car batch) 'acquisition) (= (dlm-nth batch 1) 74)
               (= (dlm-length batch) 4)) "invalid acquisition bundle")
  (let* ((before (dlm-nth state 2))
         (after (web-merge before (dlm-nth batch 2)))
         (event (list 'acquire batch (dlm-length before) (dlm-length after))))
    (list 'web-state 74 after (dlm-append (dlm-nth state 3) (list event)))))

(define-function web-replay (events)
  (let ((state (web-new)))
    (list-do event events
      (assert (and (= (car event) 'acquire) (= (dlm-length event) 4)) "invalid web event")
      (let ((next (web-ingest state (dlm-nth event 1))))
        (assert (equal event (dlm-nth (dlm-nth next 3)
          (- (dlm-length (dlm-nth next 3)) 1))) "web replay mismatch")
        (set state next)))
    state))

(define-function web-verify-state (state)
  (assert (and (= (car state) 'web-state) (= (dlm-nth state 1) 74)
               (= (dlm-length state) 4)) "invalid web state")
  (assert (equal state (web-replay (dlm-nth state 3))) "web snapshot mismatch")
  state)

(define-function web-report (state)
  (let ((groups ()))
    (list-do document (dlm-nth state 2)
      (set groups (dlm-add groups (web-field document 'source-group))))
    (list 'web-report (list 'documents (dlm-length (dlm-nth state 2)))
          (list 'content-groups (dlm-length groups))
          (list 'acquisitions (dlm-length (dlm-nth state 3)))
          '(admitted-facts 0) '(interpretation unresolved))))
