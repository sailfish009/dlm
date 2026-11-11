# Release 0.0149 — dependency-aware proof cache (candidate)

- Date: 2026-11-08
- Predecessor: 0.0148. Candidate, not promoted.
- Scope: keep a cached ground proof valid across unrelated observation changes by
  checking only the given facts actually used by that proof.
- Analysis: `/research/analysis-dependency-cache-0149.md`.

## Changes

`src/dlm/d107-prove.l`:

- The proof cache key no longer includes the whole facts digest.
- Each entry stores the proof's used given facts `(FID ATOM)`.
- A hit is returned only while every used given fact is still live with the same
  atom.
- Retracting a used fact invalidates the entry; adding an unrelated fact does not.
- Negative/no-answer results are not cached in this version.

## Experiment

`experiments/dependency_cache/`: 20 iterations; each adds an unrelated `noise`
fact before the same public ground query.

| mode | total probes | first query | hits | misses | status |
|---|---:|---:|---:|---:|---|
| whole-state cache | 80 | 4 | 0 | 1 | answer107 |
| dependency-aware | 4 | 4 | 19 | 1 | answer107 |

The dependency-aware path keeps the proof live across all 19 unrelated changes.

## Measured

```text
native normal   362 ok / 0 FAIL
native safety-2 362 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Ground atomic goals only.
- In-memory only; bounded 32 entries.
- Positive answers only; no-answer results are not cached.
- Used-given check is ID+atom; no per-rule/per-predicate dependency graph.
- A new fact that could provide a cheaper alternative proof does not invalidate
  the cached proof.
- No persistent proof store.
