# Basis91 design and experimental boundary

## 1. Question, not a settled theory

Starting hypothesis: axioms/logical structures might share useful organizational
properties with latent-space data. The experiment asks whether applying logic to
data can form internal units which reorganize and participate in later reasoning.
It does not identify latent coordinates with axioms or similarity with truth.

Compared with0090, the learner no longer needs user-written task-expression lists.
It observes finite relational data, applies bounded logical pattern schemas, and
learns conservative structural definitions from successful applications.

There is no calculus-based integral learning, new neural training, general axiom
induction, novelty claim, or demonstrated equivalence with a neural latent space.
The original reference `/research/design_20261029.md` predates the clarified
hypothesis; its checks/representation-replacement constraints remain relevant,
not a final definition of latent axiom.

## 2. Existing functionality reused

Native Maru executes learning, checks, matching and persistence. Python is only a
developer input/oracle/timing driver. Existing fact representation, bounded-list
helpers, persistent field/table functions, raw snapshot reading, writer, advisory
locks and atomic file primitives are reused. Existing DLM/Space/Contracts and
Basis90 algorithms are retained as separate paths, not relabeled as new work.

New components:

| Module | Role |
|---|---|
| `basis91-ir.l` | conjunctive IR, prefix expansion, alpha/atom-order canonicalization |
| `basis91-plan.l` | structural embedding, role binding, alternative covers |
| `basis91-check.l` | independent witness, plan, model and admission checks |
| `basis91-execution.l` | finite matching, actual basis dispatch, caches, metrics |
| `basis91-formation.l` | data-led/model-led interpretation, candidate proposals |
| `basis91-session.l` | transitions, model/evidence/audit separation, storage/API |

The Basis90 primitive-word checker cannot certify fork/shared-target rewrites.
Basis91 uses explicit role maps and exact expanded conjunctions instead.

## 3. Three distinct logical statuses

1. **Background laws:** positive relational conjunction, variable substitution and
   conservative definition expansion. These are supplied, not learned from frequency.
2. **Interpretation attempt:** a proposed mapping of data to a logical structure.
   Missing/mismatched conditions yield no match, never an invented premise.
3. **Admitted basis:** a checked definition with full variable interface, dependency
   prefix and actual substitutions into execution views.

An admitted definition is not a new world law. For example, naming
`B(x,y,z) <-> r(x,y) and s(y,z)` never licenses `r(x,z)` or transitivity of `r`.
Frequency influences usefulness selection, not logical validity.

## 4. Representation and semantics

```text
pattern: ((REL VARIABLE VARIABLE) ...)
primitive operation: (fact91 REL (VARIABLE VARIABLE))
basis operation:     (call91 ID (VARIABLE ...))

(basis91 ID PATTERN BODY-PLAN)
(episode91 ID VERSION FACTS INTERPRETED?)
(reading91 EPISODE VERSION PATTERN ACTIVE-PLAN TRAINING-ROWS)
(match91 ALL-VARIABLE-VALUES ORIGINAL-FACT-IDS)

(basis-state91 1 SIGNATURE EPISODES LIBRARY READINGS AUDIT EPOCH)
```

Patterns have1..3 distinct connected atoms and contiguous variable IDs0..3.
All roles are free/exported; distinct variables may bind the same constant.
There are no implicit inequalities, negation, universal world-law induction,
constants inside patterns, or higher-order relation-name variables. Definitions
are specialized to primitive relation names; new constant names transfer, new
predicate meanings do not transfer automatically.

Answer rows give every role, including intermediate/shared variables. Fact IDs
are local to one immutable episode/version. A query returning no row is absence
in this finite modeled relation, not a proof of an external negative statement.

## 5. Applying logic to data

For an episode with at most8 facts:

- Enumerate all distinct2- and3-fact subsets.
- Retain connected structures and alpha-normalize their node roles.
- Canonicalize by trying all atom orders (at most6), preserving relation names,
  with stable numeric codes derived from signature order.
- Add all previously learned basis patterns, even when no match exists in this
  source. Try those first, then data-derived patterns.
- Route each pattern through available basis/primitive operations.
- Execute bindings and independently check each successful witness.
- Keep all successful readings, not just the first/winning explanation.

The data-derived portion starts from witnessed structures and therefore is not
unrestricted hypothesis search. The model-led portion explicitly tests known
schemas which may fail. `inspect` exposes attempts/plans/status/match counts
without feedback; `interpret` publishes successful readings atomically only if
the entire bounded batch completes. No failed/no-match row is a logical negation.

`coverage` reports which original fact IDs participated and which remain as
residuals. Residual does not mean false or permanently inexplicable. Sources
are never erased merely because some interpretation covered them.

Initial logical shape grammar is supplied by us. There is no discovery of the
rules of logic themselves and no automatic goal invention.

## 6. Formation and actual replacement

Candidates come from successful current readings with two active operations.
A two-operation body may contain a previous `call91`, enabling hierarchical
formation. Patterns/bodies are not supplied as desired learned answers.

