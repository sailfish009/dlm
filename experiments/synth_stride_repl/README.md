# synth_stride_repl — general stride inference (0.0169)

Run:

```bash
./scripts/synth_stride.sh
```

The positive requires distance 6; negatives at distances 2, 4, and 5 reject
strides 1 and 2. The synthesizer selects stride 3 and transfers to a held chain
while still rejecting the held distance-4 negative.

This is bounded stride search, not general theory revision.
