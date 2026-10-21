# DLM 0.0078

Exploratory Maru-native deductive learning. This version adds **first-class
nondeterministic execution**, checked conditional-proof patterns, recursive
FLDx2 training and small propositional Beth/Craig operators. It is not an
established deductive attention architecture or an LLM-equivalent learner.

`v0.0077` and earlier directories/stores are unchanged. No user stores or FLD
exports were copied. No Python, GPU, Shen or Screamer runtime is used by the
model. Python/pyarrow are dataset adapters and independent test drivers.

## Original Maru REPL, one process

```sh
./scripts/selfssl.sh --reasoning /tmp/reasoning78.sexp
```

```lisp
(dlm 'think
 '(problem classical-prop-v1 ((p 0) (q 0))
   (sequent classical-prop-v1
     ((imp (pred p ()) (pred q ())) (pred p ())) ((pred q ())))))
(dlm 'advance 3)          ; partial work, not logical failure
(dlm 'branches)           ; contexts, frames, remaining obligations, partial DAG
(dlm 'nd-start 1000)      ; original reader runs cooperative idle slices
(dlm 'pause)
(dlm 'learn-proof)        ; admission requires independent certificate checking
(dlm 'proof-library)
(dlm 'save)
(dlm 'close)
```

Restore the same path to resume a saved ready job. New stores start empty, not
with implicit domain knowledge. `think` replaces the current job explicitly;
learned patterns remain. `advance` is manual; `nd-start` schedules 20-transition
slices. One idle-task slot is shared with the inherited relation learner.
Long checks/replay/evaluation are **not preempted**. Ctrl-C exits, Ctrl-D ends the
original REPL. There is no new terminal frontend or shell-per-round runner.

Branch-local provisional execution:

```lisp
(dlm 'choose-program
 '((choose (((assume provisional) (define-local concept candidate)
             (bind x a) (require x b))
            ((bind x b) (suspend need-evidence) (accept answer))))))
(dlm 'advance 50)
(dlm 'branches)
(dlm 'resume-branches)
(dlm 'advance 50)
(dlm 'next-branch)        ; discard delivered answer, backtrack to remaining ORs
(dlm 'advance 50)
```

`choose`, `assume`, `bind`, `require`, `define-local`, `fail`, `suspend` and
`accept` operate on immutable branch contexts. These results are explicitly
**provisional**, never independently true axioms or checked G3 theorems.
Bindings use consistency matching, not general unification. Suspended branches
remain saved; the scheduler skips them. FIFO scheduling is deterministic and
fair over ready branches, not random or hardware-parallel.

## G3 and learning semantics

- Existing `classical-prop-v1` and independent checker are unchanged.
- OR alternatives are two branch-local left-first/right-first decomposition
  strategies. A selected rule's **every** child is required (AND).
- Explicit `prove`/`assemble` frames and partial DAGs survive interruption. A
  candidate countermodel must falsify the **original** root, not just a leaf.
- Learning canonicalizes a checked proof's ground atoms by first occurrence,
  keeping repeated atoms, **both complete ordered contexts**, and its DAG.
- Later problems may instantiate a pattern with unseen predicates, arities and
  objects. Every instance is checked again; no trusted `lemma` rule is added.
- This is whole-sequent **bijective atom-renaming reuse**, not arbitrary formula
  substitution, context weakening, unrestricted lemma composition or universal
  rule induction. Lookup is currently a bounded linear structural search.
- Stored conditional lemmas do not certify that their premises are world facts.
  No gold labels, empirical assumptions or provisional branch definitions are
  promoted through this admission path.

Limits: 64 live OR branches; 16 alternatives/choice; program nesting16;
256 instructions/list; at most32 proof patterns; reasoning log128 events and
20,000 requested transitions per store. Formula/context/checker bounds are
inherited. Context/branch capacity suspends work, not logical refutation.
`advance` accepts0..1000 transitions. Capacity suspension cannot be solved just
by resuming with unchanged limits. Ticks do not bound individual checks.

## Native persistence and compatibility

`nd-open`, `nd-save`, `nd-close` explicitly manage `reasoning-session78` files.
Snapshots contain library, machine, contexts, partial certificates and semantic
`proof/program/run/resume/next/learn` events. Load replays from empty state and
compares the **entire** result; persisted frames are not trusted. Writes use
advisory locking, data-only dump/read, validation, `.previous` checkpoint and
atomic replacement. No eval of snapshot data, signatures or fsync guarantee.
Malformed reader syntax can still abort as in Maru. Replay is bounded but costly
and is included in REPL latency; repeated commits replay prior work.

