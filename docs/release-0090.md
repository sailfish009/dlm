# DLM0.0090 experimental working version

## Implemented

Created `/research/dlm_v0.0090` from0089. Prior product directories were not edited.
`VERSION` now reads0.0090. This is not a compiler promotion or a published release.

The central experiment is **formation → independent checking → active replacement
→ later execution → formation using a previously learned basis**. It is separate
from the existing `dlm step/start` learner. See [design](basis90-design.md) and
[run instructions](../README.md).

| File | Responsibility |
|---|---|
| `src/dlm/basis90-ir.l` | bounded expression/core IR, dependency/word checks |
| `src/dlm/basis90-discover.l` | repeated current-token factors, provisional selection |
| `src/dlm/basis90-rewrite.l` | goal covering, rewrite proposals/certificates |
| `src/dlm/basis90-check.l` | independent admission, transition/replay gate |
| `src/dlm/basis90-execution.l` | actual basis dispatch, scoped tables, fuel/metrics/controls |
| `src/dlm/basis90-session.l` | separate public API, atomic checkpoint-before-publish |
| `experiments/basis90/` | two-round demo, data-only input, measurement driver |
| `adapters/basis90_experiment.py` | developer timing/oracle, no native policy decisions |
| `tests/test_basis90.py`, `test_review90.py` | experiment and separate stabilization tests |

Existing bounded-list/IR helpers, native fact representation, raw snapshot reader,
writer and filesystem primitives are reused. The dedicated relation-word gate and
instrumented reference executor are application-level additions. Existing ND/G3,
Contracts87/88, A77 and Space79 algorithms are not renamed as new mechanisms.

## Observations

### Actual replacement and use

The demo generated `B1 = r∘s`, then `B2 = B1∘t`; neither was supplied as a checked
answer. The final active `rst` plan is `use90(2)`.

For its five tasks:

| Metric | raw | append only | basis rewrite | structural memo |
|---|---:|---:|---:|---:|
| Active work-expression nodes |29|29|13|29|
| Additional basis-body nodes |0|6|6|0|
| Pair comparisons in final batch |48|48|24|34|
| Basis dispatches |0|0|6|0|
| Cache hits |12|12|6|10|

All answer sets agree. These logical counters exclude various validation, routing,
allocation and serialization operations; fewer comparisons is not by itself a CPU
speedup. Source facts and the original task mapping remain part of the model.
Output: [basis90-demo.sexp](basis90-demo.sexp).

### Four workloads, including negative/overhead cases

The fixed CPU experiment used4 workloads ×3 source-graph seeds ×4 arms ×2 repeats,
randomized order: **96 fresh native runs,360 answer-table checks, zero mismatches**.
All arms pay both discovery phases, followed by3 cold-cache query batches.
No attached-checkpoint cost is included. End-to-end timings include interpreter
startup and output, so this is not an isolated inference benchmark.

Median canonical execution-core bytes (source facts, task mapping, active plans,
checked bodies and metadata included; audit separately recorded):

| Workload | raw | append | basis | memo |
|---|---:|---:|---:|---:|
| recursive |859|954|802|859|
| no-repeat |453|453|453|453|
| small-overhead |383|429|391|383|
| overlapping factors |821|916|802|821|

For example, `small-overhead` reduces active nodes6→2 but grows the core383→391
bytes. Its median wall time was0.564s raw,0.574s basis,0.561s memo. The recursive
case measured about0.630s raw and0.623s basis. These tiny differences, few repeats
and startup-heavy measurements **do not establish a robust wall-time improvement**.
The raw/memo execution-core views do not pretend to be the checked learned-session
snapshot, and the append control is not a full legacy A77 performance baseline.

Raw records, wall/user/system time, child max RSS, audit/output byte counts, request
hashes, logical counters and medians: [basis90-experiment.json](basis90-experiment.json).
Environment and compiler hash: [environment.json](basis90-evidence/environment.json).

### Validation actually run

