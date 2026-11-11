# Release 0.0144 — indexed closure for the public inference path (candidate)

- Date: 2026-11-08
- Predecessor: 0.0143. Candidate, not promoted.
- Scope: execute the same rule closure with predicate/argument indexes instead of
  scanning every fact for every body literal.
- Analysis: `/research/analysis-indexed-closure-0144.md`.

## Changes

- `src/dlm/d107-index.l` adds:
  - `p107-solve-pos-idx`
  - `p107-solve-idx`
  - `p107-child-ids-idx`
  - `p107-derive-pass-idx`
  - `p107-close-indexed`
  - `p107-closure-fast`
- The public `p107-query`, `p107-answer`, and `p107-answer-evidenced` paths now
  use `p107-closure-fast`.
- `p107-close` remains the exhaustive reference implementation.
- `*p107-close-probes*` counts candidate checks for differential comparison.

The indexed path still uses the same rule/proof representation and the same
proof IDs/order for the tested programs.

## Experiment

`experiments/indexed_closure/` compares exhaustive and indexed closure with
0, 8, 32 and 128 irrelevant `noise` facts.

| noise facts | exhaustive probes | indexed probes | reduction | rows | equal |
|---:|---:|---:|---:|---:|---|
| 0 | 1064 | 154 | 85.5% | 27 | true |
| 8 | 1512 | 154 | 89.8% | 35 | true |
| 32 | 2856 | 154 | 94.6% | 59 | true |
| 128 | 8232 | 154 | 98.1% | 155 | true |

The exhaustive scan grows with irrelevant facts; the indexed path remains
constant because parent/ancestor buckets do not contain noise facts.

## Measured

```text
native normal   349 ok / 0 FAIL
native safety-2 349 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Index is rebuilt each closure pass; no incremental index.
- No goal-directed proof: the whole relevant closure is still computed.
- No closure/proof cache or semi-naive delta evaluation.
- No cost-based join order; the first bound argument chooses the bucket.
- No change to rule/definition language or evidence semantics.
