# Basis90: a first experiment in forming and replacing an execution basis

## Status and relation to the design

This is an implementation experiment derived from `/research/design_20261029.md`,
not a settled architecture or a claim of scientific novelty. Its hypothesis is
that factors of the current computation can become checked internal operators,
replace current expressions, and participate in subsequent formation/execution.

It does **not** learn independent truths from examples. Formalization is binary
relation composition over a caller-supplied signature. Input facts and question
programs remain explicit. Initial demonstration workloads are synthetic and offline.

| Design requirement | Implementation in90 | Remaining boundary |
|---|---|---|
| Form internal basis | repeated adjacent active factors | limited deterministic grammar |
| Replace existing representation | all registered active plans replaced after admission | old task interfaces retained |
| Recursive formation | `use90` tokens participate in later candidates |8 prefix-ordered definitions |
| Change subsequent computation | goal covering and basis dispatch/materialization | no learned neural scorer |
| Preserve meaning | independent expansion-word checker and dependency gate | relational fragment only |
| Separate execution and justification | core/audit snapshot fields | not separate blob storage |
| Exploration rather than predetermined victory | no-repeat/overlap/overhead and memo controls | tiny local workloads |

## Representation and API ownership

```text
(rel90 NAME)
(join90 LEFT RIGHT)
(use90 INTEGER-ID)

(basis90 ID BODY PRIMITIVE-WORD)
(task90 ID ORIGINAL-EXPRESSION ACTIVE-EXPRESSION)
(episode90 ID FACTS)

(basis-state90 1 SIGNATURE EPISODES LIBRARY TASKS AUDIT EPOCH)
```

All primitives are directed Boolean binary relations. `join90(R,S)(x,z)` means
`exists y: R(x,y) and S(y,z)`. Neither commutativity, symmetry, transitivity of a
primitive, nor closed-world conclusions about the external world are assumed.
Absence of a pair means absence in this modeled relation, not a universal fact.

`basis90` owns a separate native state/store. It does not mutate the legacy DLM,
Space79 or Contracts87 globals, and does not introduce a second Python learner.
All source imported through `observe` is explicit; runtime answers are never
promoted to source facts. Task creation is also explicit, not automatic goal invention. Public `task` and
`query` expressions use primitives/joins; `use90` belongs to internal plans and
checked definitions, not externally supplied opaque question IDs.

## Formation, replacement and recurrence

1. Flatten active joins to visible tokens. Keep `use90` atomic.
2. Enumerate adjacent token pairs; associative regrouping is legal in this grammar.
3. Count nonoverlapping occurrences within tasks, never across task boundaries.
4. Eligible candidates have support >=2, expansion length2..4, and no existing
   definition with the same primitive word. Duplicate tasks are an explicit
   workload frequency signal, not independent source corroboration.
5. Select by `2*support - 3`, with stable first-encounter ties. This is a provisional
   work-node heuristic, not a predictor of wall time or total stored bytes.
6. Propose a new prefix-ordered definition and replacement rows for every task.
7. Independently check the definition, word identity, original active plan,
   certificate and row coverage. Require at least2 explicit new-basis references
   and a strict reduction in work-expression nodes.
8. Stage the next state, checkpoint if attached, then publish it atomically.

The initial task router is also provisional: every transition checks the resulting
core, including original/active word equality, before any publication. A forged
initial plan cannot bypass admission just because no basis is being learned yet.

The next round counts factors containing the new token. It does not scan the
archived primitive expression or proof archive to manufacture a repeated parent.
The example first forms `B1 = r∘s`; later `B2 = B1∘t` and `rst` becomes `use90(2)`.

Discovery operates on workload execution expressions. It is not a trace-trained
statistical policy: tasks can supply structural support before they execute.
The demo executes batches before each learning phase, but a successful runtime
answer is not a logical premise for introducing a conservative definition.

There is no global minimum-basis solver, arbitrary concept synthesis, removal of
old unused basis definitions, or empirical rule induction. Basis declarations
remain append-only; **active working expressions are what is actually replaced**.
This is intentionally narrower than the long-term design's full reorganization.
If the top-ranked proposal fails the gate, the current policy reports rejection;
it does not yet backtrack through all lower-ranked possible bases.

## The gate and its guarantee

The checker never calls `b90-propose`, `b90-cover`, `b90-plan` or `b90-evaluate`.
It shares bounded IR/word primitives and a support-count helper with the proposer.

For each prefix, it recomputes a definition's word from its body rather than
trusting the serialized claimed word. Later/unknown/self references are rejected.
No two bases can claim the same primitive word. For each rewrite, it checks:

```text
expanded(old) = expanded(new) = certificate.word
```

Associativity of existential relation composition makes equal words denote equal
binary relations for every interpretation of the primitive relations in this
fragment. This is a restricted equivalence certificate, not a general G3/FOL
certificate or a formal verification of the Maru checker implementation itself.
A structurally false change is rejected even if some training graphs happen to
make its answers coincide. Equivalent plans can consume different fuel; an
operational `unknown` is not evidence of semantic inequivalence. A checked equal word is not evidence that a website's
claims are true.

