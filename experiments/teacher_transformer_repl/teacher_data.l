(define *teacher-facts*
  (list
    (l-fact "e0a" (l-atom 'edge1 (list 'a 'b)))
    (l-fact "e0b" (l-atom 'edge2 (list 'b 'c)))
    (l-fact "e1a" (l-atom 'edge1 (list 'd 'e)))
    (l-fact "e1b" (l-atom 'edge2 (list 'e 'f)))
    (l-fact "e2a" (l-atom 'edge1 (list 'g 'h)))
    (l-fact "e2b" (l-atom 'edge2 (list 'h 'i)))
    (l-fact "e3a" (l-atom 'edge1 (list 'j 'k)))
    (l-fact "e3b" (l-atom 'edge2 (list 'k 'l)))
    (l-fact "e4a" (l-atom 'edge1 (list 'm 'n)))
    (l-fact "e4b" (l-atom 'edge2 (list 'n 'o)))
  ))
(define *teacher-pos*
  (list
    (l-atom 'path (list 'a 'c))
    (l-atom 'path (list 'd 'f))
    (l-atom 'path (list 'g 'i))
  ))
(define *teacher-neg*
  (list
    (l-atom 'path (list 'c 'a))
    (l-atom 'path (list 'f 'd))
    (l-atom 'path (list 'i 'g))
  ))
(define *held-pos*
  (list
    (l-atom 'path (list 'j 'l))
    (l-atom 'path (list 'm 'o))
  ))
(define *held-neg*
  (list
    (l-atom 'path (list 'l 'j))
    (l-atom 'path (list 'o 'm))
  ))
