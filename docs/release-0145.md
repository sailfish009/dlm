# Release 0.0145 — closure cache for repeated inference (candidate)

- Date: 2026-11-08
- Predecessor: 0.0144. Candidate, not promoted.
- Scope: reuse an identical closure table when scope facts, rules and budget have
  not changed.
- Analysis: `/research/analysis-closure-cache-0145.md`.

## Changes

`src/dlm/d107-index.l`:

- `*p107-closure-cache*` — bounded in-memory cache (32 entries).
- cache key:
  ```text
  (scope, exact facts digest, exact rules identity, budget)
  ```
- `p107-closure-fast` returns a cached value on hit.
- Any observation/retraction or rule change produces a different key.
- `p107-closure-cache-reset`, hit/miss counters added.

The cached value is the same closure table/proof structure used by the indexed
path; no reduction or approximation is applied.

## Experiment

`experiments/closure_cache/`:

```text
128 noise facts, parent/ancestor recursive rules
20 repeated identical closures
one process per mode
```

| mode | total probes | first closure | hits | misses | rows |
|---|---:|---:|---:|---:|---:|
| no cache | 3080 | 154 | 0 | 20 | 155 |
| cache | 154 | 154 | 19 | 1 | 155 |

The cache path performs candidate probes only on the first closure. Repeated
queries reuse the same closure table.

## Measured

```text
native normal   352 ok / 0 FAIL
native safety-2 352 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Cache is in-memory only; no persistence across processes.
- Whole-closure cache, not partial/incremental truth maintenance.
- No goal-directed proof; a cache miss still computes the whole relevant closure.
- No semi-naive delta evaluation.
- Cache invalidation is whole-key based; no per-predicate dependency tracking.
- 32-entry eviction is FIFO-ish by insertion, not cost-aware.
