(define case-ids (list
  (list 10 5 0 2 11 9 8)
  (list 10 5 0 4 6 9 3)
  (list 10 5 0 2 6 9 3)
  (list 10 5 0 4 11 9 8)
  (list 10 5 0 7 2 6 9 8)
  (list 10 5 0 7 4 11 9 3)
  (list 10 5 0 1 2 11 9 3)
  (list 10 5 0 1 4 6 9 8)))
(define case-en (list
  "there is a cat under the table"
  "there is a dog on the chair"
  "there is a cat on the chair"
  "there is a dog under the table"
  "there is a small cat on the table"
  "there is a small dog under the chair"
  "there is a black cat under the chair"
  "there is a black dog on the table"))
(define case-expected (list
  "桌子下面有一只猫"
  "椅子上面有一只狗"
  "椅子上面有一只猫"
  "桌子下面有一只狗"
  "桌子上面有一只小猫"
  "椅子下面有一只小狗"
  "椅子下面有一只黑色猫"
  "桌子上面有一只黑色狗"))
