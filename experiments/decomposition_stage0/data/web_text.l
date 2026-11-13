;;; Actual Wikipedia text samples; text-only fields (no gold/axiom fields).
(define-function wtext (id url text) (list 'wtext id url text))
(define *web-text*
  (list
    (wtext "m1" "https://en.wikipedia.org/wiki/MNIST_database" "The MNIST database is a large database of handwritten digits that is commonly used for training various image processing systems.")
    (wtext "m2" "https://en.wikipedia.org/wiki/MNIST_database" "The database is also widely used for training and testing in the field of machine learning.")
    (wtext "m3" "https://en.wikipedia.org/wiki/MNIST_database" "It was created by re-mixing the samples from NIST's original datasets.")
    (wtext "h1" "https://en.wikipedia.org/wiki/Handwriting" "Handwriting is the personal and unique style of writing with a writing instrument, such as a pen or pencil in the hand.")
    (wtext "h2" "https://en.wikipedia.org/wiki/Handwriting" "Handwriting includes both block and cursive styles and is separate from generic and formal handwriting script/style, calligraphy or typeface.")
    (wtext "h3" "https://en.wikipedia.org/wiki/Handwriting" "Because each person's handwriting is unique and different, it can be used to verify a document's writer.")
    (wtext "i1" "https://en.wikipedia.org/wiki/Image" "An image or picture is a visual representation.")
    (wtext "i2" "https://en.wikipedia.org/wiki/Image" "An image can be two-dimensional, such as a drawing, painting, or photograph, or three-dimensional, such as a carving or sculpture.")
    (wtext "p1" "https://en.wikipedia.org/wiki/Pixel" "In digital imaging, a pixel (abbreviated px), pel, or picture element is the smallest addressable element of a raster image.")
    (wtext "p2" "https://en.wikipedia.org/wiki/Pixel" "In a display device, dot matrix printer, or ASCII art a pixel is the smallest element whose output can generally be controlled independently.")
    (wtext "d1" "https://en.wikipedia.org/wiki/Data_set" "A data set (or dataset) is a collection of data.")
    (wtext "d2" "https://en.wikipedia.org/wiki/Data_set" "The data set lists values for each of the variables, such as for example height and weight of an object, for each member of the data set.")
    (wtext "c1" "https://en.wikipedia.org/wiki/Convolutional_neural_network" "A convolutional neural network (CNN) is a type of feedforward neural network that learns features via filter (or kernel) optimization.")
    (wtext "c2" "https://en.wikipedia.org/wiki/Convolutional_neural_network" "This type of deep learning network has been applied to process and make predictions from many different types of data including text, images and audio.")
    (wtext "c3" "https://en.wikipedia.org/wiki/Convolutional_neural_network" "CNNs are the de-facto standard in deep learning-based approaches to computer vision and image processing, and have only recently been replaced—in some cases—by newer architectures such as the transformer.")))
