# graph_ir_repl — explicit graph IR (0.0176)

Run:

```bash
./scripts/graph_ir.sh
```

A linear MLIR-shaped module is converted to explicit values/nodes/edges. The
graph checks, topo-sorts, lowers back, and reproduces the same run summary.
Duplicate node IDs and an edge pointing at the wrong input are rejected.

This is structural graph IR, not yet a constraint or embedding layer.
