# DLM 0.0090 — execution-basis experiment

Copied from the 0.0089 review workspace; previous directories are unchanged.
This is an **early experiment**, not a complete theory of latent axioms.

The new path discovers repeated factors in explicit relational workloads, checks
new basis definitions, **replaces active execution expressions**, and uses the
new basis in later tasks and the next discovery round. It does not merely append
proofs to a cache. No GPU, neural embedding, backpropagation, LLM service, HTTP or
MLIR/compiler change is required.

## Run

```sh
# Explicit synthetic two-round experiment; no network or persistent side effects.
./scripts/run.sh basis90

# File-based structured experiment, read as data rather than evaluated code.
./scripts/run.sh basis90-input < experiments/basis90/input-example.sexp

# Independent finite oracle plus exploratory four-arm CPU measurements.
python3 -B adapters/basis90_experiment.py --output /tmp/basis90.json

# Original native REPL with a separate (basis90 ...) API.
./scripts/run.sh repl
```

The two-round demo discovers `B1 = r∘s`, rewrites three execution plans, then
finds `B2 = B1∘t` after later tasks arrive. The public `rst` task becomes
`(use90 2)`, and later plans use the same basis. These bodies are discovered from
the task workload, not supplied as preverified solutions.

## Manual native API

In a fresh REPL:

```lisp
(require "experiments/basis90/setup.l") ; explicit source/task fixture, resets basis90
(basis90 'candidates)
(basis90 'learn)
(basis90 'status)
(basis90 'run 'train () 200000)         ; all registered tasks, active basis plans
(basis90 'run 'train () 200000 'raw)    ; original expression control
(basis90 'query 'train '(join90 (rel90 r) (rel90 s)) 200000)

; Attach the current experiment to a fresh path; commits checkpoint before publish.
(basis90 'open "/tmp/fresh-basis90.sexp")
(basis90 'save)
(basis90 'close)
```

In a fresh process, `(basis90 'open "/tmp/fresh-basis90.sexp")` restores the core,
checked definitions, transformed plans, task interface and audit. A different live
experiment is not silently replaced. Init is refused while a store is attached.

Additional commands:

```lisp
(basis90 'init '(r s t))
(basis90 'observe 'source-id '((atom r (a b)) (atom s (b c))))
(basis90 'task 'task-id '(join90 (rel90 r) (rel90 s)))
(basis90 'retract 'source-id)
(basis90 'proposal)
(basis90 'state)
(basis90 'snapshot)
```

Task IDs are immutable. Re-importing an existing ID is rejected without adding
feedback. `query` does not register a training task or mutate the model. Runtime
answer tables are local to one execution batch and one immutable episode.

## What is being learned?

Expressions are `(rel90 NAME)`, `(join90 LEFT RIGHT)` and checked `(use90 ID)`.
Meaning is Boolean binary relation composition, not empirical implication.
Discovery counts repeated adjacent factors in **current execution tokens**;
an existing `use90` is atomic, enabling a later basis to depend on it.

A separate gate checks acyclic prefix dependencies, exact primitive expansion,
all task rewrites, at least two uses of the new basis, and an actual reduction in
active work-expression nodes. The gate does not call the proposer, router or
executor. Equal primitive words establish the restricted relational identity by
associativity; finite graph tests are additional evidence, not its definition.

There is no automatic useful-goal invention, general natural-language extraction,
new world-axiom induction or trained multi-head attention. Symbolic eligibility,
competition and routing are the first attention-inspired decomposition. Candidate
scores are heuristics, never logical truth values. Learned bases retain prior
checked dependencies; global basis minimization/retirement is not implemented.

The executable core and justification audit occupy separate snapshot fields,
not yet separate content-addressed blob files. Original task expressions remain
as the public-to-internal mapping; their storage cost is not hidden.

## Controls and measurements

`raw`: original programs, no basis needed in the execution core.
`append`: basis is available, but programs are not rewritten.
`basis`: checked basis with rewritten execution plans.
`memo`: primitive programs with canonical structural memoization.

`append` is a deliberately limited experimental control, **not** a benchmark of
the entire legacy A77 learner. All measurement processes pay the same discovery
phases. CPU/wall/RSS includes startup, training/checking, queries and output;
checkpoint costs are not included in that particular measurement.

The demo's active work nodes change from 29 to 13 after two rounds, plus 6 basis-body
nodes. Pair comparisons in its final batch change from 48 (`raw`) to 24 (`basis`),
while the memo control performs 34. This is not proof of wall-time speedup.
Small workloads can have a larger core after basis introduction. Costs, no-repeat
cases and overlapping candidates are retained in `docs/basis90-experiment.json`.

## Retained legacy entry point

The earlier integrated relation/Boolean-contract learner is still available:

```sh
./scripts/recursive-selfssl.sh --demo --contracts-demo --rounds 12 --budget 4 /tmp/legacy90.sexp
```

Its `(dlm 'step/start)` curriculum is **not** silently switched to basis90.
See [the preserved legacy usage guide](README-legacy88.md) and
[Contracts88 design](docs/contracts88-design.md). The joint plain replay ordering
fix described below is the intentional compatibility change.

## Verification

```sh
./scripts/run.sh test
python3 -B tests/run_offline.py
python3 -B -m unittest discover -s tests -p 'test_basis90.py' -v
python3 -B -m unittest discover -s tests -p 'test_review90.py' -v
```

The offline runner excludes the six legacy local-HTTP tests and guards Python
socket calls. It is not an OS network sandbox. New transport regression uses a
seeded `--offline` cache without a server.

Basis tests include two-round formation/replacement, actual dispatch, independent
checking, forged rewrites/definitions/certificates, malformed input, saturation,
limits, source retraction, checkpoint rollback, external file changes, fresh
process next-step equality, and all 256 two-node/two-relation graphs against an
independent Python join oracle.

Separate inherited fixes: web input list-shape validation no longer segfaults;
joint plain relation replay uses canonical ordering rather than a live spatial
cache. Legacy plain routing remains available. `.gitignore` packaging rules are
restored. These fixes are not evidence for a new learning algorithm.

## Scope

Limits: 8 primitive relation names, 4 episodes, 24 facts/episode, 12 nodes/episode,
16 tasks, 8 bases, primitive word length 4, 64 audit events, and 200000 logical
execution units per batch. Unknown is not an empty relation or a refutation.
Logical fuel is not a hard wall-time bound.

Existing `(dlm ...)`, `(space ...)`, and `(contracts ...)` remain separate APIs.
`dlm save` does not save basis90. This experiment neither changes the Maru compiler
nor claims a new promoted compiler image. Historical release documents/manifests
are retained as historical evidence, not manifests for this working version.

Details, trust boundary and discovery limitations: [basis90-design.md](docs/basis90-design.md).
