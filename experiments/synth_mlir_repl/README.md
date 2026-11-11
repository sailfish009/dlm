# synth_mlir_repl — synthesis as MLIR-shaped ops (0.0171)

Run:

```bash
./scripts/synth_mlir.sh
```

Two modules express seed/step/program synthesis as MLIR-shaped ops. `ml-run`
lowers them to the existing `synth.l` core; the lowered rules are compared with
direct `s-stride-synthesize` and `s-pair-synthesize` and must be equal.

This is explicit template IR, not a full MLIR pass pipeline.
