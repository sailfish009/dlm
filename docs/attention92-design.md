# Attention92: declared search visibility and checked deductive workspaces

## Status and boundary

0092 adds native application control over a frozen0091 executable core. It does
not replace the existing basis learner, invent new world axioms, train a neural
selector, or establish a latent-axiom theory. The working research question is
whether context-dependent activation/routing can reorganize actual deduction,
while source data and question meaning stay fixed.

The local `declarative-attention` review supplied the idea of reversible,
explicit reference selection. No upstream source was copied: this is a small
native symbolic protocol with different correctness obligations. It uses no
Torch masks, KV backend, generated-tag parser, or upstream model. If source is
copied in a future change, preserve the upstream MIT notice.

## Reuse versus additions

Inherited and unchanged:

- `basis91-ir.l`: model, patterns, prefix definitions, expansion/role checks.
- `basis91-plan.l`: embeddings and minimum-operation covers.
- `basis91-formation.l`: data-led interpretations and conservative basis formation.
- `basis91-execution.l`: independent full-source primitive evaluator/certifier.
- `basis91-session.l`: source versions, archive/model separation and learner API.

New modules:

| Module | Responsibility |
|---|---|
| `attention92-ir.l` | Immutable context, source index, validated ID/environment domains, work records |
| `attention92-control.l` | Eligible operator generation, marginal estimates, typed focus proposal, next action |
| `attention92-execution.l` | Scoped worker; independent coverage and complete-row gates |
| `attention92-step.l` | Pure state transitions, provisional/local/final publication boundaries |
| `attention92-session.l` | Public API, replay-admitted restore and atomic checkpoint-before-publish |

The existing Space79 versioned task-sharing/AND-closure patterns informed the
separation of obligations, but its propositional library/scope is not merged with
the relational core. No LLVM, MLIR, compiler or runtime redesign is involved.

## Representation

```text
(context92 EXECUTION-CORE91 EPISODE PATTERN POLICY INITIAL-FUEL)
(scope92 ORIGINAL-FACT-IDS EFFECTIVE-BASIS-IDS)
(frame92 PREVIOUS-SCOPE PREVIOUS-INTENT PREVIOUS-PHASE)
(intent92 OP)
(pending92 OP STATUS PROVISIONAL-ENVS)
(work92 REMAINING PLAN VERIFIED-ENVS SCOPE STACK PENDING PHASE
        FUEL METRICS TRACE FINAL-MATCHES)
(attention-state92 1 CONTEXT IMMUTABLE-INDEX WORK COMMAND-EVENTS)
(attention-session92 1 CONTEXT WORK COMMAND-EVENTS)
```

The index is reconstructed, not trusted from a checkpoint. Work environments
contain `(VARIABLE VALUE)` pairs. Keys are unique0..3; values are names. Foreign
or conflicting entries are rejected, not silently removed during row comparison.
`match91` results preserve all question roles and refer to original source fact
positions. No filtered-view renumbering or hidden witness projection occurs.

The model contains raw source facts and conservative definitions, not training
answer rows. Current query work/trace is separate transient or resumable control
state, not learned model parameters. `query` always starts fresh; a saved
completed job may expose its already-verified result after admitted replay.

## Commands and phases

```text
ready --choose92/focus92--> focused --apply92--> applied
applied --local92, coverage+row checks pass--> local --restore92--> ready
applied --local92, insufficient view--> need-widen --widen92--> focused
ready + no remaining atoms + empty stack --finish92--> complete
valid transition + insufficient logical fuel --> unknown
invalid command/check --> rejected92, previous public state unchanged
```

`choose92` runs the native policy and materializes a focus/intent. The command
history records the policy invocation; the trace records its concrete scope and
operator. Explicit `focus92` commands are also supported for interventions.
`proposal` is read-only inspection; its cost is not charged to a later unrelated
execution. `tick` meters the policy action it actually performs.

```lisp
(focus92 EPISODE VERSION BASIS-EPOCH FACT-IDS REQUESTED-BASIS-IDS OP)
(apply92)
(local92)
(restore92)
(widen92)
(global92)
(finish92)
```

