# synth_pair_repl — two-predicate block synthesis (0.0170)

Run:

```bash
./scripts/synth_pair.sh
```

Alternating `up`/`down` edges cannot be traversed by a single-predicate rule.
The synthesizer finds the ordered block `up, down`, builds a seed and recursive
step, covers the long positive, rejects odd-distance negatives, and transfers
to a held chain.

This is two-predicate block synthesis, not general ILP.
