# DLM 0.0092 — native declarative deductive control

CPU-only Maru experiment copied from0091; predecessor directories are preserved.
No GPU, PyTorch, neural gradient training, LLM/API service, network acquisition,
or compiler/runtime change. Python is a development harness and finite oracle,
**not the policy or inference engine**.

This version implements **goal/binding-dependent selection of facts and logical
operators → actual scoped execution → independent admission → workspace reuse →
restore/widen**. It borrows the declaration/state-machine idea reviewed in
`declarative-attention`, not its neural attention implementation.

**This is application control over a frozen Basis91 core, not a learned attention
policy, a new world-axiom learner, or proof of a latent-axiom theory.** Existing
Basis91 formation and legacy APIs remain unchanged.

## Run

```sh
./scripts/run.sh attention92
./scripts/run.sh attention92-input < experiments/attention92/input-example.sexp
./scripts/run.sh proof experiments/attention92/interventions.l

python3 -B -m unittest discover -s tests -p 'test_attention92.py' -v
python3 -B tests/run_offline.py
python3 -B adapters/attention92_experiment.py --output /tmp/attention92.json
```

## What actually changes?

The demo first uses0091's data-led formation to obtain `B1=r-s`, then `B2=B1-t`.
The new controller receives the resulting executable core, **not training answer
rows or the training audit**. A query supplies a logical question, not a desired
basis body, answer label, or routing program.

For the same `r(x,y) ∧ s(y,z) ∧ t(z,w)` goal:

- On balanced training facts, `adaptive92` chooses B2 and actually dispatches B1.
- On the selective-tail source, it chooses **t → s → r**, passing verified variable
  bindings into later choices. Focuses contain original fact IDs **7 →4 →0**.
- Its active query plan is executed, not merely recorded as metadata.
- Selecting B2 automatically includes its B1 dependency.
- A deliberately incomplete focus leaves the result pending, then widens and
  retries. Partial absence is not a global negative.

The learned core itself is frozen during a query. This stage does not yet feed
control choices back into basis formation, retire definitions, or learn its cost
policy from experience.

## Native API

```lisp
(require "experiments/attention92/setup.l")
(define model92 (basis91 'model))

;; Pure fresh inference; does not modify the current learner or control session.
(attention92 'query model92 'dense
  '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)

;; Resumable control session over an explicit immutable model context.
(attention92 'start model92 'dense
  '((r 0 1) (s 1 2) (t 2 3)) 'adaptive92 200000)
(attention92 'proposal)   ; inspect concrete next focus, read-only
(attention92 'tick)       ; native policy/next transition
(attention92 'run 2)      ; bounded transitions, can return pending
(attention92 'status)
(attention92 'result)     ; no answer rows until complete
(attention92 'snapshot)
(attention92 'run 64)
```

Additional commands: `step COMMAND`, `state`, `restore SNAPSHOT`, `reset`,
`open PATH`, `save`, `close`. `restore` and `start/reset` require detachment.
The protocol uses typed data, not generated HTML or execution of supplied text.

```lisp
(focus92 EPISODE SOURCE-VERSION BASIS-EPOCH FACT-IDS REQUESTED-BASIS-IDS OP)
(apply92)
(local92)
(restore92)
(widen92)
(global92)
```

`local92` independently checks and commits a prepared binding workspace. It is
not a general local theorem language: the worker's AND composition uses these
bindings on subsequent scoped applications. The verifier may inspect the full
source; a visibility restriction is **not** a restriction on proof checking or a
change to authorized premises.

Models are explicit immutable snapshots. To use a changed/retracted corpus,
start from a newly exported current model. An explicitly retained old model
supports historical inference; it is **not an automatic revocation service**.

## Policies and controls

| Arm | Purpose |
|---|---|
| `raw`, `memo`, `basis` | Unmodified0091 executors; complete tables shared within an immutable episode/batch in measurement; memo includes structural caching |
| `ordered92` | New backend/checker, fixed minimum-op cover, all facts visible |
| `indexed92` | Same backend/checker and fixed cover, indexed binding-aware focus |
| `adaptive92` | Also selects next primitive/basis operator using goal and current bindings |
| `narrow92` | Explicit failure stress: truncate selected focus to its first ID, then recover via checked widening |

