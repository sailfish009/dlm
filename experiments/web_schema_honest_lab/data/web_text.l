;;; Web text only: no subj/obj/kind/gold fields.
(define-function wtext (id url text) (list 'wtext id url text))
(define *web-text*
  (list
    (wtext "m1" "https://en.wikipedia.org/wiki/MNIST_database" "a MNIST is a handwritten-digit-dataset")
    (wtext "m2" "https://en.wikipedia.org/wiki/MNIST_database" "a handwritten-digit-dataset is a image-dataset")
    (wtext "m3" "https://en.wikipedia.org/wiki/Image" "an image-dataset is a pixel-matrix-collection")
    (wtext "m4" "https://en.wikipedia.org/wiki/Data_set" "a pixel-matrix-collection is a data-collection")
    (wtext "m5" "https://en.wikipedia.org/wiki/Handwriting" "a handwritten-digit is a image")
    (wtext "m6" "https://en.wikipedia.org/wiki/Pixel" "an image is a pixel-grid")
    (wtext "m7" "https://en.wikipedia.org/wiki/Data_set" "all image-datasets are data-collections")
    (wtext "m8" "https://en.wikipedia.org/wiki/Data_structure" "all pixel-grids are data-structures")
    ;; Distractors: text-only false candidates; not in gold.
    (wtext "d1" "https://example.org/noise" "a dataset is a collection")
    (wtext "d2" "https://example.org/noise" "an image is a file")
    (wtext "d3" "https://example.org/noise" "a pixel is a number")))
