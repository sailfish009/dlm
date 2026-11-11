# synth_mlir_auto_repl — automatic mode selection (0.0173)

Run:

```bash
./scripts/synth_mlir_auto.sh
```

Both modules use `synth-search` mode `auto`. A single-predicate chain selects
`stride`; an alternating `up/down` chain selects `pair`. The selected program is
equal to the corresponding direct synthesizer result.

This selects between two fixed families; it does not invent a new family.