Existing `axiom-space77`, `dlm-session77`, graph75, proof-store-v1, symbolic73,
web74 and legacy public function signatures remain supported. They are **not**
silently merged or migrated into the new store. The relation learner remains:

```sh
./scripts/selfssl.sh --demo /tmp/relations77.sexp
```

Its `start/status/observe/query/retract` commands and fixed relation-composition
grammar are unchanged. New reasoning uses `nd-start/branches/proof-library`.
`pause` stops either scheduler; `save/stop/close` recognize an attached reasoning
store. Use `nd-close` explicitly when independently managing both store kinds.
Application modules still load from `src/dlm`; the embedded compiler and generic
REPL tasks retain the existing source-free/self-hosting behavior.

## Bounded Beth/Craig experiments

```lisp
(dlm 'interpolate '((p 0) (q 0))
 '(and (pred p ()) (pred q ())) '(pred q ()) 1000)
(dlm 'beth '((p 0) (q 0))
 '(and (imp (pred p ()) (pred q ())) (imp (pred q ()) (pred p ())))
 '(pred p ()) 1000)
```

Nullary propositional vocabulary only, at most4 atoms. Craig constructs a
shared-atom DNF by finite model projection and checks `A |- I` and `I |- B`.
Beth rejects inconsistent theories, checks uniqueness using a fresh renamed
predicate, constructs a target-free DNF and checks both conditional directions.
Proof budgets can prevent certification. These are bounded experiments, not
minimal definitions, proof-extracted interpolants or general FOL algorithms.
They do not automatically enter the learned library.

## Fixed-data FLDx2 experiment

```sh
python3 adapters/recursive_fld.py \
  --out experiments/fld/recursive-small --limit 20 --budget 40 --passes 2
```

The native process receives only premises/goals, selected split membership and
fixed budgets. Train passes resume unresolved positive/negative proof machines;
checked patterns can affect later fresh jobs. Cold training uses identical
slices without admission/reuse. Validation/test freeze the train library and
compare cold versus learned arms with the same transition budget. Gold is opened
only after native execution. Test is opt-in (`--include-test`); the completed
small experiment did **not** evaluate test. Unsupported quantified inputs remain
unsupported, never UNKNOWN or training failures.

Observed small run, first20 unfiltered rows per split:

| Evaluation | Supported | Correct | Incomplete | Reuse hits |
|---|---:|---:|---:|---:|
| validation, cold | 5/20 | 2/5 | 3 | 0 |
| validation, learned | 5/20 | 2/5 | 3 | 0 |

Training supported13/20, learned2 patterns. Two passes did not improve train
classification in this sample. Library serialization2,047 bytes; learned train
state1,031,987 bytes, including unfinished search/certificates and copied
library snapshots. This is **not compression**. See `docs/fld-recursive-small.json`
for wall/CPU/RSS, all arms and accounting. Tick savings on a constructed unseen
renaming are tested, but **no FLDx2 validation improvement was observed**.
A larger first100/budget200/two-pass run with test enabled was externally stopped
at180 seconds; it has no completed evaluation and is not evidence of quality.

## Verification and remaining work

```sh
./scripts/run.sh test
python3 -m unittest discover -s tests -p 'test_*.py' -v
./scripts/compiler.sh rebuild
./scripts/compiler.sh verify RELEASE_ID
./scripts/compiler.sh promote RELEASE_ID
```

See `docs/implementation.md`, `docs/verification.log`, `docs/release.txt` and the
actual PTY transcript. New independent checks cover417 sequents,16 Beth theories,
256 Craig pairs, deterministic slicing, isolated provisional contexts, replay
forgery, locks, atomic rollback and frozen-gold isolation. The inherited3,392-case
G3 oracle and relation/graph/Horn tests remain mandatory.

**Not implemented:** quantified G3/FOL, binder normalization/capture-free
substitution/eigenvariables, equality, G3T, Russellian descriptions, arbitrary
predicate/program synthesis, general axiom composition, proof-derived concept
invention, unified storage migration or task-level LLM/resource equivalence.
The runtime and research operators here are a bounded foundation, not completion
of the entire proposed v0.0078 research program. No GitHub commit/push is made.
