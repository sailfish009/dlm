# Space79: operating rules and invariants

## Scope

Investigate connected computational units, not a new benchmark winner. Keep
classical G3c semantics, independent certificate checking and the original Maru
REPL. Pure Maru application changes; compiler, GC and platform files are unchanged.
No Screamer Common Lisp runtime is imported. No G3T, ST/MQST, general FOL or
specifically identified G3S calculus is implemented.

## Data and transitions

```
space79: format-version, pattern-epoch, units, obligation-index,
         ready-front, ready-back, jobs, patterns, next-id, ticks, statistics,
         definitions, historical-pattern-libraries
unit79:  id, kind, scope, status, data, dependencies, waiters, result, xyz
```

The leading tag occupies field0. `space.l` owns structural operations, immutable
ID tables, requests, rule units, subscriber notification and shared certificate
export. `space-execution.l` owns event dispatch, incremental certificate checking,
job delivery and scoped programs. `space-learning.l` implements proof annotations,
interpolation/Beth job protocols and subproof harvesting. `space-definitions.l`
implements naming and definition use; `space-session.l` owns persistence and REPL
commands. Sources are loaded in that order; mutual callbacks are explicitly bound
before use, avoiding Maru forward-reference encoding errors.

Every ready event has an explicit target; a two-stack FIFO schedules it. Sleeping
units generate no repeated queue scan. ID/key tables remain bounded association
lists: lookup/update can be linear in retained table size. New ID insertion is
constant-time cons; historical immutable tails are shared in memory. Serialization
does not preserve all pointer sharing, and can duplicate certificate/library data.
No constant-time lookup or general computational-complexity claim is made.

### Request and G3 collaboration

The request key contains the pattern-library epoch, signature, exact ordered root
sequent and scope. A repeated request registers another consumer on the same unit.
Each root freezes its library epoch; child requests inherit it even if learning
publishes a newer library meanwhile. Definitions do not smuggle new facts into a
root: user premises are explicit and immutable. There is no mutable global world KB
or automatic retraction migration across running jobs in this version.

A G3 obligation activates one canonical invertible decomposition rule. The rule
unit requests every child and waits. It is checked using the independent
`sq-check-step`, not a call to the expansion path. Repeated child IDs retain their
multiplicity in the rule's dependency list and exported premise list, while sharing
execution. This is legitimate DAG sharing, not dropping an AND obligation.

The current propositional calculus does not need to fork over every invertible
rule ordering. Real nondeterministic alternatives are represented by program
choice units. Possible future noninvertible rules must add explicit alternatives,
not reuse the current propositional ordering as a completeness assumption.

An atomic open leaf builds a total valuation of its own atoms. A rule can propagate
a child countermodel only after extending it and checking the parent root. No local
failure, missing message or resource exhaustion is a countermodel. Context overflow
suspends a rule, leaving its parent/job incomplete. An empty event queue means
quiescence, not necessarily that all waiting jobs have logically finished.

Proved obligations store `via RULE-ID`, or a reference to an existing proof pattern,
not full copied certificates at every internal node. A boundary DFS emits one
postorder node per shared proof unit; reused modules are inlined with remapped IDs.
Independent checking then processes one proof node per event. Certificates and
checker state at job boundaries still consume memory; this is not free compression.

### Scoped nondeterministic programs

`choose` forks immutable context values. Each child has a distinct scope ID, so
provisional assumptions or bindings cannot leak through the obligation cache.
`ask` explicitly adds the current branch's assumptions to the sequent antecedent,
waits for its proof/model result and resumes or fails that continuation. Generic
`accept` returns a provisional result, never a verified world assertion. `suspend`
retains remaining instructions; `resume` reactivates it. A delivered first answer
leaves other active alternatives paused when they next receive an event. `next`
acknowledges the answer and reactivates those alternatives. Bind/require performs
exact consistency, not unification, and local definitions are contextual data.

### Learning and formation

`study` is a proof job whose successful completion schedules a learn unit on the
same queue. The learn unit visits reachable solved obligations one at a time and
admits checked atom-renaming patterns through the existing pattern verifier.
A pattern preserves complete ordered assumptions and targets. New problems may
reuse a pattern inside their graph, not just at the original whole-problem root.
Publishing a pattern creates a new immutable library epoch; existing roots keep
their previous view. Imported certificates are not arbitrary new axioms.

