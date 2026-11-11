# graph_select_repl — constraint-guided selection (0.0181)

Run:

```bash
./scripts/graph_select.sh
```

Two hard-valid graph candidates differ in a soft constraint. The selector picks
the candidate with the higher soft score and runs it normally. A hard-invalid
candidate is filtered out.

Soft scores only select among candidates; they do not decide truth.
