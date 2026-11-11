# Release 0.0151 — constant-aware negative cache (candidate)

- Date: 2026-11-08
- Predecessor: 0.0150. Candidate, not promoted.
- Scope: refine the negative cache from touched predicates to touched constants,
  so an unrelated value of the same predicate does not invalidate a failed proof.
- Analysis: `/research/analysis-constant-cache-0151.md`.

## Changes

`src/dlm/d107-prove.l`:

- proof search records touched **constants** as well as predicates;
- a negative cache entry stores:
  ```text
  (touched-constants, ((predicate, filtered-facts-digest) ...))
  ```
- filtered digest uses only facts containing a touched constant;
- an unrelated value of a touched predicate therefore leaves the entry live;
- a fact containing a touched constant invalidates it.

## Experiment

`experiments/constant_cache/`: 20 false `ancestor(c,a)` queries; each adds an
unrelated `parent(pxN,pyN)` fact; then one relevant `parent(c,a)`.

| mode | total probes | first query | hits | misses | false status | after relevant fact |
|---|---:|---:|---:|---:|---|---|
| touched-predicate | 290 | 5 | 0 | 2 | no107 | answer107 |
| touched-constant | 5 | 5 | 19 | 2 | no107 | answer107 |

The constant-aware cache keeps the failure across unrelated values of the same
predicate and invalidates on `parent(c,a)`.

## Measured

```text
native normal   366 ok / 0 FAIL
native safety-2 366 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Ground atomic goals and conservative positive rules only.
- Constant-level granularity; a new fact sharing an irrelevant touched constant
  still invalidates conservatively.
- In-memory only; 32 entries.
- No per-rule/per-position dependency graph.
- No alternative cheaper proof selection or persistent store.
