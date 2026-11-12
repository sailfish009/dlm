;;; Evaluator-only gold; never passed to the extractor.
(define *gold*
  (list
    (list "m1" 'nl-fact 'mnist 'handwritten-digit-dataset)
    (list "m2" 'nl-fact 'handwritten-digit-dataset 'image-dataset)
    (list "m3" 'nl-fact 'image-dataset 'pixel-matrix-collection)
    (list "m4" 'nl-fact 'pixel-matrix-collection 'data-collection)
    (list "m5" 'nl-fact 'handwritten-digit 'image)
    (list "m6" 'nl-fact 'image 'pixel-grid)
    (list "m7" 'nl-rule 'image-dataset 'data-collection)
    (list "m8" 'nl-rule 'pixel-grid 'data-structure)))
