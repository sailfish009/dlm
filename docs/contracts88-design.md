# Native joint curriculum88

## What changed from87

The contract verifier is no longer only a manually invoked library API beside
the relation learner. Queued contract goals are work items for the original
`d77-step` and cooperative `d77-start`/reader-idle scheduler. Both kinds of work
commit through `d77-commit` into one locked snapshot. One source process owns
model mutation, scheduling and storage; Python is used only for developer tests.

New source modules:

- `src/dlm/contracts88-curriculum.l`: bounded pure agenda/transition/replay logic.
- `src/dlm/contracts88-session.l`: joint transactions, publication, checkpoints,
  original-REPL commands, scheduler integration and migration hooks.

Changes to existing seams: `repl.l`, `session-store.l`, `search-session.l`,
`contracts87-runtime.l`, `run.sh`, the existing recursive experiment shell/driver.
The87 explorer/checker and Boolean IR remain in place. `c87-search` now factors
out the actual space79 nondeterministic batch operation so a goal frontier can
advance by pages, rather than repeatedly testing all16 candidates.

## Model and event protocol

A joint snapshot is DATA, not executable source:

```lisp
(dlm-session88 1 NATIVE-MODEL ROUND EVENTS CURRICULUM)
```

CURRICULUM is a13-field list:

```text
0 curriculum88
1 schema version1
2 mode: relations | contracts | mixed
3 library87: checked modules with certificates
4 goal88 records in declaration order
5 next mixed scheduler turn: contracts | relations
6 contract candidate batch1..16 (default4)
7 verification fuel per candidate1..200000 (default2000)
8 cumulative contract candidate-fuel reservations, <=20000000
9 plain native relation cursor
10 last relation stop reason
11 cumulative relation requests, <=100000
12 last/persistently configured relation budget1..1000 (default200)
```

A goal is `(goal88 TEMPLATE STATUS CURSOR CONTEXT ATTEMPTS REASON OUTCOMES)`.
Its template is a well-typed contract87 with an empty body. Names are immutable
queue identities, unique among at most16 declarations; duplicate or differently
specified redeclarations are rejected. CONTEXT contains exact library contract
bindings plus fuel. OUTCOMES retain the last page's checked candidate statuses
and counterexample/unknown diagnostics, not a proof that the entire goal is
impossible. Solved procedures carry their actual certificates in the library.

New events:

- `(curriculum88 MODE)`
- `(goal88 TEMPLATE)` / `(retry-goal88 NAME)`
- `(contract-config88 BATCH FUEL)` / `(relation-config88 BUDGET)`
- `(library88 CHECKED-LIBRARY)` for existing manual library publication/import/reset
- `(contract-run88)` for a scheduler-selected contract page
- `(relation-run88 BUDGET)` for a scheduler-selected native relation step

Original observe/define/retract, routing83 and search84/85/86 events also replay.
Joint replay uses the same underlying `a77-*`/`a84-run`/`n86-run` proof-gated
operations, not Python approximations. Native search feedback/controllers are
reconstructed from the log, not treated as a second authoritative cache. Plain
native incomplete cursors now survive joint checkpoints as well.

The round counter is operational metadata as in older codecs, not a truth input.
The persisted scheduler turn, frontiers and budgets determine the next work item;
restarting does not depend on an unpersisted `round % 2` convention. Private direct
writes to globals are not a persistent configuration API; use the budget commands.

## Scheduling and unresolved obligations

The compatibility default is `relations`. Registering a goal does not silently
change that mode. `contracts` selects only the goal agenda; `mixed` alternates
runnable relation and contract work and falls back to the remaining runnable
domain when one is exhausted. Relations retain their existing search modes.
The same `dlm step`, `start`, `pause`, `save` and `close` commands serve both.

Each contract page contains at most BATCH of the existing deterministic grammar's
first16 candidates. They run through actual space79 choose/verify87/accept jobs.
A page can include both refuted and unknown candidates. Partial failure advances
a frontier; it does not refute the goal. A success must pass the goal-specific
final admission gate below before a checked operator is appended.

Goal states:

- `pending`: more candidate positions remain for this context.
- `solved`: an exact matching contract has a checked library module.
- `blocked`: this grammar/context was exhausted, a name conflicts, or library
  capacity was reached. This is **not** falsehood or global impossibility.
- `inapplicable`: no Boolean input satisfies Pre; never counted as learned.

A blocked search is not run again on every idle poll. Changed library bindings
or verification fuel make it runnable again and restart its frontier. This also
allows a later checked operator to help an older unresolved goal. A batch-size
change alone changes page width, not the search context. `retry-goal` explicitly
restarts a named search. Inapplicable goals require explicit retry; adding an
operator cannot change the Boolean meaning of their Pre.

Import or manual learning can satisfy an exact matching queued template. Removing
a library module reopens the affected solved goal. Name/spec conflicts remain
blocked; contracts are not silently substituted under an existing identity.
There is no automatic revision of user goals, web-to-goal grounding, goal utility
model or generation of a useful question curriculum in this release.

