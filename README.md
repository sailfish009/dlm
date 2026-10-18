# DLM v0.0071 -- minimal learned controller / Maru interaction

Goal: demonstrate an execution-feedback loop before attempting natural-language
reading. Maru is the executor, not an LLM replacement with equivalent abilities.
The original Horn model and verified compiler lifecycle from 0070 remain available.

```sh
./scripts/run.sh interaction
./scripts/run.sh test
./scripts/run.sh repl
```

## Experiment

Input is a list and a goal value. The action IDs are head, tail and abstain.
Each action calls an actual Maru primitive through a bounded whitelist. A head
result ends the episode, checked by exact equality with the goal; tail returns
the next list state. No operation can return the goal argument itself.

A tiny sparse state/action linear ranker selects each operation. Integer pairwise
margin updates learn from successful execution traces found by bounded BFS. This
is expert iteration with execution-derived supervision, not gradient training,
LLM generation, learned Horn axioms or general natural-language understanding.

Features: bias, head equals goal, singleton list. In particular, head/goal equality
is a built-in observable affordance, not learned semantic understanding. There is
no goal-position feature. BFS and exact equality are trusted seed mechanisms.

The current model drives Maru action selection, receives execution state, and
updates action weights. Successful search trajectories train local state/action
contrasts. Search uses a fixed independent terminal checker, never the scorer's
own prediction as a truth label. Experience and weights are plain Lisp model data.

## Fixed protocol and measured results

- Training: all target positions in prefixes of (a b c d), lengths 1 through 4.
- 12 rounds over those 10 tasks; 480 teacher primitive calls, 3 margin updates.
- Held out: unseen values (u v w x y z s t), lengths 5 through 8, 26 tasks.
- Rollout budget per task: list length + 1 primitive calls for every arm.

| Arm | Successes / 26 | Actual rollout calls |
|---|---:|---:|
| Frozen zero-weight controller | 4 | 26 |
| Seeded random action policy | 3 | 43 |
| Learned controller | 26 | 100 |
| Learned controller with head/tail IDs swapped | 0 | 30 |

Teacher search cost is additional and reported separately. The learned arm is
more successful, NOT cheaper in actual calls than early-failing baselines.
This tiny deterministic task, explicit features and one random schedule are not
evidence for general intelligence or real-world generalization.

## Manual interaction

```lisp
(define model (interaction-model))
(set model (interaction-train model '(a b c) 'c 64))
(interaction-rollout model '(u v w) 'w 4 'learned 70)
```

For the full trained model, run the interaction experiment or train across all
provided tasks. One successful example alone need not generalize.

## Implementation

src/dlm/interaction.l: scorer, actual primitive execution, bounded trajectory
search, margin contrast, rollout and experience. experiments/interaction/run.l:
fixed train/held-out tasks and controls. tests/interaction-tests.l: nine checks.
Full suite: 22 previous model checks plus 9 interaction checks.

The interaction learner is separate from Ground/Experience in the Horn model:
its weight feedback cannot admit facts or rules. No compiler mutation, file/network
capability, persistence, web acquisition or arbitrary eval is exposed by its action
interface. This interface is not an OS sandbox for arbitrary Maru user programs.

## Compiler lifecycle (unchanged)

```sh
ID=$(./scripts/compiler.sh rebuild)    # external current source; initial Python assembly
# ID=$(./scripts/compiler.sh reproduce)  # embedded snapshot; no Python
./scripts/compiler.sh verify "$ID"
./scripts/compiler.sh promote "$ID"
./scripts/compiler.sh rollback
```

Compiler/runtime self-reproduction does not establish semantic correctness.
See docs and LICENSE.maru. DLM source licensing must be confirmed before publishing.
Optional development comparison: python tests/differential.py (sibling 0066 oracle).

Next stage: replace list operations with a small explicitly typed reader-action
space and fixed text corpus, preserving an independent validation boundary.
