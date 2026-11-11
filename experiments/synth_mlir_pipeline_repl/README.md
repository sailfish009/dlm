# synth_mlir_pipeline_repl — search + proof as MLIR ops (0.0172)

Run:

```bash
./scripts/synth_mlir_pipeline.sh
```

Each module contains a `synth-search` op and two `synth-proof` ops. The search
op selects the same program as the direct synthesizer; the proof ops return
`proof` for the held positive and `fail` for the held negative.

This is MLIR-shaped orchestration, not a decomposed MLIR pass pipeline.
