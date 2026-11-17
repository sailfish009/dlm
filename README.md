# DLM 0.0262 — minimal deductive core + hybrid reasoning layer (DP value labels)

**0.0262** replaces the single-step utility label with a **budget-exact DP value**
`V(mask, rem) = max(P(mask), max_c V(mask∪{c}, rem−1))`, computed from the kernel
closure with memoisation and audited against an independent brute-force
enumeration (24 checks, 0 mismatches). 5 seeds, fresh base 31–35, d4/b4:

```text
arm      dfs     dfs_full  note
util     0.5095  0.4340    single-step utility
dp       0.5318  0.4560    exact DP value  -> +2.2pp goal +-2.8 (inside 2SE)
dpshuf   0.1746  0.1660    same label multiset, shuffled (labels are used: -35.7pp)
dplem    0.6540  0.6080    dp + hand-mined contracts (+12.2pp over dp)
```

**DP-VALUE-NOT-DEMONSTRATED**: an oracle-grade value label does not substitute
for the missing learning signal at 19,939 parameters / 40 epochs; it is +2.2pp on
the DFS split and −4.1pp under beam. The large effect remains the symbolic action
space (contracts), which stacks with the value label (+14.5pp over util).
Details: `docs/release-0262.md`; gates: `verify_value.sh` → `V0262-DPVALUE-PASS`.

# DLM 0.0261 — minimal deductive core + hybrid reasoning layer (contract proposal test)

**0.0261** tests whether the 0.0260 contract gain can be *learned* rather than
hand-designed. Four arms on a fresh seed base (21–25), identical transformer
(19,939 params), identical protocol, identical search, matched contract count:
`pure` / `mined` (teacher-rollout pairs) / `learn` (scorer fitted on **kernel
labels** only, normal equations) / `rand` (matched random pairs).

```text
arm     dfs     dfs_full  pair_uses
pure    0.4683  0.3900    0
mined   0.6302  0.5880    479
learn   0.6778  0.6400    887
rand    0.6841  0.6480    922
```

`learn − rand = −0.6 pp ± 0.7` (5 seeds, inside 2 SE): **PAIR-LEARN-NOT-DEMONSTRATED**.
The contract gain (+16…22 pp) is an action-space effect — 16 structurally valid,
kernel-admissible 2-rule actions per state — and the teacher-mined set was a
*coverage* restriction, not a smarter set. The learning side needs a budget-aware
value target over contract sequences, not a pointwise pair score. Details:
`docs/release-0261.md`. Gates: `verify_pair.sh` → `V0261-PAIRLEARN-PASS`.
Also repaired in this line: the 0.0259 layer-table aggregation (seed-13 row
printed as a 3-seed mean), stale release manifests, a wrapper token that no
lab emitted, a `tail -20 a b` diagnostic that failed on GNU 9.12, the seed-count
dependence of the 0.0251 harness pin, and a latent stack overflow in the 0.0257
lemma action found by the new ASan gate.

# DLM 0.0260 — minimal deductive core + hybrid reasoning layer

**0.0260** continues the 0.0259 layer-substitution experiment in
`experiments/proof_state_transformer_maru/` with reasoning layers borrowed from
proof engineering, all ablatable on the same 19,939-parameter native model:
Rocq (independent proof certificates, obligation focus), Silicon (kernel path
condition, verified 2-rule contracts) and Screamer (sparse top-k attention,
branch/backtrack/propagation/subsumption). Measured on the hard fixture
(d4/b4, 3 seeds): verified contracts +13.0 pp goal / +16.0 pp full over the
unmodified transformer, hybrid +15.1 pp / +18.0 pp; top-k attention, the soft
residual gate and obligation focus are neutral-to-negative on this fixture
(focus is vacuous: the relevance closure saturates). Gates:
`experiments/proof_state_transformer_maru/verify_hybrid.sh` →
`V0260-HYBRID-PASS`. Details: `docs/release-0260.md`. 0.0259's review
(`/research/code-review-0259.md`) found the layer table printed the seed-13 row
as a 3-seed average and the release gate failing on stale manifests; both are
repaired here (per-seed aggregation with a mutation regression, regenerated
manifests, wrapper token matches, new lab inside the release gate). The 0.0260
ASan gate also found a latent stack overflow in the 0.0257 lemma action (two
rules written into an array sized for one per slot), now fixed.

# DLM 0.0256 — minimal deductive core + native-search soundness repairs

This is the **minimal-core lineage** of DLM on Maru, extended with the v0.0216
array-view C/LLVM backend, the v0.0237 transformer graph/LLVM variant matrix,
the v0.0238 M0–M5 roadmap, the v0.0243 native integral-credit lab
(`experiments/native_integral/`), and the v0.0244 native proof-state transformer
lab (`experiments/proof_state_transformer_maru/`). It keeps the trusted symbolic kernel, proof
gate, basis/axiom layer, and the DT proof-state dialect. It intentionally removes
the older `d107-*` contract layer (see below).

```text
facts / observations
→ Horn closure + proof term + independent checker
→ basis axioms / axiom graph / proof-credit frontier
→ DT proof-state dialect (mdmodule / mdop / verify)
→ optional web / NL / recursive self-supervision boundaries
→ C/LLVM array-view backend (indexed join, v0.0216)
```

## Core modules