## Approval and domain separation

Search proposes candidates and positive tickets; it cannot approve them.
`c88-contract-step` requires:

1. The proposed contract, with its body removed, equals the requested template.
2. An independent `c87-check` validates its complete certificate against the
   exact current dependency prefix, with all applicable inputs, effects and Post.
3. The native session transaction can publish the next state and, if attached,
   can complete the joint checkpoint.

The second gate is additional to the search helper's own certificate check.
Forged search successes and valid proofs of weaker/different specs cannot satisfy
a queued obligation. A successful runtime branch is not universal verification.
The exact finite Boolean semantics, old/frame checks and prefix-bound procedure
summaries are described in `contracts87-design.md`. They do not imply full
Silicon compatibility, ownership permissions, SMT arithmetic or formal verification
of the Maru checker implementation itself.

Relation facts/definitions and contract state share ownership/scheduling/storage,
not an implicit logical universe. Generated procedures are not `observe` events,
and certified modeled transitions are not world observations. Retracting a native
source does not retract an independent Boolean-contract theorem; there is no
unimplemented cross-domain evidence bridge being asserted here.

## Atomicity, persistence and migration

Every new event is first applied to a local pure frame. Nothing is published yet.
The pending frame is reused only when the exact next event log and native model
match. `d77-commit` validates the transition, writes a checkpoint when attached,
and only then publishes the model, log, agenda, library and controller. On failed
joint step checkpoint the round is restored too; the scheduler pauses.

`d77-snapshot?` routes session88 to independent replay. Disk validation never
trusts the pending/live frame: it replays all events, checks imported module
certificates, reconstructs generated results and compares native and curriculum
state. Changed goal status, missing library, forged events, and a downgrade to an
older tag with88 events are rejected. The existing data-only read, advisory lock,
readback, previous snapshot and atomic rename protections remain the storage
boundary. Crash handling preserves completed checkpoints, not partial searches.

Manual87 `learn`, `admit`, `restore`, `load`, and `reset` library publications now
use this transaction boundary too. `dlm save/close` include the library and goal
agenda; no second save is needed. `contracts save/load` remain standalone
contract-store87 export/import for compatibility. `dlm reset` clears both domains;
`contracts reset` clears only operators and reopens applicable obligations.
Pause the idle scheduler first if the intention is to inspect an empty library
without immediately relearning queued goals.

Old77/83/84/85/86 files remain readable and relation-only workflows keep their old
codecs and fast path until a first88 event. That first transaction lazily rebuilds
the old prefix's model/controller without publishing temporary state. Previously
unlogged plain77 partial work was never durable and may be rescanned on migration;
new joint plain partial work is durable. Opening an old file cannot silently erase
live contract state: reset is required when incoming joint state differs.

The existing shell persists/respects joint configuration on restart. It does not
replace a restored relation budget4 with its default8 unless `--budget` is
explicitly provided. Demo flags do not reinject over existing goals/libraries or
observations. The single existing `recursive86.l` driver name is retained for
compatibility, but the implementation/printed version is88.

## Resource and cost boundaries

Existing limits remain6 Boolean variables,128 statements,8 acyclic modules,
16 generated candidates per context,256 total semantic/configuration events,
plus16 queued goals. Module capacity is reported before proposing more modules.
Reservations are BATCH-PAGE-LENGTH times requested verification fuel; cumulative
contract reservation and native-request limits are checked before executing that
page/step. The event cap is checked before work. Exhaustion pauses idle execution
without appending a refusal event, advancing the round, or calling it refutation.

These counters throttle requests, not total CPU, elapsed time or all validation
work. Library validation, the extra final gate, full journal replay and checkpoint
readback can repeat checks and add substantial cost. Native cooperative execution
can block the reader until a bounded step completes; an interval is not a hard
real-time guarantee. No speedup or amortized summary-cache benefit is claimed.
The grammar bound can miss even simple multi-statement plans; later operators or
more fuel do not guarantee success.

## Reproduction and tests

```sh
./scripts/run.sh proof experiments/space/curriculum88.l
./scripts/recursive-selfssl.sh --demo --contracts-demo --rounds 12 --budget 4 /tmp/fresh88.sexp
python3 -m unittest discover -s tests -p 'test_contracts88.py' -v
```

The demo learns native primitive paths2/3/4 and three Boolean procedures. Mixed
steps1/3 admit setx/sety; both88 requires four pages, and step10 admits the verified
composition. Subsequent steps wait without adding events. This demonstrates
recursive operator reuse and shared control/storage, not automatic goal discovery.

Fifteen new tests include both-domain learning, exact fresh-process next-step
comparison, plain relation and contract cursors, legacy lazy migration, changed
fuel/library retry, nonvacuity, forged search tickets/weaker specs/serialized
state, checkpoint rollback, original API publication/reset, restore conflict,
resource preflight, shell restart/config preservation and live reader-idle use.
The existing independent finite semantic and logic oracles remain in the suite.
Final release evidence is listed in `release-0088.md`.
