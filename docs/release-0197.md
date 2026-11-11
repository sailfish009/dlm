# Release 0.0197 — MLIR-shaped axiom dependency graph (candidate)

- Date: 2026-11-10
- Predecessor: 0.0196. Candidate, not promoted.
- Scope: lower atomic axioms into an MLIR-shaped dependency graph, verify node
  and dependency structure, enumerate closed subsets, and select the same
  minimal set as the list-based selector.
- Analysis: `/research/analysis-axiom-graph-0197.md`.

## Changes

New `src/dlm/axiom-graph.l`:

```text
mlaxiomgraph
agnode ID RULE EVIDENCE SUPPORT DEPS
ag-from-axioms / ag-to-axioms
ag-check / ag-check-deps
ag-closed? / ag-subsets
ag-select
```

## Experiment

```text
AG nodes=2 check=ok deps=ok
AG SEL (A-0 A-1) COV 3
A SEL (A-0 A-1) SAME yes
HELD 3/3
done-axiom-graph
```

The graph selector and list selector choose the same two axioms. The recursive
step without its seed dependency is excluded by closure checking.

## Self-host

```text
compiler.sh reproduce
→ 20261110T104355Z-8801
compiler.sh verify 20261110T104355Z-8801
→ Verified
```

## Measured

```text
native normal   63 checks / 0 FAIL
native safety-2 63 checks / 0 FAIL
self-host       verified
```

## Still not

- graph is MLIR-shaped, not upstream MLIR
- dependency inference remains simple same-head matching
- no CSE/DCE/SCC pass yet
- no cost/MDL attributes on nodes/edges
- activation lifecycle is not integrated
- truth remains with the proof checker
