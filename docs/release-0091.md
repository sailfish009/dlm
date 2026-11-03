# DLM0.0091 working experiment: applying logic to data

## Status

Implemented in `/research/dlm_v0.0091`, copied from0090. The predecessor remains
clean and its compiler binary is unchanged. Existing product source files were
not modified except the launcher, root version/usage and ignore metadata.

This is an experimental application-level implementation, not a new compiler,
claimed new mathematical axiom theory or complete latent-axiom model.

## Implemented loop

```text
structured facts, without user task programs/answer labels
 → data-derived logical patterns + existing learned schemas
 → role binding and checked applications (including failed trials)
 → repeated application structures
 → independently checked conservative definitions
 → replacement of active interpretation plans
 → actual execution and later interpretation using the new units
```

All learning/checking/execution/storage is native Maru on CPU. The Python adapter
is a development input/timing/independent finite-oracle driver. No GPU, neural
training, network service or online source acquisition was used.

Details and boundaries: [basis91-design.md](basis91-design.md).
Commands and compatibility: [README](../README.md).

## Observations

### 1. Data-only formation and hierarchy

The demo receives six facts, yielding three successful interpretations: `r-s`,
`s-t`, and `r-s-t`. It first forms the `r-s` basis, then a new `r-s-t` basis whose
body contains the first call and a primitive `t` operation.

The three active plans have7 primitive operations before formation and4 after
these two rounds. The two new bodies contribute4 more operations: **7→4 is an
active-view reduction, not a reduction of total representation to4**. A third
valid basis can still name the remaining standalone `s-t` reading; the first two
rounds are not falsely described as saturation.

The second unit is actually dispatched; queries on new constants produce fresh
bindings and source witnesses. Fork/shared-target structures also form checked
bases in tests, not just word-composition operators.

Output: [basis91-demo.sexp](basis91-demo.sexp).

### 2. Applying known logic can fail, without inventing a premise

After learning, a source containing only one `r` fact triggers attempts of the
existing `r-s` and `r-s-t` schemas. Both finish with zero matches. No conclusion
or false negative fact is introduced. The original fact remains as an explicit
residual. Inspection does not publish learning feedback.

Retracting the training source clears its readings/support. Conservative basis
definitions remain usable on a genuinely new source; the old answer cache does
not survive. Tests also remove the current learner/training-archive access and
run the standalone executable projection successfully.

Output, including all-basis ablation and new string constants:
[basis91-interventions.sexp](basis91-interventions.sexp).

### 3. Four execution controls

The controls are primitive matching (`raw`), structural-prefix memoization (`memo`),
unused appended bases (`append`), and actual basis-rewritten execution (`basis`).
Primitive relation tables are cached even in raw, so raw is not an intentionally
unindexed matcher. The append control is not the full legacy A77 learner.

Final cold-batch counters in the fixed chain demo:

| Metric | raw | memo | append | basis |
|---|---:|---:|---:|---:|
| Active view operations |7|7|7|4|
| Basis-body operations |0|0|4|4|
| Logical units charged |55|45|55|54|
| Fact scans |18|18|18|18|
| Binding-pair join attempts |16|12|16|12|
| Basis calls |0|0|0|3|
| Actual operation visits |7|5|7|8|

All bindings and intermediate/source witnesses agree. **Basis changes execution
and reduces joins versus raw, but does not beat primitive memoization here.**
Naming, argument mapping and materialization introduce their own costs.

### 4.96 fresh-process measurements and negative size results

Four fixed workloads ×three seeds ×four arms ×two repetitions, randomized order.
Seeds shuffle/rename the training facts and perturb the heldout source; they are
not three independent broad training distributions. Every arm pays the same
interpretation and at most two formation phases, then three cold query batches.

The independent oracle checked576 final-training-batch answer tables and720
heldout tables: **1296 answer/witness checks, zero mismatches**. Earlier repeated
batches contribute timing but are not separately counted as oracle checks.
Heldout probing publishes no feedback. It includes unlearned chain/fork/target
questions as well as the learned reading patterns.

Median executable-model bytes, including source facts, original interface patterns,
active plans, definitions and metadata; excluding separately reported evidence/audit:

| Workload | raw | memo | append | basis |
|---|---:|---:|---:|---:|
| chain |527|527|668|623|
| fork-overhead |276|276|341|326|
| ambiguous |2114|2114|2255|2135|
| no-repeat |245|245|245|245|

The chain core grows527→623 bytes despite the view reduction. Fork grows276→326.
The no-repeat source forms no basis. The ambiguous source retains19 alternative
readings rather than selecting a single explanation.

Median whole-process wall seconds:

| Workload | raw | memo | append | basis |
|---|---:|---:|---:|---:|
| chain |0.782|0.758|0.786|0.793|
| fork-overhead |0.662|0.636|0.674|0.668|
| ambiguous |1.792|1.836|1.808|1.843|
| no-repeat |0.598|0.614|0.590|0.598|

