# Release 0.0150 — negative dependency cache (candidate)

- Date: 2026-11-08
- Predecessor: 0.0149. Candidate, not promoted.
- Scope: cache a failed ground proof while no predicate touched by the search
  changes; unrelated observations do not invalidate it.
- Analysis: `/research/analysis-negative-cache-0150.md`.

## Changes

`src/dlm/d107-prove.l`:

- proof search records touched predicates;
- a negative cache entry stores `(predicate, facts digest)` for those predicates;
- a hit requires every touched-predicate digest to match;
- a new fact of an unrelated predicate does not invalidate;
- a new fact of a touched predicate does invalidate;
- negative caching is enabled only for the conservative positive eligible rule
  shape.

## Experiment

`experiments/negative_cache/`: 20 false `ancestor(c,a)` queries; each adds an
unrelated `noise` fact; then one live `parent(c,a)` fact is added.

| mode | total probes | first query | hits | misses | false status | after live fact |
|---|---:|---:|---:|---:|---|---|
| whole-state negative | 80 | 4 | 0 | 2 | no107 | answer107 |
| touched-predicate negative | 4 | 4 | 19 | 2 | no107 | answer107 |

The final live parent fact invalidates the negative entry and the query becomes
answer107 in both modes.

## Measured

```text
native normal   364 ok / 0 FAIL
native safety-2 364 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Ground atomic goals and conservative positive rules only.
- Touched-predicate granularity; unrelated values of the same predicate
  invalidate conservatively.
- In-memory only; bounded 32 entries.
- No per-rule/per-constant dependency graph.
- No alternative cheaper proof selection.
