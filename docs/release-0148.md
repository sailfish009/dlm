# Release 0.0148 — goal-proof cache (candidate)

- Date: 2026-11-08
- Predecessor: 0.0147. Candidate, not promoted.
- Scope: cache a ground goal-directed proof by scope, goal, exact facts digest,
  rules identity and budget.
- Analysis: `/research/analysis-proof-cache-0148.md`.

## Changes

`src/dlm/d107-prove.l`:

- `*p107-prove-cache*` — bounded 32-entry in-memory cache.
- key:
  ```text
  (scope, goal, facts digest, rules identity, budget)
  ```
- `p107-prove-cache-reset`, hit/miss counters.
- `p107-prove-ground` returns the cached answer/no-answer on a hit.
- Any observation/retraction, rule change, scope or budget change invalidates
  by key.

The cached object is the already proof-checked answer; no approximation is used.

## Experiment

`experiments/proof_cache/`: 20 repeated public ground queries through
`p107-query`, cold closure cache, one process per mode.

| mode | total probes | first query | hits | misses | status |
|---|---:|---:|---:|---:|---|
| no proof cache | 260 | 13 | 0 | 1 | answer107 |
| proof cache | 13 | 13 | 19 | 1 | answer107 |

The cache hit path performs zero proof probes.

## Measured

```text
native normal   360 ok / 0 FAIL
native safety-2 360 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Ground atomic goals only.
- In-memory only; no cross-process persistence.
- 32-entry bounded cache, no cost-aware eviction.
- Goal proof cache does not populate the closure cache.
- No non-ground/derived body extension or negation.
- Invalidation is whole-key based; no per-predicate dependency tracking.
