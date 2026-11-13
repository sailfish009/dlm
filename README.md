# DLM 0.0242 — minimal deductive core + native integral-credit composition

This is the **minimal-core lineage** of DLM on Maru, extended with the v0.0216
array-view C/LLVM backend, the v0.0237 transformer graph/LLVM variant matrix,
the v0.0238 M0–M5 roadmap, and the v0.0239 structure-discovery lab (P0 fixture
qualification + P1 direction-aware structural variants on proof-state worlds). It keeps the trusted
symbolic kernel, proof gate, basis/axiom layer, and the DT proof-state dialect.
It intentionally removes the older `d107-*` contract layer (see below).

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
- no unapproved file larger than 5 MB outside `runtime/`;
- `./scripts/run.sh test` (`ALL-CORE-TESTS-PASSED`);
- `./scripts/compiler.sh verify <release-id>` (self-host `Verified`).

## Research snapshots

The release includes code-only snapshots of:

```text
experiments/tiny_transformer_maru/          Q16 transformer inference port
experiments/deductive_transformer_maru/     DT × MNIST learning/eval
```

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
