# Release 0.0128 — exact budget and memoized proof-DAG foundation

- Date: 2026-11-08
- Predecessor: 0.0127. Candidate, not promoted.
- Input: `/research/analysis-screamer-dlm-execution.md` (F6/F7 prerequisite).
- Scope: repair the execution foundation before any continuation machine or
  macro DSL. No Screamer CPS/macro port in this release.

## F6 — budget N means exactly N steps

- `p107-spend` now checks `(>= steps budget)` **before** consuming a step.
- `p107-exec-atoms` does the same for join execution.
- A budget of N permits N steps, never N+1.

```text
budget=1 -> status unknown, rows=0, steps=1
budget=2 -> status complete, rows=1, steps=2
```

## F7 — memoized, cycle-safe proof DAG

`p107-validate-node` replaces the old worklist that re-expanded shared children.

- `verified` list: a shared child is checked once.
- `visiting` list: cycles are rejected.
- work counts distinct nodes, not expansions.
- `p107-proof-ok?` still uses the same `32 + 4*table` bound but now that bound is
  consumed by distinct nodes.

```text
10-fact shared DAG:
  closure complete
  query/answer/read accept the calls proof
  validator accepts the shared DAG
```

This closes the F7 prerequisite: valid shared proofs are no longer rejected
merely because the same child is reached through multiple parents.

## Why this order

The Screamer analysis recommends F6/F7 before an explicit execution machine.
The continuation-data machine needs:

- an exact budget context,
- memoized proof checking that distinguishes failure from work exhaustion,
- branch-local evidence/basis versions.

F6/F7 provide the budget and proof-validation base; 0.0128 does not yet add
`fork/bind/require/yield/suspend/resume/exhausted`.

## Measured

```text
native normal      282 ok / 0 FAIL
native safety-2    282 ok / 0 FAIL
Python             16 tests OK
contract oracle    256/256 PASS
```

## Still open

- Explicit inference execution machine (continuation as data, branch-local
  assumptions, wait/resume/exhausted) — next.
- Restricted `define-form` search DSL after that.
- Optional CSP propagation/MRV as a branch operator.
- `H ⊢ q` vs unconditional q, unknown vs fail, AND obligations, checked commit
  before reuse remain explicit design constraints.
- No numeric EML, no full Screamer port.