The independent Python oracle enumerates all256 two-node/two-predicate graphs
(including empty graphs, cycles and self-edges),5 questions and3 execution arms.
This tests implementation correctness in addition to the structural argument.

## Symbolic attention decomposition and execution

`b90-cover` considers a primitive token and all basis words matching the current
word prefix. Candidates compete by remaining token count; ties keep the existing
primitive/older-basis plan. Word length<=4 bounds this search. The selected cover
is assembled into joins. This separates eligibility, competition and routing;
it is not multi-head Transformer attention or a trained goal encoder.

`b90-evaluate` interprets the **active expression**, with a table for primitives
and selected basis calls local to one immutable episode and one batch. A basis
body is evaluated on first demand; subsequent calls can use its materialized
relation. The evaluator does not execute the archived original task expressions
or replay history. However, the public execution entry still validates the bounded
core each batch, traversing original/active expansion words; that overhead has not
been optimized away. Primitive facts are still necessary input.

Joins require both operand tables (AND); alternative matching middle vertices
provide existential witnesses (OR/union), not a weighted average or a scored proof. A budget
exhaustion returns `unknown`, and the unfinished task is not emitted as an empty
answer. Completed earlier tasks may be included. Metrics count expression visits,
fact scans and pair comparisons, not every primitive CPU operation. Validation,
lookups, allocation and serialization are reflected in whole-process time, not
fully in these logical counters.

Transient queries route through the current basis without task registration or
feedback publication. Source retraction removes that episode. A later execution
starts with a new cache, so a replaced/retracted source cannot reuse stale answer
tables. Conservative definitions remain meaningful after the source disappears.

## Controls and measurement limits

- `raw`: original expressions, primitive and no generic-join memoization.
- `append`: the same basis is available but original expressions are unchanged.
- `basis`: active transformed expressions with basis materialization.
- `memo`: primitive expressions in canonical right-associated form, with structural
  join memoization. This helps distinguish naming/reorganization from simple caching.

`append` is NOT the legacy A77 learner, and none of these controls claim to model
all of the legacy system's costs. The measurement driver creates non-persistent
core views; it does not present their mismatched historical audit as valid saved
sessions. All arms pay the same formation phases before measurement queries.

`adapters/basis90_experiment.py` only supplies data, times fresh native processes,
checks answers using a separate join algorithm, and reports results. It never
chooses a basis or updates native policy. Four workloads, three graph seeds,
randomized arm order and two repetitions give96 runs. Logical metrics are for
the final query batch; each batch starts with a cold cache. CPU/RSS is per child
on Linux (`wait4`). No attached-checkpoint costs are in this measurement.

Core byte counts include original task expressions, transformed expressions,
source facts and basis bodies. Audit bytes and actual native output bytes are
reported separately. A basis can reduce work nodes while making a small core
larger. Timings are exploratory local diagnostics, not evidence of general speedup.

## Persistence and trust boundary

```text
(basis-session90 1 CORE AUDIT)
(basis-core90 SIGNATURE EPISODES LIBRARY TASKS EPOCH)
```

Restore first checks bounded core shapes, library dependencies and task word
identities. Then it independently replays explicit events and compares the whole
core. It does not trust a serialized `verified` marker. Replay checks supplied
admission rows; it need not rediscover which heuristic candidate would have won.
This proves a valid checked history, not authenticity of a caller-provided source.

Open holds an advisory lock and remembers the exact loaded file value. An attached
transaction stages a pure transition, validates/writes/readbacks a new snapshot,
keeps `.previous`, compares the old file, and atomically renames. Only then does it
publish the basis, working plans, epoch and audit. Failed saves preserve the old
live state; external file changes are refused. A failed close keeps the attachment.
Locks are released by explicit close or process exit.

This is not an fsync-based power-loss durability protocol, hostile filesystem
sandbox, content-addressed blob store or asynchronous checkpoint system. Snapshot
validation still replays the bounded audit synchronously. Execution avoids that
replay, but storage cost is deliberately not hidden as constant time.

## Limits and separate inherited fixes

8 primitive names;4 episodes;24 facts and12 distinct nodes per episode;16 tasks;
8 bases; primitive word length4;64 events; fuel0..200000 per execution batch.
Bodies are acyclic and prefix checked. Logical fuel is not preemption/wall-time.
Waiting on no repeated factor or capacity creates no synthetic learning event.

Separate stabilization changes:

- Web documents/collections/state/list fields are bounded before traversal; malformed
  ingress now errors instead of SIGSEGV. This does not add native SHA/span verification
  or bridge web claims into trusted observations. Ingress also rejects trailing data.
- Joint plain relation execution uses `a77-step-canonical`. It no longer consults a
  live Ground83 ordering cache during replay. `ground on` can still affect spatial
  queries/legacy plain routing, not joint plain candidate ordering. Previously
  invalid snapshots are not automatically repaired; relation-only codec behavior
  outside that joint path is retained.
- Packaging ignores generated LLVM files/local stores; tracked historical artifacts
  are not deleted. Historical0088 source/test manifests are not republished as90.

No compiler/MLIR/runtime platform source changed, no GPU/service is required, and
neither unrestricted web grounding nor full latent-axiom theory is claimed.
