# DLM v0.0076 — checked classical propositional sequents

Implements the first P0/P1 release of `/research/design.md` on top of preserved
0075 Horn/graph/web/symbolic behavior. All proof search, certificate checking and
model evaluation run in Maru. No LLM, neural model, Z3 or Python runtime is used
by the proof kernel. Maru/compiler sources are unchanged.

## Run

```sh
cd /research/dlm_v0.0076
./scripts/run.sh test
./scripts/proof.sh                         # scoped modus ponens; persistent proof store
STORE=/tmp/my-proof ./scripts/proof.sh my-problem.sexp 1000
./scripts/proof-verify.sh /tmp/my-proof/state.sexp
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

`proof.sh` uses a lock, verifies the previous store, normalizes the input, searches,
serializes with reader-safe `dump`, rechecks serialized evidence and canonical
input SHA256, retains a dated snapshot, then atomically replaces `state.sexp`.
Failure preserves the old file. No fsync/power-loss durability or signatures are
claimed. `sq-store?` checks evidence; use `proof-verify.sh` to also check the hash.

## Implemented logic

- Profile `classical-prop-v1`: ordered, duplicate-preserving antecedent/succedent
  occurrences; ground predicates, bottom/top, not/and/or/imp. The succedent means
  disjunction, **not** a choice of intuitionistic right-or rule.
- Cut-free G3c with atomic identity, bottom-left and explicit top-right/top-left/
  bottom-right rules. All generated premises are required, including both AND
  branches. No structural rule or premise can be silently inserted or deleted.
- Deterministic bounded search; independent certificate checker reconstructs
  each rule, without calling the search successor implementation.
- Topologically serialized certificate DAGs. Shared premises are allowed;
  duplicate IDs, forward/missing references, cycles, changed contexts, malformed
  occurrences, profile mixing, invented rules and missing branches are rejected.
- A falsifying open leaf yields a total ground-atom valuation. Independent
  evaluation checks it against the **original** root, not just the leaf.
- Two-direction classification: PROVED has a proof of A; DISPROVED has a proof
  of not A; UNKNOWN has two checked countermodels; CONFLICT has both proofs.
  Resource exhaustion stays `incomplete`, never UNKNOWN. A positive countermodel
  alone does not establish DISPROVED.
- `proof-store-v1` / `g3c76-v1` retains the problem, fixed search event, result,
  metadata and canonical input hash. It is not merged into graph75/symbolic73/
  web74, and changes to a premise require a new checked problem/result.

```lisp
(problem classical-prop-v1 ((p 0) (q 0))
 (sequent classical-prop-v1
  ((pred p ()) (imp (pred p ()) (pred q ()))) ((pred q ()))))
