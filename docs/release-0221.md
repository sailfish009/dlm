# Release 0.0221 — MNIST Web-Axiom Accumulation Pipeline

- Date: 2026-11-12
- Predecessor: 0.0220
- Type: candidate research release
- Runtime: `20261112T082709Z-18619`

## What changed

- Added `experiments/mnist_web_axiom_lab/`:
  - cached MNIST-related web observations with URLs/provenance;
  - two-batch web accumulation;
  - observation → facts/rules → axioms;
  - CSE/minimal-subset/provenance controls;
  - no-web / single-page / shuffled-web controls;
  - DT inference and training gates from the v0.0220 C/LLVM backend.
- The web axiom pipeline and the C DT training are **not yet coupled**: the
  pipeline reports this explicitly (`WEB_AXIOM_DT_COUPLING none`).

## Results

```text
WEB OBS 8 ACCUM1 4 ACCUM2 8
FACTS 6 RULES 2 AXIOMS 2 ACTIVE 2 PROV 2
GRAPH ok CSE 2 NEG 0 (want 0)
BASE 1/3 HELD 0/2
NOWEB 0/3 SINGLE 0/3 SHUF 1/3
MINIMAL (agsel (ax-1) 1)
DT-FULL-INFER-C-PASS
DT-TRAIN-C-PICK-PARITY-PASS
WEB_AXIOM_DT_COUPLING none
V0221-MNIST-WEB-AXIOM-PIPELINE-PASS
```

## Verification

```bash
cd /research/dlm_v0.0221/experiments/mnist_web_axiom_lab
./pipeline.sh
```

and:

```bash
cd /research/dlm_v0.0221
./scripts/verify_release.sh
```

## Limits

- Web observations are cached representative text, not a live fetch.
- The web-derived symbolic axioms are not yet used as DT training features.
- The MNIST DT result is the v0.0220 reference parity, not an improvement from
  web axioms.
- Proof remains Maru; MLIR is not used.
