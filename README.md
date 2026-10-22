# DLM 0.0082 — native grounded graph and adaptive 3D index

v0.0082 adds a separate native Maru provenance/support graph, independent 3D
placements, local layout relaxation, exact-formula candidate retrieval with
complete fallback, evidence retraction and replay-verified snapshot data.
No LLM or neural representation is used. This is a bounded reference prototype,
not yet a demonstrated speedup or an actual LLVM MLIR dialect.
See [the contracts and limitations](docs/ground82-design.md).

```sh
./scripts/run.sh proof experiments/space/ground82.l
python3 -m unittest discover -s tests -p test_ground82.py -v
```

Six new tests bring the full Python suite to 61 tests. Previous version
directories and existing store formats are preserved.

## Inherited v0.0081 front-end

v0.0081 adds an optional **MLIR-shaped Python front-end**, not a registered
LLVM MLIR dialect. It verifies SSA/operation structure and lowers to the existing
Maru API without changing the compiler bootstrap chain. Direct `.l` execution
remains available. See [the scope and syntax](docs/space-dialect.md).

```sh
./scripts/dialect.sh verify experiments/space/dialect.mlir
./scripts/dialect.sh run experiments/space/dialect.mlir
```

Seven new translation/roundtrip tests bring the Python suite to 55 tests.
The rest of this document describes the inherited space79 engine.

Research question: **Which local operating rules let connected units constitute
reasoning, learning and reusable structure?** This is an exploratory execution
model, not a settled deductive architecture or a benchmark-performance release.

New: one Maru event space connects scoped nondeterministic programs, G3c proof
obligations, partial-proof learning, formula naming, proof-based propositional
interpolation and Beth definition jobs. All use the same ready queue and explicit
state. No MLIR, neural framework, GPU, external Screamer runtime or worker thread.

v0.0080 fixes the executable defects found in the v0.0079 review: malformed
definition signatures are rejected instead of crashing, failed certificate checks
finish the waiting job, alternative exhaustion is terminal, rejected child jobs
and Beth capacity exhaustion are explicit, and annotation traversal memoizes on
`(node-id, left-colors, right-colors)` instead of re-walking shared DAG regions.

Prior version directories and user stores are preserved. Old `dlm` APIs, profiles,
codecs and `selfssl.sh --demo/--reasoning` paths remain available. `space-session79`
is a separate, explicit format; old stores are not silently migrated.

## Run in the original REPL

```sh
./scripts/selfssl.sh --space /tmp/space79.sexp
```

```lisp
(space 'study 'example
 '(problem classical-prop-v1 ((p 0) (q 0))
   (sequent classical-prop-v1 ((pred p ()))
     ((and (pred p ()) (pred p ()))))))
(space 'step 6)
(space 'unit 0)
(space 'start 100)        ; cooperative execution while original reader waits
(space 'pause)
(space 'job 'example)
(space 'library)
(space 'definitions)
(space 'save)
(space 'close)
```

`prove` submits a query. `study` submits a query and automatically schedules
learning from its successful proof. Several jobs progress in one process.
Loading a store restores partial obligations and queues; the launcher schedules
ready work. New stores start empty. No fixed domain facts are injected.

## Local operating rules

- **Request:** intern an obligation by exact signature, ordered sequent, scope
  and pattern-library epoch. Identical requests subscribe to the same unit.
- **Expand:** a G3c unit emits required child obligations and an AND rule unit.
- **Wait:** a unit with unmet dependencies emits no periodic polling traffic.
- **Notify:** a completed child wakes only its registered consumers. Duplicate
  deliveries cannot complete an AND rule with missing premises.
- **Compose:** every required child must be proved; the rule is independently
  checked. An exported topological certificate is checked one node per event.
- **Choose/backtrack:** programs fork contexts and continuations. Bindings,
  assumptions and local definitions cannot leak into sibling scopes.
- **Suspend/resume:** preserve unfinished work. A budget/capacity limit never
  becomes logical refutation.
