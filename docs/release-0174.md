# Release 0.0174 — goal-directed proof with rule index (candidate)

- Date: 2026-11-08
- Predecessor: 0.0173. Candidate, not promoted.
- Scope: add a ground goal-directed prover that expands only matching rule heads
  and relevant facts, with rule-head indexing, per-query memoization, bounded
  probes, and a proof-tree checker.
- Analysis: `/research/analysis-goal-proof-0174.md`.

## Changes

`src/dlm/proof.l`:

- `p-prove` — reset budget/table and prove a ground goal
- `p-sld` — a single recursive function with `goal`/`body` modes (avoids
  forward references in Maru)
- `p-build-rule-index`, `p-rule-candidates`, `p-index-put` — rule-head
  predicate/arity index
- `p-goal-table`, `p-goal-active` — per-query memoization and cycle rejection
- `p-proof-check` — iterative pending-stack certificate checker
- `*p-prove-probes*`, `*p-rule-scans*` — cost counters

`experiments/goal_proof_repl/` + `scripts/goal_proof.sh`.

## Experiment

Independent parent chains; query only chain 0:

```text
N=1  closure=42  prove=13 scans=7 status=proof
N=5  closure=162 prove=13 scans=7 status=proof
N=20 closure=612 prove=13 scans=7 status=proof
CHECK1 ok
CHECK20 ok
done-goal-proof
```

Closure probes grow with unrelated chains; goal-directed probes and rule scans
stay constant. The proof certificate is checked against facts and rule indices.

## Self-host

```text
compiler.sh reproduce
→ 20261109T094355Z-22050
compiler.sh verify 20261109T094355Z-22050
→ Verified
```

## Measured

```text
native normal   40 checks / 0 FAIL
native safety-2 40 checks / 0 FAIL
self-host       verified
```

## Still not

- Ground goals only.
- Non-ground recursive body atoms fall back to extensional facts only.
- Per-query memoization, not a persistent dependency-aware proof cache.
- No negation, aggregation, or cost-based choice between closure and proof.
- Rule index is rebuilt per query.