| Check | Result |
|---|---|
| `python3 -B tests/run_offline.py` | **133 passed**,291.442s;6 legacy loopback HTTP tests excluded |
| `test_basis90.py` separately | **19 passed**, including500 seeded malformed trees |
| `test_review90.py` separately | **5 passed**, including seeded offline web cache roundtrip |
| `./scripts/run.sh test` | native suites passed |
| `tests/store-tests.sh` | restart, corrupt/forged-store rejection passed |
| `tests/runtime-tests.sh` | source-free embedded runtime passed |
| `tests/graph-store-tests.sh` | graph restart/retraction/string/atomic rejection passed |
| Two-process native basis-store probe | exclusion, failed-close lock retention, successful release passed |
| `basis90-input` example | data-only load, formation, four arms, snapshot output passed |
| `bash -n`, `git diff --check`, local README links | passed |

The exhaustive basis oracle checked all256 two-node/two-predicate graphs,5 task
words and3 execution arms:3840 native answer-table comparisons, zero mismatches.
Other inherited proof/contract oracles also ran in the offline suite. The native
experiment test covers two formation rounds, no raw/replay fallback on active
execution, forged initial routing, forged definitions/certificates/rewrites,
cyclic/forward dependencies, fuel/limits, retraction, saturation, fresh-process
restoration with identical next proposal and next learned state, failed checkpoint
rollback and changed external file refusal.

The offline runner denies Python socket operations. It is not an OS sandbox, but
all selected child paths are file/native/PTY-only. No HTTP server or GPU/service
was used. The six original web tests were deliberately not run; they start a
loopback HTTP server. A new seeded-cache test covers the web shell without one.

Logs are under `docs/basis90-evidence/`. `source.sha256` covers working product
sources/tests/scripts and root usage files; historical0088 manifests remain
historical. `SHA256SUMS` binds this report, experiment output and evidence.

## Interpretation — narrower than a latent-axiom theory

- Actual basis calls and changed plans distinguish this from merely archiving a
  proof or appending an unused operator.
- The second basis containing the first is evidence that the implemented formation
  loop can operate on its own earlier representation, in this restricted grammar.
- The learned law is a conservative definition/associative factor, not a new fact
  inferred from web frequency. Logical soundness comes from word equivalence;
  finite oracle agreement only supplements that argument.
- Representation reduction is workload-dependent. Whole-model/audit overhead and
  the memo control prevent interpreting the result as automatic latent compression
  or general acceleration.

## Hypotheses and next experiments

It remains a hypothesis that broader basis invention can yield useful, smaller
CPU inference models. Next experiments should vary task distributions, compare
with the actual legacy learner, profile validation/cover/materialization costs,
include attached checkpoint costs, and attempt safe retirement/replacement of old
bases. Learned selection policies and goal invention are not implemented here.
No broad theory is inferred from the synthetic success case.

## Separate inherited fixes and unresolved boundaries

- Malformed web list/document/state/collection/ingress shapes now fail without
  SIGSEGV; bounded validation and trailing-input rejection are explicit.
- Joint plain relation replay no longer consults a live Ground83 ordering cache.
  Canonical ordering is intentional for that path. Legacy A77 routing still uses
  its callback; previously invalid snapshots are not silently repaired.
- Packaging ignore rules now include generated LLVM/local-store artifacts.
- Native web raw/hash/span integrity verification is **not** newly implemented;
  the Python cache validator remains separate. The acquisition-to-native-learning
  bridge and robust truncated-HTTP handling remain future work. No online trial
  was attempted.
- Core/audit are separate fields in one file, not a content-addressed storage
  redesign. Restore is still bounded synchronous replay; no fsync guarantee.
- Basis definitions accumulate; only active work plans are replaced. There is no
  global basis deletion/reconstruction, arbitrary free-text semantics, trained
  Transformer-style attention, gradient learning or cross-logic unification.

A hash comparison after work found203 selected product files still identical
between0088 and0089; [predecessors.json](basis90-evidence/predecessors.json).
The copied native compiler binary still matches0089 exactly. Only the0090
application working version was developed.
