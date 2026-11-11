# Release 0.0138 — checked Horn rule induction attempt (candidate)

- Date: 2026-11-08
- Predecessor: 0.0137. Candidate, not promoted.
- Scope: test whether a new universal Horn rule can be induced from observed
  positives and improve held-out answers, unlike conservative definitions.
- Analysis: `/research/analysis-rule-composition-0138.md`.

## Why this attempt

0.0137 controls showed that the reported 42 -> 22 plan-step reduction is fully
explained by join-order selection. Conservative definitions abbreviate existing
patterns and do not add consequences. The missing learning step is therefore not
more definition compression: it is **rule invention**.

## Implementation

New `src/dlm/d107-rulelearn.l`:

- Candidate rules are witnessed by two observed binary facts sharing a middle
  constant:
  ```text
  p(a,b), q(b,c)  ->  target(x,z) :- p(x,y), q(y,z)
  ```
- The target predicate is removed from the evaluation base.
- `p107-close` evaluates each candidate.
- A candidate is accepted only when:
  - it derives at least one observed target positive;
  - it derives **zero** target atoms outside the observed positives.
- The learner returns `(learned107 RULE TP FP CANDIDATES)` and installs nothing;
  the caller decides whether to add the rule to `*p107-rules*`.

## Experiment

`experiments/rule_composition/`:

```text
target: grandparent(x,z) :- parent(x,y), parent(y,z)
train:  3 chains with parent edges + grandparent positives
held:   3 new chains with parent edges only, no held target labels
neg:    4 held pairs that must not be derived
```

| arm | held positives | held negatives clean | notes |
|---|---:|---:|---|
| learned | 3/3 | 4/4 | rule learned with TP=3 FP=0 |
| frozen | 0/3 | 4/4 | no rule |
| oracle | 3/3 | 4/4 | true rule supplied |
| random | 0/3 | 4/4 | wrong composition |
| definition | 0/3 | 4/4 | 4 conservative definitions; no new facts |
| scrambled | 0/3 | 4/4 | corrupted target labels; learner returns none |

The definition arm is the key control: 0.0137-style conservative definitions do
not solve the held-out composition.

## Measured

```text
native normal   328 ok / 0 FAIL
native safety-2 328 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- One synthetic binary-composition target, hand-designed predicates.
- Target positives are observed labels; the learner is not yet driven by a
  proof-failure frontier or structural credit.
- No multi-rule search, recursion, negation, arity >2 or schema held-out.
- Derived-fact evidence chains and the all-witness grounding bug from 0.0137
  remain separate; this release does not fix them.
- No live web or autonomous source/goal selection in this task.
