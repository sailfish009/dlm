# Release 0.0199 — axiom graph CSE (candidate)

- Date: 2026-11-10
- Predecessor: 0.0198. Candidate, not promoted.
- Scope: merge duplicate atomic axiom nodes and rewrite dependency edges.
- Analysis: `/research/analysis-axiom-cse-0199.md`.

## Changes

`src/dlm/axiom-graph.l`:

```text
ag-key
ag-cse-maps
ag-rewrite-id / ag-rewrite-deps
ag-cse
```

## Experiment

```text
BEFORE 3 AFTER 2 check=ok deps=(A-0)
SEL (A-0 A-1)
done-axiom-cse
```

A duplicate seed axiom `D` is merged into `A-0`; `A-1` keeps dependency `A-0`.
The minimal selector still chooses `A-0 + A-1`.

## Self-host

```text
compiler.sh reproduce
→ 20261110T110341Z-16726
compiler.sh verify 20261110T110341Z-16726
→ Verified
```

## Measured

```text
native normal   65 checks / 0 FAIL
native safety-2 65 checks / 0 FAIL
self-host       verified
```

## Still not

- no SCC/group pass
- no cost/MDL attributes
- activation lifecycle not integrated
- graph is MLIR-shaped, not upstream MLIR
- truth remains with the proof checker