The same traversal names encountered compound single-goal formulas as fresh closed
propositional definitions. These names represent existing formula structure; they
do not discover a universal predicate from examples. A definition unit stores
signature, target, body, condition, kind and evidence. Fresh naming is a conservative
extension with an explicit iff declaration; a Beth definition is conditional on its
theory. `use` creates both named and unfolded proof requests. The original named
certificate includes the definition/theory condition explicitly, so no unverified
fold/unfold operation is hidden inside the trusted G3 checker.

### Proof-based interpolation and Beth

New interpolation does not call the old truth-table projector. It annotates a
checked G3 certificate with a Maehara partition. For partition1 vs partition2:

- identity within partition1 yields bottom; within partition2 yields top;
- identity crossing1-to2 yields the atom; crossing2-to1 yields its negation;
- unary decomposition propagates the annotation;
- binary rules combine annotations with OR for a partition1 principal formula,
  and AND for a partition2 principal formula.

Occurrence colors follow negation across sides and duplication/decomposition to
children; they are not inferred from the symbol's name alone. The annotation uses
explicit visit/combine frames, one per event. The result must contain only shared
ground atoms and be within the supported formula shape. Both interpolant
entailments are generated as new jobs and independently checked. Construction can
produce redundant or excessively deep formulas; depth overflow is incomplete,
not evidence that no interpolant exists. At most6 nullary atoms are accepted.

Beth accepts at most4 original nullary atoms. It schedules: T entails bottom
(consistency test), T(P),T(P') entails P iff P' (fresh renamed target), then Craig
on T(P) and P versus T(P') implies P'. A checked countermodel to T entails bottom
is the nonvacuity witness. Nonunique theories return not-defined; inconsistent
ones are rejected. The extracted target-free formula is checked in both directions
under the original theory before a definition unit is stored. All these phases
use the same graph/event engine; no black-box theorem oracle is introduced.
This does not implement general FOL interpolation/Beth, uniqueness testing from
finite observed cases, or minimal information compression.

## Persistence and concurrency boundaries

A `space-session79` snapshot stores space plus semantic input events. Restore
replays from empty and compares the entire graph: IDs, scopes, waiters, queues,
certificates, definitions, layout and versions. Native snapshots are data, not eval.
Old77/78 stores remain separate and their old commands keep their behavior.

Normal command execution applies only its new transition. `save-async` captures an
immutable prefix and replays one logged command per service step; later model
commands may progress without altering the captured prefix. A log command can
itself request a bounded event slice. On replay equality, native dump/read validates
the candidate's data roundtrip; the current old file must exactly match the last
verified value from open/save. The write keeps a previous checkpoint and performs
atomic rename under an advisory lock. A changed old file is refused, not silently
replaced. Save failures leave a consistent but unsaved current model, not a claimed
rollback to an earlier in-memory state. Save/close synchronously drain validation
and save the latest prefix. Only completed explicit saves are durable.

Serialization, initial read/restore, proof export, table traversal and pattern
admission still execute synchronously inside service steps. The ready event budget
is not a primitive/time bound. No fsync, authentication, remote-reader sandbox,
append journal or preemptive scheduling claim is made. Unit reserve stops execution
before hard allocation capacity; retained obligations remain incomplete. Completed
units/jobs/library versions are not compacted. This limits long-running sessions.

The original REPL's one cooperative idle-task slot drives many space jobs. Legacy
learning modes are preserved but do not have independent simultaneous idle slots.
There are no worker threads/processes or thread-safe shared heaps. Spatial xyz is
layout metadata on a16x16x16 ID grid; place events may move units without changing
their logic. Distance-sensitive routing and neural/spiking dynamics are absent.

## Investigation criteria

Observe and falsify local behavior: AND waits for all premises; alternative
contexts are isolated; repeated requests share actual execution; new goals use
partial modules; naming creates no fact; Beth uniqueness/consistency matters;
interpolation uses only the shared vocabulary; save/restart resumes the same
partially active graph. These are operating-rule checks, not accuracy promotion
gates. The fixed probe has no labels and claims no task-level learning advantage.

The final verification includes48 Python tests, new417 semantic comparisons,
100 Craig pairs and six Beth theories, native module/definition/capacity tests,
all inherited oracles and restart suites, actual PTY launch/restart, and three
compiler generations with identical LLVM and stripped images. Source/test
manifests identify exactly what was verified. v0.0080 adds review-regression
contracts for malformed signatures, failed-check completion, alternative
exhaustion, child-job rejection, Beth completion-time capacity and partition-aware
annotation memoization. Self-reproduction remains a reproducibility check, not
proof of semantic correctness or native compilation of DLM application modules.