- **Learn:** traverse actual solved sub-obligations, canonicalize checked
  certificates and preserve their entire conditional contexts.
- **Name:** give encountered compound goal formulas fresh definition units;
  names alone assert no fact.
- **Reuse:** later fresh obligations can instantiate learned subproofs inside
  a different outer goal, not just match an entire old problem.

Ground propositional G3 rules are invertible, so this version chooses one fixed
rule ordering instead of branching over redundant left/right permutations.
Nondeterministic interpretation/assumption alternatives live in program choice
units; no false claim of additional logical power from rule permutations.

Every unit has a deterministic 3D grid position. `(space 'place ID '(X Y Z))`
changes layout only; it does not change logical meaning, routing costs or proof
rules. Logical dependency, branch scope and spatial location are distinct.
This is not a biological spiking-neuron simulation.

### Scoped nondeterministic program with real G3 work

```lisp
(space 'program 'alternatives
 '((choose
    (((assume (pred p ()))
      (ask (problem classical-prop-v1 ((p 0))
             (sequent classical-prop-v1 () ((pred p ())))))
      (bind x a) (suspend need-input) (accept first))
     ((bind x b) (require x a) (accept impossible))))))
(space 'step 100)
(space 'resume 'alternatives)
(space 'step 100)
(space 'job 'alternatives)
```

`ask` creates a G3 obligation with that branch's assumptions explicitly included
in its antecedent. Proof success resumes the continuation; a checked countermodel
fails only that branch. `accept` is still a **provisional program result**, not a
world fact. `define-local` stays branch-local. Bind/require is exact consistency,
not general first-order unification. `next NAME` acknowledges a delivered answer
and reactivates remaining alternatives. Suspended capacity cannot be fixed merely
by resuming under unchanged bounds.

## Structural learning and definition formation

Patterns remain checked bijective **ground-atom renaming**, now harvested from
reachable subproofs and available at every obligation. Repeated children share
one proof unit. A library epoch is immutable and inherited by that obligation's
children; later learning does not silently alter a running proof's lookup view.
Subsequent program `ask`s are new requests and may use a newer epoch.

`study` also creates fresh names for compound single-goal formulas encountered
in proved sub-obligations. This is formula naming, not universal concept discovery
or an information-compression claim. No ranking reward or held-out accuracy gain
is required to keep the research direction.

```lisp
(space 'define 'pair '((a 0) (b 0))
 '(and (pred a ()) (pred b ())))
(space 'use 'pair-query 'pair '((pred a ()) (pred b ())))
(space 'step 1000)
(space 'job 'pair-query)
```

Definition use requests both the original named goal and its unfolded body.
Fresh definitions introduce an **explicit iff condition** in the original
certificate; Beth definitions retain their theory as a condition. No opaque
trusted macro/lemma rule is added to the old checker. Empty observations do not
become true just because a formula has a name. Partial modules still require exact
ordered contexts: arbitrary weakening, formula substitution, unification and
unrestricted program synthesis are absent.

## Proof-based Craig and Beth jobs

```lisp
(space 'interpolate 'interface '((p 0) (q 0))
 '(and (pred p ()) (pred q ())) '(pred q ()))
(space 'beth 'explicit '((p 0) (q 0))
 '(and (imp (pred p ()) (pred q ())) (imp (pred q ()) (pred p ())))
 '(pred p ()))
(space 'start 100)
```

Craig follows a checked G3 proof with occurrence-partition annotations (Maehara
style), composing intermediate formulas locally. Each annotation frame is an
event, and both resulting entailments are separately checked by graph jobs.
No truth-table projection constructs the new interpolant. At most6 nullary atoms;
excessive annotation depth can produce an explicit incomplete result.