A focus checks exact episode/version/epoch, distinct numeric IDs, eligible atom
coverage and basis availability. Its effective basis IDs include the transitive
prefix dependency closure. Nested scopes are permitted up to depth4. A restore
restores the reference scope and a still-eligible parent intent, **not old
bindings**: independently committed child results survive. An aborted provisional
application is discarded without changing the verified workspace. If a child
consumed a parent's intended atoms, the obsolete parent intent is cleared.

`global92` removes the current visibility restriction; `widen92` retries the
current intent with all original facts available. Neither changes premises.
`local92` is a verification/commit boundary for a prepared workspace, not an
unrestricted local deduction language. The worker uses that workspace in later
applications; the verifier remains allowed to read the authoritative source.

## Eligibility and semantic preservation

The question is a positive connected conjunction. An eligible operator is either
one remaining primitive atom, or a checked basis embedded in distinct remaining
atoms. Its role-preserving expansion must consume an exact subset, with no
new/dropped/repeated conjunct. The accumulated plan plus primitive residual must
expand to the original full atom multiset. Completion requires no residual.

The worker interprets the actual selected `fact91`/`call91` plan. Prefix call
bodies are mapped through their exported arguments and recursively dispatched.
B2 calling B1 is an actual call, not a flattened trace label. The worker only
fetches source facts whose ORIGINAL IDs belong to the current view. Primitive
steps merge bindings, enforcing repeated variables but not implicit inequalities.

The core meaning does not change when a different order or factorization is
selected. No current-model rule, source version or definition body is rewritten
by a query. This is active **query-plan** adaptation, not yet persistent policy
learning or reorganization of the whole learned library.

## Independent admission, not blind masking

A scoped application is provisional. Admission performs two independent checks:

1. **Coverage:** scan original facts against the expanded atoms and all
   PRE-existing environments. A potentially matching fact must be in the view.
   This is a sufficient overapproximation: shared-variable constraints may later
   eliminate some included facts. It does not use the policy's source index.
2. **Exact row semantics:** evaluate the expanded primitive conjunction on the
   full source with the predecessor evaluator and merge the previously verified
   workspace with the predecessor join. Compare complete environment sets,
   including absence, to the scoped worker's proposed set. This uses neither the
   new planner nor the new worker and cannot fill missing worker answers.

An incomplete view causes widening, not acceptance of empty results. Sufficient
coverage with wrong/omitted rows causes rejection. Budget exhaustion causes
unknown and exposes no provisional answer rows. The final plan is checked and
all returned rows receive exact original-fact witnesses through `b91-certify`.

This reference execution is deliberately expensive. It checks the finite query
instance, while the structural gate preserves the logical expression. Finite
answer coincidence never licenses a chain-to-fork rewrite or a new universal
law. The trusted kernel still includes the source validator, expansion checker,
predecessor primitive semantics, and the Maru runtime. No general mechanically
verified completeness theorem is claimed; independent exhaustive tests supplement
these contracts.

## Policies

- `ordered92`: first operation of the existing minimum-op cover, all facts visible.
- `indexed92`: same operator choice, but union of indexed candidates compatible
  with each current binding across each expanded atom.
- `adaptive92`: enumerate eligible primitive/basis operations and select a cost
  proxy computed from goal, current bindings and full-source index metadata.
- `narrow92`: the same adaptive choice but only the first proposed fact ID; an
  explicitly artificial stress policy for incomplete focus/fallback.

For k expanded atoms and a workspace environment, let `n_i` be each atom's
marginal index-bucket size. The estimate is:

```text
sum_over_environments (sum_i n_i + product_i n_i) / k^2
```

Integer cross-products compare candidates; ties prefer more covered atoms, then
encounter order. The index has predicate, left, right, exact-pair and self-loop
buckets. No joined answer, oracle label, future query result or reference-checker
row is supplied to the selector. Only checked workspace bindings feed later
choices. The heuristic is hand-written, can be worse than fixed indexing, and
ignores important costs such as local replay/serialization. It is not learned
attention, semantic similarity, or a truth score.

