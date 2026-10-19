(
 (observe (observation ab positive (atom edge (a b)) (provenance fixture () observed)))
 (observe (observation bd positive (atom edge (b d)) (provenance fixture () observed)))
 (observe (observation ac positive (atom edge (a c)) (provenance fixture () observed)))
 (observe (observation cd positive (atom edge (c d)) (provenance fixture () observed)))
 (rule (rule-record base (rule (atom reach ((var x) (var y))) ((atom edge ((var x) (var y))))) (provenance fixture () given)))
 (rule (rule-record chain (rule (atom reach ((var x) (var z))) ((atom reach ((var x) (var y))) (atom edge ((var y) (var z))))) (provenance fixture () given)))
)