```

A signature maps predicate names to arities (0..32). Ground `(const NAME)`
arguments are also allowed: distinct ground predicate tuples are propositional
atoms. This is quantifier-free relational reasoning, **not** quantified FOL or
natural-language understanding. Unsupported/free/function/quantified terms do
not pass the P1 runtime schema; the FLD adapter reports quantified input as
`unsupported` rather than feeding it to the runtime. There are no initial domain
axioms, and no automatic import of graph75 observations or web documents. In a
classical context contradictory assumptions explode; Horn75 still does not.

Runtime APIs (load with `scripts/run.sh repl`):

```lisp
(sq-formula? 'classical-prop-v1 formula signature)
(sq-search problem 1000 'fixed)                 ; (result STATUS EVIDENCE VISITS)
(sq-verify certificate root signature 10000)    ; verified / invalid-input / incomplete
(sq-check-countermodel problem model)
(sq-classify signature assumptions goal 1000)
```

Budgets count **visited obligations** or checked certificate nodes, not primitive
instructions, schema traversal, list scans, allocation or verification work.
The fixed policy does not learn and does not memoize; branching can be expensive.
Input depth/context/signature limits are explicit in `formula.l`; search budgets
are 0..9000. Verification is not an arbitrary hostile-input sandbox.

## FLDx2 adapter and audit

Optional adapter dependency: Python + pyarrow; proof runtime does not need either.

```sh
python3 adapters/fld.py --out experiments/fld/audit
python3 adapters/fld.py --out experiments/fld/validation-smoke \
  --split validation --limit 100 --evaluate --budget 1000
# Data-only runtime batch (no labels):
./scripts/fld.sh 1000 < experiments/fld/validation-smoke/validation.sexp
```

The adapter follows the actual generator's left-associative equal-precedence
binary grammar, respects parentheses and quantifier scope, and requires full
consumption. Empty contexts are valid; `fake_formula` placeholders are explicitly
unsupported. Row/version/file hashes, raw text and occurrence IDs are retained.
Gold proofs/labels/negative hypotheses go to separate evaluator-only JSONL;
only premises, target and signature are submitted to Maru. The negative example
column is **not** treated as the current target's logical negation. Evaluation
uses `proof_label`, not the closed-world `world_assump_label`.

Full audit (data version 0.31, all rows, no label filtering):

| split | total | supported | quantified | placeholder |
|---|---:|---:|---:|---:|
| train | 100000 | 38446 | 61059 | 495 |
| validation | 5000 | 1938 | 3035 | 27 |
| test | 5000 | 1935 | 3038 | 27 |

No parsing failures on this corpus. These are syntax-support counts, not solved
counts. Full row provenance/reasons live under the generated audit directory;
compact hashes and counts are in `docs/fld-audit.json`.

Validation smoke: first 100 rows, 44 supported, 31 correct, 13 incomplete at 1000
visits **per direction**; supported accuracy counting incomplete as incorrect is
31/44 (70.45%), coverage 44/100. Resolved labels: 10 PROVED, 11 DISPROVED,
10 UNKNOWN; no resolved mismatch. 26004 total search visits; about 21.4 seconds
including process/checker overhead on this machine. No training, teacher, policy
selection or test-set accuracy measurement was performed. This is not a full
FLDx2 benchmark. Reports: `docs/fld-validation-smoke.json`, `docs/fld-evaluation.log`.

## Verification and preserved features

- Inherited 0075 tests rerun before changes: `docs/baseline75.log`.
- Every G3c rule has a positive test and adversarial rule/context/reference/
  occurrence/branch mutations. DAG-sharing and classical-vs-Horn behavior tested.
- 3392 small sequents compared against all four independent two-atom truth-table
  valuations: zero mismatches. Includes every pair of depth-one formulas plus
  fixed-seed deeper/multi-succedent cases. Checker also runs without search loaded.
- 18 Python tests: parser/gold isolation, oracle, proof-store lock/restart/hash/
  string/forgery tests, inherited six HTTP tests. Inherited Horn and graph oracles
  each compare 20 seeded cases. Logs in `docs/`.
- Compiler lifecycle: `scripts/compiler.sh rebuild`, `verify ID`, `promote ID`.
  Verification runs all tests, hashes adapters/scripts/fixtures, checks candidate/
  next/third LLVM and stripped-binary equality, and retains source-free tests.
  Release result is recorded in `docs/release.txt`.

Preserved entry points: `scripts/run.sh graph|symbolic|constraints|interaction`,
`scripts/graph.sh`, `scripts/selfssl.sh`, `scripts/web.sh`; inherited stores are
not copied as training state. No existing logic profiles/codecs were changed.

## Explicitly deferred

P2 binder normalization, capture-free substitution, eigenvariables and fair FOL
instantiation; P3 equality; P4 g-sequent accessibility/path-Horn transforms;
P5 learned ordering/experience controls; MLIR, unified-store migration, domain
semantics and natural-language extraction. These have **not** been implemented.
Self-host equality is reproducibility evidence, not a proof of logical soundness.

Licensing: Maru `LICENSE.maru`/`maru.lock`; local FLD-corpus license is CC BY 4.0,
FLD-generator Apache-2.0. Original datasets are unchanged and not bundled as
implementation source; the local FLDx2 card points to FLD-corpus without an
explicit license field, so verify upstream attribution/terms before distribution.
DLM publication licensing remains to be confirmed. No code from the reference
calculi or FLD-generator was copied; their grammar/rules were independently used.
