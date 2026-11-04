# Release 0.0094 — cumulative relational basis / EML representation integration

## Outcome

Implemented in `/research/dlm_v0.0094`, copied before implementation from the
actual 0093 working tree. The 0092/0093 directories and their original Git state
are preserved. The compiler/runtime are unchanged.

**The new path uses the existing Basis91 learned state/library and Attention92
execution/admission. It does not introduce another independently trained model.**
Existing bases can be migrated in place to checked EML bodies, used by existing
queries, and reused as constructors in subsequent formation. Controlled
interpretation now feeds its checked plans and original witnesses into the
existing reading/support/proposal/admission path.

This is a representation and learning-lifecycle integration result. It is not
new evidence that arbitrary latent axioms have been discovered, that all past
DLM subsystems are semantically unified, or that EML increases learning power.

## Concrete formation trace

The native demo observes four facts with two `r-s` applications, then:

1. Existing formation learns `B1(x,y,z) = r(x,y) ∧ s(y,z)`.
2. `basis91 encode` changes B1's body in the **same** library to its EML execution
   representation. ID, pattern, variable roles, active views and support remain.
3. A second six-fact source is observed. Attention92 executes the stored B1 while
   interpreting the source; complete independently checked results become readings.
4. The ordinary two-constructor formation rule can now admit
   `B2(x,y,z,w) = B1(x,y,z) ∧ t(z,w)`, with an EML body that calls the existing B1.
5. An ordinary query executes B2→B1 and returns new bindings with original IDs.

The demo's triple query returns `(u v w k)` with IDs `(0 1 2)` and `(j l m n)`
with IDs `(3 4 5)`. Actual called basis IDs are `(2 1)`. Removing the training
learner is not a barrier to frozen-core inference; heldout query cores use new
facts and the same definitions, with no training episodes or answer rows.

EML combines **candidate** predicate values; it is not applied to a pre-solved
full-goal answer table. False candidate rejection and primitive execution counts
are recorded. An unavailable arithmetic primitive produces `unknown`; an omitted
worker table is rejected, not repaired with reference results.

## Implementation changes

Inherited product files changed relative to the actual 0093 copy:

```text
README.md
VERSION
scripts/run.sh
src/dlm/basis91-ir.l
src/dlm/basis91-check.l
src/dlm/basis91-execution.l
src/dlm/basis91-formation.l
src/dlm/basis91-session.l
src/dlm/attention92-ir.l
src/dlm/attention92-execution.l
```

New native modules:

- `src/dlm/basis-eml94.l`: EML-only DAG compiler, typed representation checks,
  exhaustive finite bit certificates, codec installation.
- `src/dlm/basis-eml94-execution.l`: shared scoped worker, independent regular
  query check, and controlled interpretation feeding existing formation.

New experiment/test products: `experiments/integration94/`,
`adapters/integration94_experiment.py`, `tests/test_integration94.py`.
New launch modes are experiment entry points only: `integrate94`,
`integrate94-input`. There is no `integration94-state` or separate checkpoint.

All existing APIs remain available. Historical numeric `eml93` is preserved but
its separate empirical library/source maps are not promoted into logical truths.

## Validation

| Check | Result |
|---|---|
| Full offline Python suite | **238 passed**, 906.933 s |
| Separate new integration suite | **25 passed**, 233.782 s |
| Excluded legacy local HTTP tests | 6; not run |
| Native suite | passed |
| Store / runtime / graph-store suites | passed |
| Binding/witness oracle | **6,144 complete checks**, 0 mismatches |
| EML finite bit-domain oracle | **28 cases**, 0 mismatches |
| Malformed-tree probe | 400 trees, no validator crashes |
| Additional large workspace | **343 rows**, encoded basis actually called |
| Example and stdin paths | byte-identical output |

The graph oracle covers all 256 subsets of a selected eight-fact/two-node
universe, six patterns, two native paths and two branch contexts. This is not
exhaustion of all graphs allowed by the larger IR bounds. Python assignment
enumeration checks exact original witness IDs, not only final row counts.

The 28 circuit cases exhaust all 1/2 inputs for 1–3 leaf slots under both branches.
An independent `cmath` evaluator checks arithmetic and positive operand domains.
Maximum complex absolute error is **0.00013200000000246348**; decoder tolerance is
max-component 0.002. This is a complete finite interface check, not a uniform
error bound for arbitrary complex EML programs. The branches agree here because
the reachable logarithm operands are positive; negative-axis behavior is not
redefined or claimed solved.

Other tests cover mixed legacy/EML prefixes, already hierarchical library
migration, role aliases/cycles/forks/shared targets, changed code or metadata,
unsupported branches, insufficient fuel, partial-scope widening, arithmetic
failure, omitted workers, read-only proposals, archive-free inference, replay
forgery, fresh-process continuation, lock exclusion, checkpoint rejection and
failed-close retention. Independent paths share some legacy binding/validation
utilities; Python oracles supply additional independent finite evidence, not a
formal proof of the entire runtime.

## Fresh-process experiment

**56 sequential native workload processes**, plus one separate arithmetic probe.
Four fixed families (chain/fork/common target/cycle), two observation-order/entity-
rename/query seeds, two explicit branches. Each process receives 24 new finite-
source queries with shuffled facts, varied role labels and atom order. Main arms
have 16 runs each; each causal control has 8 runs at seed 0.

