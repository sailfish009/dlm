# v0.0078 implementation boundaries

## Layering

No Maru compiler/platform source is changed relative to0077. Original generic
idle scheduling is reused. Model-specific execution is under `src/dlm/`:

| Module | Responsibility |
|---|---|
| `nondeterministic.l` | immutable OR branches, FIFO one-frame transitions, explicit AND continuations, proof/model output gates |
| `proof-pattern.l` | canonical ground-atom renaming, checked conditional proof storage and instantiation |
| `reasoning-session.l` | event-replayed native snapshots and extension of existing `(dlm '...)` dispatcher |
| `definability.l` | bounded propositional model projection plus independently checked G3 obligations |
| `experiments/fld/learn.l` | input-only native train/resume/admit/freeze/evaluate loop |
| `adapters/recursive_fld.py` | fixed Parquet export, transport, evaluator-only gold and resource accounting |

All inherited signatures/codecs are retained. New internal names have `n78-`,
`p78-`, `r78-`, `b78-`, `f78-` prefixes. The saved legacy dispatcher avoids
replacing `dlm-step(state,budget)`, `dlm-status()` and `dlm-observe(episodes)`.
No hidden import, migration or merging of user stores is performed.

## Explicit machine data

```lisp
(machine78 1 INPUT QUEUE ANSWERS FAILED TRANSITIONS NEXT-BRANCH-ID)
(branch78 ID CONTEXT FRAMES PROOF-NODES NEXT-NODE-ID POLICY VALUE-STACK STATUS)
(context78 BINDINGS PROVISIONAL-ASSUMPTIONS LOCAL-DEFINITIONS)
(answer78 BRANCH-ID KIND EVIDENCE CONTEXT)

(prove SEQUENT)
(assemble SEQUENT RULE POSITION NUMBER-OF-REQUIRED-CHILDREN)
```

Proof input includes its immutable source problem and library version/value;
program input includes its original data-only instructions. No native closures,
C stacks or Maru stack frames are serialized. Expansion places every child on
the continuation stack before its assemble instruction. Child IDs must already
exist in the branch-local DAG. `sq-verify` independently reconstructs premises;
it never delegates legality to `n78-action` or the inherited search expander.

OR choices fork context values, not shared mutable cells. The scheduler steps
one ready branch and appends its continuation after other queued branches. A
suspended branch is skipped, not discarded. `resume` reactivates suspended
continuations; `next` acknowledges/removes a delivered answer to continue other
alternatives. Normal `run` stops on the first answer and preserves remaining
branches. No later answer is automatically claimed equivalent to the first.
Earlier successful evidence survives in the semantic log and, if admitted, the
proof library; `next` intentionally removes it from the current answer field.

`assume` and `define-local` keep provisional context only. Program `accept` is
not G3 admission, and generic programs cannot inject `prove`/`assemble` frames.
Current bind/require performs exact value consistency checks, not unification.
The two initial G3 strategy branches are execution alternatives; logical
`or-left`, `and-right`, `imp-left` still require both premises. Since all current
G3c propositional rules are invertible, ordering alternatives do not increase
proof power. Broader choice/assumption integration into FOL remains research.

A frame counts as one transition even if its check takes significant time.
Budget0 leaves a ready machine incomplete. Context overflow restores the current
frame and marks it `suspended context-capacity`; branch overflow similarly
preserves a choice. They do not become logical failures. An explicit program
`fail`/unsatisfied require increments branch failure, not universal negation.

## Checked proof-pattern space

```lisp
(pattern78 CANONICAL-SIGNATURE WHOLE-SEQUENT CHECKED-CERTIFICATE)
```

Ground atoms are replaced simultaneously by fresh ordered nullary atoms. Atom
identity/repetition, formula constructors and both ordered contexts remain.
The canonical proof is independently checked. Instantiation reverses a new
problem's atom mapping and checks the resulting proof against that exact root
and signature. Different assumptions, repeated-atom relationships, context
orders and profiles do not match. Matching can rename ground atoms with different
predicate arities because propositional inference treats each complete ground
atom independently; it is not a first-order quantification claim.

