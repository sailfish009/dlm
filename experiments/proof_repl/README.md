# proof_repl — proof credit and failure frontier (0.0161)

Run:

```bash
./scripts/proof.sh
```

Round 1 proves an ancestor goal and reports essential rules. A path goal exposes
the missing path relation in the frontier. Round 2 adds p-comp, proves path, and
retains p-rec for another ancestor chain.

This is a controlled failure-triggered curriculum, not label-free self-supervision.
