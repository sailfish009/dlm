(w-clear)
(w-ingest (list
  (w-observation "p1" "https://example.org/1" "A dog is a mammal." 'dog 'mammal)
  (w-observation "p2" "https://example.org/1" "All mammals are animals." 'mammal 'animal)
  (w-observation "p3" "https://example.org/1" "All animals are living things." 'animal 'living-thing)))
(print "SAVE " (w-save "/tmp/dlm-web-store.l") " obs=" (l-len *web-store*) " rules=" (l-len (b-active-rules *web-basis*)) "\n")
(print "P1 " (l-nth (nl-answer-with (w-facts) (w-rules) "Is a dog a living thing?") 1) "\n")
(print "done-persist-p1\n")
