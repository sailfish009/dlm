# Release 0.0177 — hard/soft constraints on explicit graph (candidate)

- Date: 2026-11-08
- Predecessor: 0.0176. Candidate, not promoted.
- Scope: attach logical constraints to the explicit graph; hard false rejects the
  graph, soft false is report-only.
- Analysis: `/research/analysis-graph-constraints-0177.md`.

## Changes

`src/dlm/graph-ir.l`:

```text
mc-constraint ID KIND EXPR SCOPE STATUS PROV
mg-attach       graph + constraints → constrained graph
mg-check-cgraph graph check + hard constraints
mg-constraint-report
mc-eval         and/or/not, node-exists, node-kind, edge-exists, acyclic
```

Kinds:

```text
hard        → false/bad rejects
soft        → false is report-only
structural  → reserved, currently report-only
```

`experiments/constraint_graph_repl/` + `scripts/constraint_graph.sh`.

## Experiment

```text
HARD ok
REPORT ((c-node hard active true)
        (c-kind hard active true)
        (c-not hard active true)
        (c-acyclic hard active true)
        (c-soft soft active false))
BAD (rejected107 mg-constraint c-missing)
BADEXPR (rejected107 mg-constraint-expr c-expr)
done-constraints
```

- four hard constraints true → accepted
- soft constraint false → report only, accepted
- missing-node hard constraint → rejected
- unknown expression → rejected as malformed

## Self-host

```text
compiler.sh reproduce
→ 20261109T112810Z-17962
compiler.sh verify 20261109T112810Z-17962
→ Verified
```

## Measured

```text
native normal   46 checks / 0 FAIL
native safety-2 46 checks / 0 FAIL
self-host       verified
```

## Implementation note

Constraint status must be the symbol `active`, not the string `"active"`.
The first run mixed them and the constrained graph was rejected as malformed.

## Still not

- Constraint expressions are a small fixed language; no quantifiers/arithmetic.
- No attachment to individual nodes/edges beyond scope metadata.
- Soft constraints are not yet used to rank candidates.
- No Z3/SMT backend; finite evaluator only.
- Constraint provenance is stored but not validated.
- Truth remains with the proof checker.
