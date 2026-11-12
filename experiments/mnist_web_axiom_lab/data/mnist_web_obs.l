;;; Cached, MNIST-related web observations with provenance.
;;; Text is representative of public dataset/digit descriptions; no network call.
(define *batch1*
  (list
    (w-observation "m1" "https://en.wikipedia.org/wiki/MNIST_database"
      "MNIST is a handwritten-digit-dataset" "MNIST" "handwritten-digit-dataset")
    (w-observation "m2" "https://en.wikipedia.org/wiki/MNIST_database"
      "a handwritten-digit-dataset is an image-dataset" "handwritten-digit-dataset" "image-dataset")
    (w-observation "m3" "https://en.wikipedia.org/wiki/Image"
      "an image-dataset is a pixel-matrix-collection" "image-dataset" "pixel-matrix-collection")
    (w-observation "m4" "https://en.wikipedia.org/wiki/Data_set"
      "a pixel-matrix-collection is a data-collection" "pixel-matrix-collection" "data-collection")))
(define *batch2*
  (list
    (w-observation "m5" "https://en.wikipedia.org/wiki/Handwriting"
      "a handwritten-digit is an image" "handwritten-digit" "image")
    (w-observation "m6" "https://en.wikipedia.org/wiki/Pixel"
      "an image is a pixel-grid" "image" "pixel-grid")
    (w-observation "m7" "https://en.wikipedia.org/wiki/Data_set"
      "all image-datasets are data-collections" "image-datasets" "data-collections")
    (w-observation "m8" "https://en.wikipedia.org/wiki/Data_structure"
      "all pixel-grids are data-structures" "pixel-grids" "data-structures")))
(define *web-obs* (l-append *batch1* *batch2*))