All four92 policies use the same worker and verifier. The marginal-count cost
heuristic is hand-designed, not trained, not optimal, and never a truth criterion.

## Verification

Final [offline run](docs/attention92-evidence/offline-tests.log): **186 tests passed
in588.770s**, including **26 new attention tests**. Six legacy local-HTTP tests
are excluded; the runner guards Python sockets, not an OS network sandbox.
Native, store, embedded-runtime and graph-store suites also passed.

New independent finite oracle: **256 two-node/two-relation graphs ×8 patterns
×4 policies =8,192 complete answer/witness checks**, zero mismatches. Additional
coverage includes a343-row workspace, wrong/omitted worker answers, unknown and
conflicting IDs/roles, poisoned indexes, partial focus, source-version changes,
nested restoration, budget exhaustion, malformed trees, replay forgery,
checkpoint failure and two-process locking.

## Experiment: useful routing, no end-to-end speedup

[Measurement](docs/attention92-experiment.json): **210 fresh native processes**
(5 workloads ×3 seeds ×7 arms ×2 repeats), **3,360 final-batch answer/witness
checks**, zero mismatches. Every process pays the same formation phases. Seeds
shuffle/rename fixed cases; they are not independent broad task distributions.

Selective-tail heldout chain, same new backend:

| Metric | ordered92 | adaptive92 |
|---|---:|---:|
| Worker fact reads | 64 | 3 |
| Independent checker units | 78 | 70 |
| Control actions | 5 | 13 |

These worker reads **exclude index construction, selection and checker access**.
They do not mean total data access or execution time fell by64/3.

Median whole-process seconds, including startup, formation, two query batches,
checking and serialization; no attached checkpoint:

| Workload | memo | ordered92 | adaptive92 |
|---|---:|---:|---:|
| chain | 0.9537 | 1.3978 | 1.3673 |
| selective-tail | 0.9712 | 1.5014 | 1.5278 |
| fork | 0.7656 | 1.2056 | 1.2190 |
| ambiguous | 2.0295 | 2.5775 | 2.6564 |
| no-repeat | 0.7444 | 1.1200 | 1.1223 |

**The new adaptive path is slower than memo on all five measured workloads.**
Fixed indexed control can also beat the adaptive heuristic. Whole-process timings
are not isolated steady-state kernel measurements and show no general speedup.

The frozen model size is identical across arms. Adaptive peak serialized
per-query control profiles add about1,639–2,345 bytes (workload medians), separate
from learned parameters, training evidence and audit. These are not heap sizes.
`metrics91` and `metrics92` have different units; do not compare their fuel totals.

## Scope and limits

Inherited grammar/bounds remain: positive connected binary conjunctions, ≤3 atoms,
≤4 variable roles, ≤8 facts/8 nodes per episode, ≤4 episodes, ≤8 prefix bases.
New control bounds: stack depth4,64 accepted transitions, ≤512 workspace rows,
logical fuel0..200000. No arbitrary FOL, negation, implicit inequality, projection
of witnesses, or universal world-law induction.

The implementation intentionally checks each local result with an independent
full-source primitive replay. Selection, list allocation/walks, model preflight
and serialization are not fully charged to logical fuel. No wall-time bound,
formal global completeness theorem, cryptographic authentication, or fsync-based
power-loss guarantee is claimed.

## Files

- [Design and contracts](docs/attention92-design.md)
- [Release and evidence](docs/release-0092.md)
- [Compact interventions](docs/attention92-interventions.sexp)
- [Full demo trace](docs/attention92-demo.sexp)
- [Input demo](docs/attention92-input-demo.sexp)
- [Previous0091 README](README-0091.md), [0090](README-0090.md), [legacy](README-legacy88.md)

`basis91`, `basis90`, `dlm`, `space`, and `contracts` remain separate APIs. The
compiler and all inherited logical implementation modules are unchanged.
