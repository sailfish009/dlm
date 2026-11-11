# mlir_repl — MLIR-shaped fragment IR (0.0159)

Run:

```bash
./scripts/mlir.sh
```

A 16-operation MLIR-shaped module declares fragments, combines/templates,
programs and fixed tasks. It lowers to the existing fragment/match core in the
Maru REPL.

This is an internal dialect, not upstream MLIR; it preserves self-host.
