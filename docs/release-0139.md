# Release 0.0139 — recursive Horn rule induction attempt (candidate)

- Date: 2026-11-08
- Predecessor: 0.0138. Candidate, not promoted.
- Scope: extend one-rule composition induction to a two-rule recursive program
  and test held-out length-2/length-3 closure.
- Analysis: `/research/analysis-recursive-rule-0139.md`.

## Implementation

`src/dlm/d107-rulelearn.l` now also supports:

```text
seed:       target(x,z) :- p(x,z)
recursive:  target(x,z) :- p(x,y), target(y,z)
```

- `p107-rulelearn-recursive` first learns a seed rule from observed target
  positives (FP=0).
- It then evaluates recursive candidates with the seed installed.
- A recursive rule is accepted only if it increases TP with FP=0.
- It returns `(learned107 (SEED RECURSIVE) BASE-TP TP FP CANDIDATES)`.

## Experiment

`experiments/recursive_rule/`:

```text
target: ancestor(x,z)
train:  parent chains of length 3 + all ancestor positives
held:   3 new chains of length 3, parent edges only, no ancestor labels
queries: direct, length-2, length-3 ancestor positives; 5 negatives
```

| arm | held positives | held negatives clean | notes |
|---|---:|---:|---|
| learned recursive | 9/9 | 5/5 | seed + recursive rule |
| seed only | 3/9 | 5/5 | direct ancestors only |
| single composition | 3/9 | 5/5 | length-2 only |
| frozen | 0/9 | 5/5 | no rules |
| oracle | 9/9 | 5/5 | true recursive program |
| random/reverse | 0/9 | 4/5 | one false positive |

The non-recursive composition (`parent(x,y), parent(y,z)`) cannot answer the
length-3 held-out queries. The recursive program can.

## Measured

```text
native normal   332 ok / 0 FAIL
native safety-2 332 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Synthetic binary relation, observed target positives, finite entities.
- Candidate generation is from observed fact pairs, not a proof-failure
  frontier/structural credit.
- No negation, arity >2, multi-relation recursion or schema held-out.
- 0.0137's all-witness grounding and derived-evidence traversal remain
  unfixed in this candidate.
- No live web or autonomous curriculum in this task.
