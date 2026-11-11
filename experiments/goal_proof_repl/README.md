# goal_proof_repl — goal-directed proof (0.0174)

Run:

```bash
./scripts/goal_proof.sh
```

Queries one ancestor chain while unrelated chains grow. Full closure probes grow
with all chains; goal-directed probes and rule scans stay constant. The returned
proof tree is checked against the facts and indexed rules.

This is ground goal-directed proof, not a complete non-ground/negation prover.
