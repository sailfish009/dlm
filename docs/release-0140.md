# Release 0.0140 — failure-triggered recursive rule induction (candidate)

- Date: 2026-11-08
- Predecessor: 0.0139. Candidate, not promoted.
- Scope: let a failed query choose the target predicate and learn a recursive
  program over partially labeled data, treating unlabeled entities as unknown
  rather than negative.
- Analysis: `/research/analysis-failure-rule-0140.md`.

## Changes

### Open-world target domain

`src/dlm/d107-rulelearn.l` now evaluates a candidate target atom only when its
arguments occur in the **observed target-positive domain**. An entity that has no
target label is unlabeled; its parent edges are not silently treated as negative
target examples.

### Failure-triggered learning

`p107-rulelearn-from-failure`:

- takes a failed ground goal, not a manually supplied target predicate;
- reads the target from the failed goal;
- runs the checked recursive learner;
- reports whether the same failed goal becomes derivable.

Result form:

```text
(failure-learned107 TARGET (SEED RECURSIVE) BASE-TP TP FP SOLVED)
(failure-none107 TARGET CANDIDATES)
```

## Experiment

`experiments/failure_rule/`:

```text
labeled chains A/B: parent edges + ancestor positives
unlabeled chain C:  parent edges only
held chains D/E/F:  parent edges only
failed goal:        ancestor(C_start, C_end)  (length 3)
```

| arm | before failed | after failed | held positives | held negatives clean |
|---|---:|---:|---:|---:|
| failure | 0 rows | 1 row | 9/9 | 5/5 |
| seed only | 0 | 0 | 3/9 | 5/5 |
| single composition | 0 | 0 | 3/9 | 5/5 |
| frozen | 0 | 0 | 0/9 | 5/5 |
| oracle | 0 | 1 | 9/9 | 5/5 |
| random/reverse | 0 | 0 | 0/9 | 4/5 |
| no-label | 0 | 0 | 0/9 | 5/5 |

The `no-label` arm has no target positives, so the learner abstains. The
`failure` arm learns from the labeled chains, treats C as unlabeled, resolves the
query that triggered learning, and generalizes to three new held chains.

## Measured

```text
native normal   336 ok / 0 FAIL
native safety-2 336 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Synthetic binary relation; target labels are still required on some chains.
- Candidate generation is triggered by failure but not selected by a proof-DAG
  credit/failure-frontier decomposition.
- No multi-relation recursion, mutual recursion, negation, arity>2, or schema
  held-out.
- 0.0137's all-witness grounding and derived-evidence traversal remain separate.
- No live web or autonomous curriculum in this task.
