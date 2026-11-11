# Release 0.0155 — body value index for goal-directed proof (candidate)

- Date: 2026-11-08
- Predecessor: 0.0154. Candidate, not promoted.
- Scope: when a rule body atom is non-ground, use its bound argument value to
  fetch candidates instead of scanning every fact of the predicate.
- Analysis: `/research/analysis-body-index-0155.md`.

## Changes

`src/dlm/d107-prove.l`:

- non-ground body atoms use `p107-index-lookup-atom` with the current
  substitution;
- full-predicate scan remains available as a control via
  `*p107-prove-force-body-scan*`;
- `*p107-prove-body-candidates*` counts candidates examined.

## Experiment

`experiments/body_index/`: query `ancestor(a,c)` with N unrelated parent facts
placed before the useful facts; compare bound-value candidates with a full
predicate scan.

| unrelated parent facts | indexed candidates | full predicate scan | status | same answer |
|---:|---:|---:|---|---|
| 0 | 1 | 1 | answer107 | true |
| 10 | 1 | 11 | answer107 | true |
| 50 | 1 | 51 | answer107 | true |
| 100 | 1 | 101 | answer107 | true |

The bound value `x=a` selects only the relevant parent candidate; full scan grows
with the number of unrelated parent facts.

## Measured

```text
native normal   377 ok / 0 FAIL
native safety-2 377 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Only the first bound argument selects a bucket.
- No multi-position selectivity/ordering.
- Non-ground body candidates are extensional facts, not derived relations.
- Ground goals and conservative eligible rules only.
- No persistent value index.

## Recursive schema curriculum (experiment)

See `experiments/recursive_selfsup/`.

Round 1: recursive reachability schema → manages/reaches: A 6/6.
Round 2: unsolved hop1+hop2 target shape → second composition schema:
B 0/2 → 2/2, A remains 6/6.

Controls: `a-only` B 0/2; `frozen` A/B 0; `random-b` B 0/2.
This is a failure-triggered curriculum, not label-free self-supervision.
