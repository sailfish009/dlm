# Release 0.0154 — rule-head index for goal-directed proof (candidate)

- Date: 2026-11-08
- Predecessor: 0.0153. Candidate, not promoted.
- Scope: index rules by head predicate/arity so a ground goal only scans rules
  that can match it.
- Analysis: `/research/analysis-rule-index-0154.md`.

## Changes

`src/dlm/d107-prove.l`:

- `p107-prove-rule-index-build`
- `p107-prove-rule-candidates`
- `p107-prove-rule-loop` iterates only candidates for the goal head;
- original rule indices are retained for proof terms;
- `*p107-prove-rule-scans*` counts rule candidates considered;
- `*p107-prove-force-scan*` provides the full-scan control.

## Experiment

`experiments/rule_index/`: query `ancestor(a,c)` with N unrelated `fooN` rules
whose bodies are parent facts.

| extra rules | indexed scans | full scans | status | same answer |
|---:|---:|---:|---|---|
| 0 | 3 | 5 | answer107 | true |
| 10 | 3 | 15 | answer107 | true |
| 50 | 3 | 55 | answer107 | true |
| 100 | 3 | 105 | answer107 | true |

The indexed path scans only ancestor rules; full scan grows with unrelated rules.

## Measured

```text
native normal   375 ok / 0 FAIL
native safety-2 375 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Rule index is rebuilt per proof.
- Head predicate/arity only; no body/selectivity index.
- Ground goals and conservative eligible rules only.
- Proof cache and axiom lifecycle remain separate.
- No persistent rule index.
