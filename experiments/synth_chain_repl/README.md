# synth_chain_repl — three-fact chain synthesis (0.0164)

Run:

```bash
./scripts/synth_chain.sh
```

The target path requires three hops. Two-fact candidates are empty; the
three-fact candidate is synthesized, checked against positive/negative facts,
and transfers to a held chain.

This is fixed-length chain synthesis, not general ILP.
