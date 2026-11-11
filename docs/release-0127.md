# Release 0.0127 — bounded four-atom unit composition and residual frontier

- Date: 2026-11-08
- Predecessor: 0.0126. Candidate, not promoted.
- Scope: the analysis's step-1 minimum. Fixed E; bounded conservative unit
  composition; read-only residual frontier. No numeric EML, no new facts.

## What is new

### 1. Learned unit as the constructor of the next unit

- 0.0126 composed `2-atom unit + atom -> 3-atom unit`.
- 0.0127 adds `3-atom unit + atom -> 4-atom unit`:
  - indexed quads (`p107-index-quads`),
  - `p107-patterns4-from`,
  - active 3-atom views (`p107-views3`),
  - `p107-4-decomposition`, `p107-admit4`, `p107-try4`.
- The default learner order is four → three → two. Existing 3-fact demo data
  still stops at b1/b2; a 4-fact fixture learns b3 and b3 calls b2.
- Boundary: 4 atoms and 6 pattern variables. Deeper unit-DAG compositions need
  another grammar extension after this contract is verified.

### 2. Explicit ports and dependency body keys

```text
p107-def-ports      ordered VARS of the unit
p107-def-body-key   injective key of the exact body
p107-def-deps       (dep CALLEE exact-body-key) for every call step
```

This is a data-level interface/dependency record, not a new stored schema.

### 3. Read-only residual frontier

`(dlm 'residual)` returns:

```text
(residual107 grammar 4
  inactive ((UNIT SUPPORT) ...)
  max-record-facts N
  last-search complete|REASON
  last-proposal FEATURES|())
```

It reports inactive units, the grammar ceiling, record size and the last search
state. It does not mutate observations, basis, policy, or create goals.

### 4. Proposal purity / commit ordering

- `p107-learn` no longer updates routing weights while proposing.
- It stores `*p107-last-proposal*`; the weights change only after a successful
  durable `def107` transition **and** publish:
  - `p107-step-once` after publish,
  - `(dlm 'learn)` after publish.
- Rejected event-limit/checkpoint transitions leave route updates at 0.

### 5. Incomplete resident ticks wait, not halt

An `incomplete107` search is normalized to the `unknown` tick class:
mode `waiting`, idle task unregistered, and new evidence reactivates it.
It is no longer `halted incomplete`.

## Measured

```text
4-fact records:
  b1 (2 atoms) -> b2 (3 atoms) -> b3 (4 atoms, calls b2)
  b3 ports ordered, dependency names b2's exact body key
  b3 plan = 2 steps; raw/planned answers identical
  residual grammar=4; after retraction inactive includes b1/b2/b3 at support 1
3-fact demo:
  b1 -> b2 -> waiting (no 4-atom candidate)
```

```text
native normal      279 ok / 0 FAIL
native safety-2    279 ok / 0 FAIL
Python             16 tests OK
contract oracle    256/256 PASS
```

## Still open

- Deeper than 4 atoms; full typed schema/pipeline.
- Scope/evidence-conditioned applicability.
- F6/F7 exact budget and memoized shared DAG.
- No numeric EML/confidence/RMSE/LS/Adam/Python facade.
- The residual frontier is report-only; it is not yet a self-generated goal
  scheduler.
