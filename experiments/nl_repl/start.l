;;; English natural language → facts/rules → proof → English answer.
(define texts (list
  "A cat is a mammal."
  "A dog is a mammal."
  "All mammals are animals."
  "All animals are living things."))
(define q1 "Is a cat a living thing?")
(define q2 "Is a cat a plant?")
(define r1 (nl-run texts q1))
(define r2 (nl-run texts q2))
(print "PARSED " (l-map nl-parse texts) "\n")
(print "BASIS RULES " (l-len (b-active-rules (nl-basis (l-map nl-parse texts)))) "\n")
(print "STATUS1 " (l-nth r1 1) "\n")
(print "ANSWER1 " (l-nth r1 3) "\n")
(print "WHY1 " (l-nth r1 4) "\n")
(print "STATUS2 " (l-nth r2 1) "\n")
(print "ANSWER2 " (l-nth r2 3) "\n")
(print "done-nl\n")