Startup, input, learning/checking, queries and serialization are included; attached
checkpoint costs are not. Child CPU/RSS and actual output/evidence/audit sizes are
recorded. Times are small local diagnostics with few repetitions, not robust
hardware performance claims. **No general CPU speedup or model-size reduction
was demonstrated.**

Control models are nonpersistent views and retain the common learned evidence/
audit for accounting. Their modified executable projections are not replay-valid
saved sessions. The experiment is not a measurement of an optimally implemented
raw learner which never pays formation/history costs.

Raw records and per-pattern heldout activation/match profiles:
[basis91-experiment.json](basis91-experiment.json).

## Verification actually completed

| Check | Result |
|---|---|
| `python3 -B tests/run_offline.py` | **160 passed**,365.126s;6 legacy local-HTTP tests excluded |
| `test_basis91.py` separately | **27 passed**,58.936s |
| Finite graph oracle | all256 two-node/two-relation graphs ×8 patterns ×4 arms: **8192** complete answer/witness checks, zero mismatches |
| `./scripts/run.sh test` | native suites passed |
| `tests/store-tests.sh` | restart and corrupt/forged-store rejection passed |
| `tests/runtime-tests.sh` | source-free embedded native runtime passed |
| `tests/graph-store-tests.sh` | graph restart/retraction/string/atomic rejection passed |
| Data-only input example | interpretation/formation/four controls/snapshot output passed |
| Intervention driver | failed known-schema trials/residuals/ablation/retraction/new data passed |
| Shell syntax, diff whitespace, local links, evidence checksums | passed |

New tests also cover independent admission with proposer/matcher/planner disabled;
false initial routing/matching; changed shared roles; dropped witness roles;
self/forward references; false source fact IDs; version mismatch; empirical
coincidence on a complete graph; repeat/automorphism support inflation; limits,
unknown/partial results; checkpoint rollback; external file change/corrupt open;
fresh-process same pending proposal and next state; two-process writer exclusion
and failed-close lock retention;500 malformed trees; isolation from legacy APIs.

The offline runner guards Python socket calls and excludes six inherited tests
which start a loopback HTTP server. It is not an OS sandbox. Selected native/file/
PTY child drivers use no network; the inherited offline web-cache regression ran.

Full restore checks executable semantics, independently replays bounded events,
and compares the executable model and all current training evidence. Pure `infer`
checks definition semantics but does not authenticate a claimed learning history.

Logs/environment/predecessor comparison are under `docs/basis91-evidence/`.
`source.sha256` binds working sources/tests/scripts/root usage; `SHA256SUMS` binds
this report, design and outputs. Historical predecessor manifests are not reused
as working0091 checksums.

## Interpretation, not overclaim

| Question | What0091 supports |
|---|---|
| Can the model apply logical structures to data? | Yes, bounded explicit role matching with checked witnesses |
| Can existing internal logic be tried and fail? | Yes, with no hallucinated premise/negative fact |
| Can application structures form later computation units? | Yes, conservative definitions including hierarchical calls |
| Are active expressions actually replaced? | Yes, and dispatch is measured |
| Can execution be separate from the answer archive? | Yes, standalone core inference is tested |
| Does this improve CPU cost/representation size? | Not generally; the measured memo/size results are negative |
| Is a latent-axiom theory or neural analogy established? | No |

The learned objects are still bounded structural operators. The experiment adds
data-led/model-led interpretation and role-preserving organization, but does not
prove a qualitative separation from abstraction/library learning. It does not
learn new independent truths or discover a minimum axiom basis.

## Hypotheses and next investigation

The remaining hypothesis is that richer organization of valid logical structures
can function as a useful internal inference basis. Current evidence supports the
mechanical loop, not that broader conclusion. Candidate scoring only rewards
support/expanded size; it ignores actual call/metadata/evidence costs. Larger,
more varied structures and cost-aware selection/retirement would be separate
experiments, not changes to the meaning-preservation gate.

## Preserved boundaries

- The grammar, relation names and positive-logic semantics are supplied. No free
  text, online grounding, automatic useful-goal invention or neural scorer.
- No projection of intermediate roles; arbitrary quantified/negative/recursive
  world theories are outside scope.
- Definitions accumulate; only active view plans are replaced.
- Source facts/interface mappings remain in the core. Evidence and audit are
  separate fields, not content-addressed blobs or an fsync durability redesign.
- Logical fuel is not a wall-time bound; canonicalization/validation are additional
  bounded costs.
- No changes to old DLM/Space/Contracts/Basis90 source or Maru platform source.

Of218 tracked predecessor product files, only `.gitignore`, `README.md`, `VERSION`
and `scripts/run.sh` differ in0091; all implementation modules are additions.
The0090 Git status is clean, and compiler hashes match exactly:
[predecessor.json](basis91-evidence/predecessor.json).
