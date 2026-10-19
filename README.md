# DLM v0.0073: recursive symbolic learning on Maru

This is the first executable slice of the symbolic-graph / constraint-runtime /
revisable-theory design. DLM is a Maru application, not a compiler-patching agent.
No LLM, tokenizer, embeddings, GPU, Python or PyTorch is needed at runtime.

## Run

```sh
./scripts/run.sh symbolic       # empty / one-round / recursive / scrambled arms
./scripts/run.sh test           # inherited and new assertions
./scripts/selfssl.sh 3          # three persistent learning rounds; resumes by default
./scripts/selfssl.sh 0          # repeat until Ctrl-C (saturates on fixed corpus)
bash tests/store-tests.sh      # restart and corruption checks
python tests/differential.py   # optional developer oracle, needs sibling 0066
```

`STORE=/path` selects a separate experience directory. An exclusive lock prevents
concurrent writers. Each committed generation retains the complete event log and
snapshot in a `.sexp` datum; `state.sexp` is atomically replaced. Input is read as
data, never evaluated. Restart recomputes each transition and checks the saved
state/graph. There is no signature, hostile-input sandbox, fsync durability,
compact incremental journal, or periodic replay checkpoint. Replay grows with the
number of rounds; repeating saturated rounds is not additional learning.

## Maru changes

`src/maru/source/symbolic.l` now owns finite-domain choice, immutable branch
backtracking, binary constraints, arc-consistency propagation and MRV. It has no
DLM dependency. `boot.l` loads it, and compiler images embed the source. Existing
CSP names remain compatible. The old `src/dlm/constraints.l` is only a shim.

```lisp
(symbolic-choose '((x (a b))) 'x)
(symbolic-solutions '((x (a b)) (y (a b))) '((neq x y)) 100)
```

These are explicit solver operations, not continuation-based `choose` inside
arbitrary evaluator expressions. Existing deterministic evaluation is unchanged.
Node budgets are not strict relation-check/time/memory budgets. Constraints still
require finite, well-formed domains with distinct names and valid references.
Self-inequality support was corrected and regression tested.

The modified runtime must be rebuilt before using 0073: an old 0072 image does not
contain this module. `scripts/compiler.sh rebuild`, `verify ID`, `promote ID`
provide explicit candidate gates; `reproduce` copies an embedded source snapshot,
not current external edits. Original seed and rollback are preserved.

## DLM model

`src/dlm/symbolic-learning.l` carries one immutable model value:

```text
(symbolic-state 73 EPISODES THEORY EVENTS GRAPH)
```

The graph interns entity/predicate nodes by structural equality, retains sourced
observation records, provides a predicate index, and derives argument-role groups
from positive observation signatures. These are structural groups, not discovered
world categories. Explicit negative observations are separate from unknowns.
No domain axioms are seeded.

DLM generates a bounded grammar of unary mappings, binary mappings and two-edge
Horn compositions from observed signatures. Maru enumerates legal candidate
alternatives. DLM evaluates each against fixed training observations, commits at
most one useful rule per round, and stores successful AND rejected verdicts.
The next round uses the revised theory, enabling dependent rules. Ranking uses
the existing symbolic coverage/debt/counterexample score, not gradient learning.
This is theory learning, not a newly trained CSP-ordering policy.

A later conflicting observation causes conservative whole-theory retraction.
This is soundly cautious but less selective than proof-dependency invalidation.
Replay rechecks admissions and retractions. Derived atoms are recomputed and are
never promoted to independently observed labels. Derived test goals require
membership-checked Horn proof verification.

## Fixed experiment

`experiments/symbolic/data.l` contains two training episodes and two held-out
episodes. All are synthetic relational observations, not natural language.
Predicates r/s/t are primitive observations; q/u are separately observed targets.
The synthetic generator defines q as composition of r and s, u as composition of
q and t. Those laws are NOT provided to the learner. Explicit counterobservations
cover the finite q/u complement in each synthetic episode: this closed finite
oracle is a dataset construction choice, not a general closed-world assumption.

Held-out episodes use new entity names and additional edges/joins. Their labels
never enter candidate generation, ranking or state updates. The relation
vocabulary is shared; there is no held-out-predicate or broad semantic transfer.

| Arm | Held-out goals proved | Explicit violations |
|---|---:|---:|
| Empty theory | 0/14 | 0 |
| One learning round | 8/14 | 0 |
| Two recursive rounds | 14/14 | 0 |
| Scrambled training targets, two rounds | 0/14 | 0 |

The third round saturates with two learned rules. The candidate pool has 60
rules; evaluated candidates are 60, 59, 58 over three rounds (177 total).
Candidate enumeration additionally expands 61 choice states per round, and each
rule evaluation performs multiple Horn closures. This is not an efficiency or
speedup claim. Independent proof checking shares the kernel implementation;
optional differential tests provide a separate Python implementation oracle.

## Verified release

Active candidate: `20261019T015829Z-7615` (built from this version's sources).

- 60 Maru/DLM assertions pass; optional 20 seeded Horn differential cases pass.
- Candidate -> next -> third: identical LLVM and stripped binaries.
- Empty-directory execution finds embedded choice/propagation source without an
  external Maru source tree.
- Separate-process experience resume, corrupted format rejection, and forged
  transition rejection pass without overwriting the previous state.
- Three persistent demo rounds are saved under `experiments/symbolic/store`.

## Not implemented yet

- Raw-text mention extraction, polarity/modality/attribution-preserving reading.
- Automatic semantic predicate discovery, alias resolution, category merge/split.
- Arbitrary higher-order rule synthesis or unrestricted predicate invention.
- Shared proof DAGs with selective invalidation, tropical/provenance algebras.
- Learned CSP variable/value ordering, continuous parameters or neural backend.
- Autonomous Maru source modification.

The next step is sourced, ambiguous mention/relationship candidates with an
independent observation channel, not treating model-generated conclusions as
self-supervised truth.

## Licensing

Maru's license is `LICENSE.maru`; source provenance remains in `maru.lock`.
No Bio or Screamer code was copied. DLM publication licensing remains to be
confirmed. Compiler fixed points establish reproducibility, not correctness.