Beth (at most4 original nullary atoms) runs consistency, fresh-renamed-target
uniqueness, interpolation and both definition directions as dependent jobs on the
same engine. Inconsistent theories are rejected. Success adds a conditional
`definition79` unit. `use` can subsequently activate it under its original theory.
A defining expression is not automatically minimal, empirical truth or a new
independent axiom. These are classical propositional operators, not ST/MQST,
G3T, a specifically named G3S calculus or general FOL Beth.

## Persistence and responsiveness

Normal commands apply only the new transition, not the entire history. Jobs,
contexts, shared proof graph, layout and library versions are persistent values.

- `save`: capture current state, replay the full semantic log, validate, write
  data, read back, keep `.previous` and atomically replace while holding a lock.
- `save-async`: validate an immutable captured prefix one log event per service
  step. Model work can continue; the saved file truthfully records that prefix.
- `save-step`: manually service pending validation. `start` also services it.
- `close`: synchronously drain validation and save the latest state before
  releasing the lock. It refuses to close on a failed save.

Restore always replays from empty state and compares the **entire graph**, not
just the output. Forged queue/status/definition data are rejected, never evaluated.
Unexpected external checkpoint changes are not overwritten. No fsync, signing,
remote-reader sandbox or crash-safe append journal is claimed. After a failed
save, the current consistent in-memory state remains **unsaved**, not rolled back.
Only explicit completed saves are durable; idle ticks do not checkpoint each time.

This remains one-thread cooperative execution, not physical parallelism. The
original reader has one idle-task slot, shared with legacy modes. `space start`
stops the legacy task before registering its own. Checks of boundary certificates
are incremental, but rule expansion, table lookup, proof export, learning admission,
serialization and file I/O may still take time within an event. There is **no hard
wall-time bound per event**, and synchronous `save/close` can block the REPL.

## Bounds and efficiency boundaries

- Two-stack FIFO avoids scanning all units for readiness.
- Waiter links and shared obligation IDs avoid duplicate subgoal execution.
- New units prepend to persistent ID tables; updates preserve older snapshots.
- ID/key tables are bounded association lists, **not constant-time hash maps**.
- Certificate materialization occurs at boundaries; completed jobs/check tasks and
  historical library values still cost memory and serialized bytes.

Unit ID limit4096, execution stops at4000 to reserve creation headroom; pending
work is incomplete. Pattern limit32; definition limit64; log limit1024 events and
100,000 requested transitions; manual slices0..1000. Completed units are retained;
retirement/graph compaction is not implemented. Formula/context bounds are inherited.
These are bounded investigations, not an endless autonomous curriculum.

## Investigation and verification

```sh
./scripts/run.sh test
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 adapters/space_report.py
./scripts/compiler.sh rebuild
./scripts/compiler.sh verify RELEASE_ID
./scripts/compiler.sh promote RELEASE_ID
```

`experiments/space/run.l` is an operating-rule probe: shared requests, partial
learning, renamed subproof reuse inside a different goal, definition activation,
proof interpolation and Beth on one event engine. It is **not** a benchmark or
an architectural promotion gate. `docs/space-experiment.sexp` and resource report
record actual behavior and costs, including serialized inspection state.

The inherited Python tests cover new417-sequent truth-table comparisons,100 interpolation
pairs, six Beth theories, branch isolation/backtracking, layout invariance,
async-prefix replay, forged snapshots, locks, original REPL interactivity and
five v0.0080 review-regression contracts and seven v0.0081 front-end tests.
Inherited3392-case and other oracles remain. Native tests additionally cover
partial reuse, naming without asserting facts, and capacity/incomplete behavior.
See `docs/verification.log`, `docs/repl-transcript.txt`, `docs/release.txt` and
source/test manifests for the final self-host checks.

Maru compiler/platform sources are unchanged; DLM modules still load externally.
The embedded compiler remains self-reproducing through external clang/linker.
No real multicore execution, neural plasticity, distance-sensitive geometry,
quantified reasoning, general concept/program induction, optimal compression or
LLM-equivalent task/resource claim is made. No GitHub commit/push is performed.