Support counts distinct `(episode, version, unordered fact-ID set)` applications.
Automorphisms, repeated inspection and duplicate imports do not inflate it.
A support application must use as many distinct source facts as pattern atoms;
this is a selection criterion only. Execution still correctly permits reusing a
fact for multiple atoms when variables coincide.

Candidate heuristic: `support * (expanded_atom_count - 1) - 1`; ties use encounter
order. It is provisional and fact-order sensitive, not learned neural attention,
source independence or a CPU-cost predictor. Renaming/atom-order normalization
preserves the pattern universe, not necessarily the winning candidate under ties.

Admission requires:

- full input state and source-witness checks;
- canonical pattern, prefix-checked definition and exact body expansion;
- support>=2 and a two-operation body;
- complete rewrite coverage of all existing readings;
- exact old identity/version/pattern/plan binding;
- new plan expansion equal to the original atom multiset with the same roles;
- at least two realized new-basis uses and fewer active view operations.

The new definition/active plans/epoch/audit publish together after successful
checkpoint when attached. The next interpretation can apply the new unit, and
the next formation sees current plans containing that unit.

Definitions remain append-only and raw/residual instance facts remain necessary.
Only active view plans are replaced. No global basis minimization, module deletion
or theory-wide reaxiomatization is implemented.

## 7. Independent meaning and witness gates

The admission checker calls neither the proposer, data enumerator, router nor
matcher. It recomputes each plan's expanded primitive conjunction and checks all
role positions. Reordering conjuncts is allowed; changing shared variables,
dropping intermediate roles and self/forward dependencies are rejected.

This is a restricted algebraic equivalence certificate: renaming and conjunction
structure preserve the query relation for every primitive interpretation. It is
not a general first-order equivalence decision procedure or a mechanically
verified implementation of Maru itself.

Witness checking separately reconstructs each atom from the returned role values
and verifies its exact source fact ID. Reconstructed witnesses are checked after
execution; training answer rows are never returned as fresh answers. Completeness
of the join implementation is additionally tested by an independent finite oracle.
Equal answers on one complete graph do not license a false role rewrite.

## 8. Executable core is not the training-answer archive

```text
(execution-core91 SIGNATURE EPISODES LIBRARY VIEWS EPOCH)
; VIEWS contain (reading91 EPISODE VERSION PATTERN ACTIVE-PLAN), without rows.

(basis-session91 1 EXECUTABLE-CORE TRAINING-EVIDENCE AUDIT)
```

`model` exports the executable projection. `infer` checks its structural semantics
and runs it even if training witnesses/history/current learner state are absent.
Normal query/run/probe preflight also checks executable definitions/plans rather
than traversing training proofs. Original query patterns remain as interface
mappings and are included in size/cost accounting.

A pure external-model evaluation is not admission of its claimed training origin
and cannot publish a learned model. Source facts are input assumptions, not
cryptographically authenticated world truths. A full `open` checks the core and
replays the bounded audit, compares the reconstructed executable core and all
training evidence. A serialized verified marker never bypasses that boundary.

Evidence and audit are separate fields, not separate content-addressed blob files.
Learning retains bounded application evidence to check support; inference does not
need it. Thus the executable projection can be smaller than a saved session, but
saved-session costs are explicitly reported rather than hidden.

## 9. Runtime, controls and causal probes

`raw` and `append` execute primitive plans with relation-table caching. `memo`
also caches structural prefixes. `basis` executes rewritten plans and materializes
basis tables on demand. Tables belong to one immutable source and one batch;
no result cache crosses an episode, probe, source retraction or process boundary.

All roles are combined by compatible bindings (AND); alternative bindings/witnesses
are enumerated (OR). Candidate selection/routing never weights facts into truth.
Budget/row-cap exhaustion yields unknown and no unfinished answer is returned.
Logical fuel covers selected visits/scans/bindings/joins, not all lookup,
canonicalization, validation or allocation costs. It is not preemption.

Controlled tests disable planner/proposer/history on active execution, run the
standalone core with the training archive unavailable, retract facts, and query
unseen constants/structural combinations. Disabling all bases is the raw control:
semantic ability should remain with sufficient budget because definitions are
conservative; operational costs and budget completion may change.

There is no separate trained inductive neural-model control in0091. Contextual
activation, combination and intervention are functional observations, not proof
of a shared latent geometry or a new learning principle.

## 10. Bounds, storage and limitations

4 primitive relation names;4 episodes;8 facts/episode;8 nodes/episode;3 atoms and
4 variable roles/pattern;8 prefix definitions;368 readings (4*(84 subsets+8 known
patterns));512 answer rows;32 audit events; fuel0..200000.

Episode IDs are immutable while present. Retraction removes that version's
readings/support; re-observation gets a fresh version. Definitions survive because
they are conservative, while no source-dependent match survives in a cache.

The store holds an advisory lock, compares the expected file value, validates and
reads back `.next`, keeps `.previous`, atomically replaces, then publishes memory.
Failed checkpoint/close preserves live state/attachment. There is no fsync-based
power-loss guarantee, hostile filesystem sandbox, asynchronous replay or history GC.

A model can have fewer active operations but more metadata/body bytes and worse
CPU cost than primitive memoization. These are measured negative results, not
reasons to change correctness conditions or discard the workload.
