# Release 0.0147 — public ground query uses goal-directed proof (candidate)

- Date: 2026-11-08
- Predecessor: 0.0146. Candidate, not promoted.
- Scope: connect the ground goal-directed prover to the public `p107-query`
  path when the closure cache is cold and the rules are in the conservative
  eligible shape.
- Analysis: `/research/analysis-public-goal-query-0147.md`.

## Changes

- `p107-closure-cache-hit?` exposes cache state without computing a closure.
- `p107-prove-eligible?` accepts only rules with:
  - no negation;
  - every positive body predicate extensional or the rule's own head.
- `p107-query`:
  - cached closure → use the cache;
  - cold cache + eligible rules → `p107-prove-ground`;
  - non-eligible/rejected → fall back to indexed closure.
- Ground query proof is still validated by `p107-proof-ok?`.

## Experiment

`experiments/public_goal_query/` uses independent parent chains and queries one
deep ancestor through the public `p107-query` after cache reset.

| chains | full closure probes | public query probes | status | closure cache |
|---:|---:|---:|---|---|
| 1 | 60 | 13 | answer107 | miss |
| 5 | 300 | 13 | answer107 | miss |
| 20 | 1200 | 13 | answer107 | miss |

The public query now expands only the queried chain on a cold cache.

## Measured

```text
native normal   357 ok / 0 FAIL
native safety-2 357 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Ground atomic goals only.
- Conservative eligibility shape; non-ground/negation queries fall back.
- Non-ground body atoms use extensional facts.
- The goal-directed path does not populate the closure cache.
- No proof cache; temporary proof table per query.
- No cost-based choice between cached closure and goal proof.