```text
src/dlm/logic.l          lists, terms, atoms, substitution
src/dlm/infer.l          clauses, unification, forward inference
src/dlm/deduce.l         closure, proof terms, proof checker
src/dlm/fragment.l       fragments/templates
src/dlm/assemble.l       composition
src/dlm/match.l          pattern matching
src/dlm/typed.l          typed admission
src/dlm/proof.l          p-prove / p-proof-check
src/dlm/synth.l          checked synthesis
src/dlm/basis.l          basis axioms, activation, rollback, CSE
src/dlm/axiom.l          axiom store and subset selection
src/dlm/axiom-graph.l    axiom DAG, DCE/CSE, selection
src/dlm/dtir.l           DT proof-state dialect
src/dlm/mlir.l           MLIR-shaped internal form
src/dlm/graph-ir.l       graph IR
src/dlm/nl.l             NL boundary (parse/build/answer)
src/dlm/web.l            observation/web boundary
src/dlm/selfssl.l        recursive self-supervision
src/dlm/repl.l           REPL / driver surface
```

## Run

```sh
./scripts/run.sh repl                 # original Maru REPL
./scripts/run.sh experiment           # fragment experiment
./scripts/run.sh mlir                 # MLIR-shaped experiment
./scripts/run.sh typed                # typed experiment
./scripts/run.sh synth                # synthesis experiment
./scripts/run.sh proof DRIVER         # proof driver
./scripts/run.sh test                 # native core assertions
```

## Verify a release

```sh
./scripts/verify_release.sh
```

This checks:

- `VERSION`, `docs/release.txt`, and the `maru-compiler` symlink agree;
- `capabilities.json` version equals `VERSION`;
- release sources and the release-gate path import no torch (`NATIVE-SCOPE-PASS`,
  scope in `docs/native-scope-0243.md`, torch snapshots pinned in
  `docs/research-snapshots.sha256`);
- no unapproved file larger than 5 MB outside `runtime/`;
- the headline lab gate (`experiments/native_integral/run_all.sh` →
  `V0243-NATIVE-INTEGRAL-PASS`);
- `./scripts/run.sh test` (`ALL-CORE-TESTS-PASSED`);
- `./scripts/compiler.sh verify <release-id>` (self-host `Verified`).

## Native integral-credit lab (0.0243)

`experiments/native_integral/` is the native (C/LLVM IR + Maru oracle, no
Python/torch) integral-credit composition lab. 0.0243 repairs the 0.0242
protocol after review: data/compute-matched memoryless baseline, randomized
tie-break (no hidden index prior), exact-credit control, measured estimation
error, paired significance + bootstrap CI over 12 seeds, and Maru parity on
generated 40-atom worlds.

```text
accumulated participation prior  40.81%   (12-seed mean)
memoryless / no learning         12.13%
single-episode policies (n=100)  13.45% mean, 23.39% max
full-budget ("exact") credit     43.73%
hand-written structural oracle   40.43%
online composition feedback      40.28%  (unstable: -5.85pp on one seed)
```

Accumulation is the driver (+28.7pp, paired z ≥ 1900 and bootstrap CI excluding
0 on all 12 seeds). 0.0242's "noise is what makes the integral work" framing is
retracted: exact credit accumulates better. At this scale the integral is an
empirical prior over rule participation, not a proof-path or order-non-integrable
integral. See `docs/release-0243.md` and the lab README.

## Research snapshots

The release includes code-only snapshots of:

```text
experiments/tiny_transformer_maru/          Q16 transformer inference port
experiments/deductive_transformer_maru/     DT × MNIST learning/eval
```

Snapshots that import torch are outside the native release scope, are not in
`docs/release.sources.sha256`, and are pinned in
`docs/research-snapshots.sha256` (see `docs/native-scope-0243.md`). The 0.0239
`structure_discovery` and 0.0241 `integral_learning` PyTorch labs were removed
in 0.0243 as superseded by `native_integral`; they remain in their own
worktrees.

Large data (`mnist.npz`), checkpoints, generated weights, and per-run logs are
intentionally excluded. Regenerate them with the READMEs/scripts in each
experiment before running the research verifiers.

The DT × MNIST result is **research**, not a core claim:

```text
baseline Maru perceptron:        8/10, proof 10/10
validated rule library:          9/10, proof 10/10
label-free support/conflict:     8/10 (negative)
case 0 ceiling: perception + no head-5 valid rule
```

Training uses MNIST labels as observations; it is observation-supervised and
proof-gated, not label-free deductive learning.

## Configurable DT variant lab (0.0219)

`experiments/dt_variant_lab/` generates variant-specific C/LLVM trainers from a
config (`D`, `F`, `layers`, `heads`, optimizer/prior settings), compiles them,
runs 10-fold training, and compares held-out picks against the v0.0218
reference.

```text
baseline / d16_f32_l3 / d32_h2_l6 / d16_h2_l3  → 10/10
```

See `experiments/dt_variant_lab/README.md`.

## Array-view backend (0.0216)

The 0.0216 addition is a reusable C/LLVM primitive path:

```text
Maru memory-block
→ array-view ABI (data, length, stride, elem-size)
→ persistent index
→ C indexed join / checksum
→ VM primitive
```

See `experiments/array_view_join_maru/` and `docs/release-0216.md`.

## Removed in 0.0205

The `d107-*` contract layer from 0.0120 is **not part of this tree**:

```text
no src/dlm/d107-*.l
no tests/test_d107.py
no d107 contract/unit/surface/plan/session modules
```

This is an intentional breaking change: 0.0205 is the minimal proof/axiom/DT
core, not a superset of 0.0120. Historical 0.0120 documentation is kept under
`docs/README-0120.md` and `docs/release-0116.md` for reference only.

## Limits

- No dense tensor/attention ops in the trusted core.
- Web acquisition remains a boundary experiment; web text is not truth.
- Numerical/embedding components only rank; proof remains the truth gate.
- Research snapshots are not part of the core test suite.
- No promotion of any unpublished runtime beyond the recorded release.
