# synth_recursive_repl — recursive seed+step synthesis (0.0166)

Run:

```bash
./scripts/synth_recursive.sh
```

From direct `ancestor` examples and `parent` edges, the synthesizer finds a
seed rule plus a recursive step rule. The pair transfers to a held four-hop
chain with no ancestor facts. Seed-only and frozen controls fail.

This is recursive two-rule program synthesis, not general ILP.
