(define *web-edges*
  (list
    (l-fact "e0" (l-atom 'subclass (list 'dog 'mammal)))
    (l-fact "e1" (l-atom 'subclass (list 'cat 'mammal)))
    (l-fact "e2" (l-atom 'subclass (list 'bird 'animal)))
    (l-fact "e3" (l-atom 'subclass (list 'sparrow 'bird)))
    (l-fact "e4" (l-atom 'subclass (list 'mammal 'animal)))
    (l-fact "e5" (l-atom 'subclass (list 'animal 'living-thing)))
    (l-fact "e6" (l-atom 'subclass (list 'plant 'living-thing)))
  ))

(define *web-sources*
  (list
    "dog->mammal: Dogs are mammals, usually to be kept as pets, or work on farms or for the police."
    "cat->mammal: Cats, also called domestic cats, are small, carnivorous mammals, of the family Felidae."
    "bird->animal: Birds (Aves) are a group of animals with backbones."
    "sparrow->bird: They are small passerine birds which belong to the family Passeridae."
    "mammal->animal: They are a group of vertebrate animals."
    "animal->living-thing: Animals are living creatures with many cells that make up the kingdom Animalia."
    "plant->living-thing: Plants are one of six big groups (kingdoms) of living things."
  ))

(define *train-facts*
  (list
    (l-fact "t0" (l-atom 'subclass (list 'dog 'mammal)))
    (l-fact "t1" (l-atom 'subclass (list 'cat 'mammal)))
    (l-fact "t2" (l-atom 'subclass (list 'bird 'animal)))
    (l-fact "t3" (l-atom 'subclass (list 'sparrow 'bird)))
    (l-fact "t4" (l-atom 'subclass (list 'mammal 'animal)))
  ))

(define *train-pos*
  (list
    (l-atom 'isa (list 'cat 'animal))
    (l-atom 'isa (list 'dog 'animal))
    (l-atom 'isa (list 'sparrow 'animal))
  ))

(define *neg*
  (list
    (l-atom 'isa (list 'animal 'cat))
    (l-atom 'isa (list 'animal 'dog))
    (l-atom 'isa (list 'animal 'sparrow))
  ))