| Arm | Runs | Bases after later formation | Complete queries | Unknown | Mismatches among complete |
|---|---:|---:|---:|---:|---:|
| Ordinary logical bodies | 16 | 2 | **384** | 0 | 0 |
| Integrated EML bodies | 16 | 2 | **384** | 0 | 0 |
| No initial prefix formation | 8 | 1 | 192 | 0 | 0 |
| No later interpretation feedback | 8 | 1 | 192 | 0 | 0 |
| Encoded Attention92 worker disabled | 8 | 1 | 34 | **158** | 0 |
| **Total** | **56** | — | **1,186** | **158** | **0** |

Total attempted queries: **1,344**; pending: **0**. Unknowns are not counted as
correct outputs. All 158 occur in the deliberately disabled-worker control.
Its 34 completed queries use primitive operators selected by the original
controller before any failed encoded call; they are not repaired EML results.

For each main-arm pair, the report checks identical source/query data and equal
learned logical patterns. The EML arm changes executable representation, not the
meaning of those definitions. No heldout answers or reference function bodies
enter formation, and heldout queries do not mutate the learner.

### What the controls do and do not establish

- Without the initial prefix, a three-atom pattern is not a two-constructor
  candidate at that subsequent step. A smaller basis forms instead. More steps
  can recover the larger definition; the ablation removes an initial learning
  step and is **not** an equal-total-computation or impossibility comparison.
- Without committed interpretation feedback, later support/readings are absent,
  so no second basis forms. Merely observing or displaying an application is not
  enough to change formation.
- Disabling the encoded worker makes later controlled interpretation fail
  atomically. It cannot fabricate successful readings or a second basis.
- All ordinary-logical and EML main queries agree. The logical control learns
  the same bases. These results establish a connected path, **not an EML-specific
  improvement in expressiveness, generalization or discovery**.
- Raw relation reasoning could already answer these tasks. Even controls with
  one basis often return all answers: changed learned organization is distinct
  from acquisition of previously impossible answers.

## Cost, not a speed claim

Whole-process median seconds over four runs per family/main arm:

| Family | Logical bodies | EML bodies | Logical core JSON bytes | EML core JSON bytes |
|---|---:|---:|---:|---:|
| Chain | 1.5397 | 3.2563 | 1,417 | 2,807–2,815 |
| Fork | 1.5427 | 3.2640 | 1,417 | 2,807–2,815 |
| Common target | 1.5865 | 3.2828 | 1,550 | 2,940–2,948 |
| Cycle | 1.4955 | 2.2393 | 1,542 | 2,932–2,940 |

Across main EML runs: **2.0841–3.5627 s**. These include native startup/modules,
formation, representation admission, replay validation, 24 queries and output,
but not Python oracle checking or attached checkpoint I/O. Benchmarks were run
after regression/native suites finished, not concurrently with test jobs.

A separate fresh small demo takes **1.4964 s**, child peak RSS **18,896 KiB** on
this host. RSS includes the full native process; JSON bytes are a serialization
proxy, not learned parameter count or native heap size. The compiler emits
0/20/36 EML nodes for 1/2/3 leaf circuits; two-constructor learned bases each use
20 nodes. Definitions may share runtime code objects but serialized structures
repeat that code; no compression/parameter-count advantage is claimed.

The EML representation is **slower and larger here**. This revision prioritizes
correct placement in the cumulative learning system, not beating a direct
logical conjunction with numerical arithmetic. Fuel/diagnostic counters do not
account for every numeric series instruction, allocation or validation step.

## Limits and remaining work

- Fixed compilation grammar for positive conjunctions; the EML circuit algebra
  itself is not freely learned. Source data chooses role/operator/prefix
  structure through the existing learner.
- A conservative definition is not a discovered primitive world axiom.
  No quantified negative/general recursive semantic learner is established.
- Predicate membership in a finite fact view is not world-level negation.
  Missing, partial, undefined and exhausted states remain distinct.
- The shared path covers the relational Basis91/Attention92 subsystem; the whole
  historical collection of DLM representations is not yet unified.
- No automatic free-text/web meaning extraction, noisy-data structure repair,
  general condition invention, arbitrary numerical-basis import or laptop-scale
  long-term growth demonstration.
- Existing native web integrity/truncated-HTTP issues remain inherited.
- Frozen contexts are historical, not automatically revoked on live retraction.
  Logical epoch counts definitions, not representation revisions; use the full
  model/audit, not epoch alone, to identify an exact encoding context.
- Replay is not cryptographic origin authentication; storage has no fsync or
  power-loss recovery guarantee.

## Preservation and evidence

Actual inventories at the version boundary: **498 files in 0092**, **532 files in
0093**. 0092 was clean; 0093's modified/untracked state was copied and preserved.
These current counts override historical manifests referring to owner-removed
archives. Both file contents and Git status are checked again at the end.

Compiler SHA256:

```text
2cbe804829509f5386933d832cbba2fef1bad367b7510a543b5d3f5818136fc9
```

No commit/reset of user Git state was performed. All changes are in 0094.

- [Design and reproduction](integration94-design.md)
- [Experiment JSON](integration94-experiment.json)
- [Demo](integration94-demo.sexp) / [stdin demo](integration94-input-demo.sexp)
- [Failure/scope/retraction/343-row interventions](integration94-interventions.sexp)
- [Evidence, logs and manifests](integration94-evidence/)
- [Preservation check](integration94-evidence/preservation.json)
- [Final checks](integration94-evidence/final-checks.json)
