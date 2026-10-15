# experiments/recursive — recursive self-supervised learning (v0.0055)

The model is given a directed graph as `edge` facts and **not** the relational
transitive rule. Each round it closes the relation it currently has under two
GIVEN definitional level rules and reifies the certified extension as a new
predicate, feeding its own output back as the next round's input:

```
r_{k+1}(X,Y) :- r_k(X,Y).                 -- inherit
r_{k+1}(X,Z) :- r_k(X,Y), r_k(Y,Z).       -- compose (self-join)
```

The kernel is the only judge; there are no labels. A round doubles the path
length the relation spans, so the model reaches the full transitive closure in
**O(log diameter)** rounds and abstains at the fixpoint (a round adds nothing).

## Run

```bash
./experiments/recursive/recursive.sh            # chain24 + dag16
OUTDIR=reports/recursive/mine ./experiments/recursive/recursive.sh
```

Writes `reports/recursive/<stamp>/result.json`.

## Falsifiers (all must hold)

| verdict | meaning |
|---|---|
| `sound` | every derived pair is a true reachable pair |
| `complete` | the fixpoint equals the full transitive closure |
| `recursion_grows` | more than one round and a later round still adds pairs |
| `fixpoint_reached` | a round adds nothing and the loop stops |
| `one_shot_insufficient` | a single composition (depth-1 control) does **not** reach the closure |
| `sublinear_depth` | depth ≤ ceil(log2 diameter) + 2 (not linear) |
| `deterministic` | two runs are identical |

Measured: 25-node chain (diameter 24) → 300/300 true pairs, false 0, depth 6
(bound 7), one-shot 47; 16-node DAG (diameter 4) → 120/120, depth 3.