## Contexts, caches and source changes

A context owns one immutable model and one episode/version. It is independent of
the current learner and may run after the learner and its training archive are
removed. Source version and basis epoch are checked on commands. To query a
retracted/replaced corpus, start a new context from its newly exported model;
old commands are then stale. An explicitly retained old model supports
historical inference. No external revocation/authentication service is promised.

There is **no partial result-table cache** in the new worker. Only independently
verified binding workspaces survive scope switches. Its index is immutable
metadata reconstructed from this context's original source. This avoids the
invalidity of carrying a partial empty table into a later global view.

For stronger controls, the measurement driver shares predecessor COMPLETE
relation/basis tables within one immutable episode/batch; `memo` also shares
structural plan tables. These caches reset at episode and batch boundaries.
The new policies use fresh per-query contexts/indexes. This intentional asymmetry
is reported, not hidden as a claimed routing speedup.

## Persistence and public boundary

`attention92` owns a live immutable state. `step/tick/run` stage a candidate;
attached sessions checkpoint it before publication. Rejected commands or failed
checkpoints leave live state/expected-file state unchanged. Snapshot admission
reconstructs the state from validated context and events, comparing the full
work record (including scope stack, intent, bindings, metrics, trace and fuel).
Private `a92-step` expects an owned state; external data must enter through
`start`, typed `step`, or replay-validated `restore/open`.

Expected-file comparisons, advisory exclusive locks, `.next` and `.previous`
replacement follow the existing session convention. Failed close retains the
attachment and lock; successful close releases them. No automatic corruption
repair, fsync power-loss guarantee or cryptographic authentication is claimed.
Replay is synchronous and bounded; attached per-step checkpoints may repeat work
quadratically in prefix length. Experiment timings exclude attached storage.
Compatibility and exact next-choice reproduction require the same compatible
native policy/format semantics, not arbitrary future implementations.

## Bounds and cost accounting

Inherited: four relation names, four episodes, eight facts/eight nodes per
episode, one to three connected atoms/four variable roles, eight prefix bases,
512 rows. New: depth4,64 accepted command events, initial logical fuel0..200000.
`run` accepts1..64 transitions. An interrupted finite prefix remains pending;
exhaustion is not false and no partial training update occurs.

```text
(metrics92 ACTIONS INDEX-FACTS INDEX-PROBES WORKER-UNITS WORKER-READS
           BIND-ATTEMPTS BASIS-CALLS CHECKER-UNITS WIDENINGS LOCAL-COMMITS
           RESTORES CALLED-BASIS-IDS)
```

Logical fuel includes initialization fact charges, accepted actions, metered
policy index probes, worker dispatch/fact visits, predecessor checker units,
coverage tests and final witness obligations. It is not a uniform CPU operation
measure. List walks/allocation, preflight, plan generation, shape checks,
serialization and inspection are not fully charged; initialization can construct
its bounded index even when fuel is insufficient. No wall-time bound follows.
Metrics91 and92 are different units, so only like metrics are compared.

The experiment reports startup-inclusive wall/user/system time, child RSS,
model/evidence/audit/output bytes, and the largest serialized per-query
index/work/events profile. Those control bytes are not heap usage or additional
learned parameters. Worker read savings exclude index and global checker reads.

## Demonstrated limits and next research boundary

The same chain goal selects B2 on balanced data but t→s→r on selective data.
Worker fact reads fall64→3 versus ordered92 in the latter example. Nevertheless,
all five workload medians are slower than predecessor memo end-to-end. The
selector can be worse than fixed indexed control. Repeated scope/verification
costs and cold per-query control state are real, not optimized away in reporting.

The next separate experiment could reduce duplicated checking using a justified
kernel contract, share immutable indexes, or learn/refine a cost policy. Only
after isolating these effects should control influence candidate formation or
persistent basis reorganization. More rules, better indexing, adaptive scheduling
and genuinely learned internal organization must not be conflated.
