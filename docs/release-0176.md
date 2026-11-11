# Release 0.0176 — explicit MLIR-shaped graph IR (candidate)

- Date: 2026-11-08
- Predecessor: 0.0175. Candidate, not promoted.
- Scope: add explicit value/node/edge graph IR, structural verification, topological
  ordering, and lowering back to the existing linear module.
- Analysis: `/research/analysis-graph-ir-0176.md`.

## Changes

New `src/dlm/graph-ir.l`:

```text
mg-value ID TYPE PRODUCER
mg-node  ID KIND INPUTS OUTPUTS ATTRS
mg-edge  VALUE NODE PORT
mg-graph VALUES NODES EDGES
```

Operations:

```text
mg-from-module  linear ml-module → graph (fragment/combine/template/program/task)
mg-check        unique IDs, defined values, valid edges, valid producers
mg-topo         dependency order; rejects cycles
mg-to-module    graph → linear ml-module in topological order
```

`scripts/run.sh` loads `graph-ir.l` after `mlir.l`.

## Experiment

`experiments/graph_ir_repl/` + `scripts/graph_ir.sh`:

```text
GRAPH check=ok topo=(fseed seed p t) values=4 nodes=4 edges=1
LINEAR run=(summary tasks 1 solved 1 active (p)) rebuilt=(summary tasks 1 solved 1 active (p)) same=yes
DUP (rejected107 mg-node-id)
BADEDGE (rejected107 mg-edge-input)
done-graph-ir
```

The graph verifies, topo-sorts, lowers back, and produces the same run summary.
Duplicate node IDs and an edge that points at the wrong input are rejected.

## Self-host

```text
compiler.sh reproduce
→ 20261109T105915Z-11199
compiler.sh verify 20261109T105915Z-11199
→ Verified
```

## Measured

```text
native normal   44 checks / 0 FAIL
native safety-2 44 checks / 0 FAIL
self-host       verified
```

## Implementation note

The graph uses the original op ID as the node ID and a fresh `vN` value ID. An
old fragment/template pair that reused the same ID (e.g. both `"seed"`) is not a
valid graph; the experiment uses distinct `"fseed"` and `"seed"` IDs.

## Still not

- Constraint records are not attached yet.
- No CSE/DCE/fusion/partition pass.
- No embedding attribute yet.
- Lowering is graph → linear `ml-op`, not graph → optimizer pipeline.
- Truth remains with the proof checker.
