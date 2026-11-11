(print "LOAD " (w-load "/tmp/dlm-web-store.l") "\n")
(print "P2 " (l-nth (nl-answer-with (w-facts) (w-rules) "Is a dog a living thing?") 1) "\n")
(print "P3 " (l-nth (nl-answer-with (w-facts) (w-rules) "Is a dog a plant?") 1) "\n")
(print "done-persist-p2\n")
