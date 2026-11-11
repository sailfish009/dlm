# Release 0.0198 — axiom graph dependency DCE (candidate)

- Date: 2026-11-10
- Predecessor: 0.0197. Candidate, not promoted.
- Scope: backward dependency reachability and dead-axiom elimination on the
  MLIR-shaped axiom graph.
- Analysis: `/research/analysis-axiom-dce-0198.md`.

## Changes

`src/dlm/axiom-graph.l`:

```text
ag-reach
ag-dce
```

`experiments/axiom_dce_repl/` + `scripts/axiom_dce.sh`.

## Experiment

```text
BEFORE 3 AFTER 2 check=ok
AG SEL (A-0 A-1)
done-axiom-dce
```

An unrelated `X` axiom is present in the graph. DCE from root `A-1` keeps
`A-1 -> A-0` by dependency reachability and drops `X`.

## Self-host

```text
compiler.sh reproduce
→ 20261110T105451Z-13270
compiler.sh verify 20261110T105451Z-13270
→ Verified
```

## Measured

```text
native normal   64 checks / 0 FAIL
native safety-2 64 checks / 0 FAIL
self-host       verified
```

## Implementation note

Earlier experiments redefined `axs` with `define`; in this evaluator the new
binding can hide the old value while evaluating the initializer. The DCE
experiment uses `set axs ...` for the incremental add. This also explains why an
earlier activation test appeared to lose the first axiom.

## Still not

- no CSE/SCC pass
- no cost/MDL attributes
- activation lifecycle not integrated
- graph is MLIR-shaped, not upstream MLIR
- truth remains with the proof checker
