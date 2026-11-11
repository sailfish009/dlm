# synth_repl — frontier-driven synthesis (0.0162)

Run:

```bash
./scripts/synth.sh
```

A failed path goal exposes `path(r,t)` in the frontier. Facts hop1(r,s) and
hop2(s,t) synthesize `path(x,z) :- hop1(x,y), hop2(y,z)`. The rule is admitted
only if it proves the target and does not derive the reverse negative relation.

This is a narrow composition synthesis experiment, not general ILP.