There is no new trusted lemma/cut rule. Proof DAGs are reused as complete checked
certificates, not assumptions. Up to32 distinct canonical roots are kept; no
lossy replacement, premise erasure, compression objective, learned scoring or
universal axiom promotion is implemented. Fresh relation definitions in the
inherited0077 learner and conditional proof patterns are distinct objects.

## Persistence

```lisp
(reasoning-session78 1 (state78 LIBRARY MACHINE) SEMANTIC-EVENTS)
```

Replay begins with an empty state and applies only declared operations. It
recreates the complete machine, including queue order, bindings, DAG, statuses,
answers and costs, and compares it to the serialized value. Library admission
is repeated through the checker. A forged continuation, proof or unreplayed
pattern is rejected, never executed. Advisory lock, reader-safe dump/read,
`.previous` checkpoint and atomic rename reuse native0077 primitives. Old state
is validated before replacement; failed checkpoint leaves memory and disk state
unpublished. No fsync/authenticity claim. Hostile reader syntax can still abort
as in inherited code; this is not a sandboxed remote service.

At most128 events and20,000 requested transitions per log; each manual slice is
at most1000. Every commit currently replays earlier events, and disk validation
repeats replay. This is intentionally simple and can be expensive. Checkpoint
replay and partial-proof serialization are future optimization targets, not free
work excluded from performance accounting. Close/reopen can preserve a full log,
not reset its capacity. Store compaction/migration is not implemented.

## FLDx2 loop and falsifiers

Training uses premises/goals only. Both target and its logical negation have
separate machines; countermodel alone never proves the negative direction.
First pass starts rows in fixed order, admits checked proofs and lets later rows
reuse them. Later passes resume unfinished machines rather than relabeling
budget failures. Existing jobs retain the library snapshot they started with;
new library patterns do not retroactively alter a saved continuation. A parallel
cold arm uses the same slices with an empty library and no admission.

After training, the library is frozen. Validation and optional test each compare
cold and learned fresh machines under the same transition budget. No evaluation
row updates the library. Gold files are opened by the Python evaluator only
after the native process exits. Tests poison gold and confirm byte-identical
native output/library. Export retains the inherited left-associative grammar,
unsupported-quantifier accounting and proof_label semantics.

Observed first20 train/validation experiment has no held-out improvement or
reuse hit. Its representation cost includes a roughly1MB serialized learned
train state, not just the2KB library. A synthetic held-out atom renaming shows a
checked lookup in one transition instead of reconstructing the same proof;
this is a capability test, not an FLDx2 result. First100/budget200/two-pass/test
attempt exceeded an external180-second command deadline; no accuracy or test
score is available from it. Smaller evaluation is validation-only and makes no
fresh-test claim. See the reports for exact resources and denominators.

## Beth/Craig

At most4 nullary atoms; enumerate finite valuations, project satisfying models
to the shared vocabulary and build a DNF. G3 verification checks the resulting
entailments. Craig can mark an inconsistent antecedent as vacuous; Beth rejects
an inconsistent theory before uniqueness. Beth uses a genuinely fresh renamed
target, checks uniqueness across the two target interpretations, then certifies
both definition directions under the theory. Search exhaustion is not a claim
that no definition exists. No minimality, automatic generalization, FOL Beth,
proof-extracted interpolation, G3T or Russellian-description implementation.

## Verification scope

- Native safety/regression suite, including all old APIs and context-capacity.
- Python38 tests; new independent417-sequent/16-theory/256-pair semantic checks.
- Inherited3,392 truth-table cases and8-graph/47-definition oracle.
- Native restart with partially completed AND obligations; complete queue/DAG
  replay equivalence; branch suspension/restart/backtracking; false-store refusal.
- Live original REPL idle proof learning, locks, failed admission rollback and
  actual PTY launcher/restart transcript.
- Compiler rebuild, candidate/next/third LLVM and stripped equality; embedded
  generic REPL/source-free tests remain inherited. Self-host fixed point proves
  reproducibility, not semantic correctness or source-free DLM application code.

Quantifiers/binders/eigenvariables and general concept/program synthesis remain
unimplemented, rather than placeholder APIs counted as completed features.
