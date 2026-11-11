# Release 0.0146 — ground goal-directed proof (candidate)

- Date: 2026-11-08
- Predecessor: 0.0145. Candidate, not promoted.
- Scope: prove a ground atomic goal by expanding only matching rule heads and
  body goals, with memoization and cycle rejection, instead of computing the
  whole closure.
- Analysis: `/research/analysis-goal-proof-0146.md`.

## Changes

New `src/dlm/d107-prove.l`:

- ground goal resolution with tabling;
- rule-head unification and body expansion;
- a temporary proof table for the existing `p107-proof-ok?` checker;
- cycle rejection and bounded depth;
- `p107-prove-probes` counter.

It is conservative: non-ground body atoms are resolved against extensional
facts; it does not claim completeness for arbitrary non-ground queries or
negation.

## Experiment

`experiments/goal_proof/`: independent parent chains; query the deep ancestor
of one chain. Full indexed closure vs goal-directed proof.

| chains | full closure probes | goal-directed probes | full facts | proof nodes | status |
|---:|---:|---:|---:|---:|---|
| 1 | 60 | 13 | 14 | 4 | answer107 |
| 5 | 300 | 13 | 70 | 4 | answer107 |
| 20 | 1200 | 13 | 280 | 4 | answer107 |

Goal-directed probes stay constant because only the queried chain is expanded;
full closure grows with the number of unrelated chains.

## Measured

```text
native normal   355 ok / 0 FAIL
native safety-2 355 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Ground atomic goals only.
- Non-ground body atoms use extensional facts, not all derived relations.
- No negation/aggregation in goal-directed proof.
- The public `p107-query` path is not switched yet; 0.0146 provides the prover.
- Temporary proof table is built per query; no proof cache.
- No parallel/backtracking cost policy.
