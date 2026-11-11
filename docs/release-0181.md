# Release 0.0181 — constraint-guided graph selection (candidate)

- Date: 2026-11-08
- Predecessor: 0.0180. Candidate, not promoted.
- Scope: use hard constraints to filter candidate graphs and soft constraints to
  rank the remaining candidates; the selected graph's run result is unchanged.
- Analysis: `/research/analysis-graph-select-0181.md`.

## Changes

`src/dlm/graph-ir.l`:

```text
mg-soft-score       count active soft constraints that evaluate true
mg-candidate        ID + constrained graph
mg-select-candidates filter hard-valid, maximize soft score
```

`experiments/graph_select_repl/` + `scripts/graph_select.sh`.

## Experiment

```text
SOFT base=0 extra=1
SELECTED extra
RUN (summary tasks 1 solved 1 active (p))
done-select
```

- both candidates pass hard constraints
- extra graph satisfies one soft constraint
- base graph satisfies none
- selector chooses extra
- selected graph run summary is normal

A hard-invalid candidate is filtered out before ranking.

## Self-host

```text
compiler.sh reproduce
→ 20261109T121306Z-22772
compiler.sh verify 20261109T121306Z-22772
→ Verified
```

## Measured

```text
native normal   51 checks / 0 FAIL
native safety-2 51 checks / 0 FAIL
self-host       verified
```

## Implementation note

The selected candidate stores a **constrained** graph. Lowering therefore uses
`(mg-cgraph-graph cg)`, not the constrained wrapper itself. Passing the wrapper
directly produced an empty module and a zero-task run.

## Still not

- Soft constraints are counts, not a weighted cost model.
- Candidate generation is still manual.
- No embedding/soft score combination yet.
- No proof-level selection; truth remains with the proof checker.
- No CSE/fusion/canonicalization yet.
