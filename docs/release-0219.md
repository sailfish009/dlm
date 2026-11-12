# Release 0.0219 — Configurable DT Variant Lab

- Date: 2026-11-12
- Predecessor: 0.0216 (array-view C/LLVM backend)
- Type: candidate research release
- Runtime: built from this tree, `20261112T074700Z-25761`

## What changed

- Added `experiments/dt_full_port_no_mlir/`:
  - full DT-1 selector inference in C/LLVM;
  - C/LLVM training backend (forward/backward/Adam);
  - 10/10 inference pick parity and 10/10 training pick parity.
- Added `experiments/dt_variant_lab/`:
  - config → generated C trainer → compile → 10-fold LOCO → comparison;
  - configurable D/F/layers/heads/epochs/lr/posw/prior/weight_decay/dropout/scheduler.
- Fixed `variant_lab.py` to use the local copied tree rather than an absolute
  v0.0216 path.
- Added `dt_configurable_variant_lab` capability ledger entry.

## Variant results

```text
baseline            10/10
d16_f32_l3          10/10
d32_h2_l6           10/10
d16_h2_l3           10/10
d32_h4_l6            9/10
d32_adamw_cos        9/10
d32_dropout          9/10
d32_f64_l6_noprior   4/10
d32_f64_l3           9/10
```

## Verification

```bash
cd /research/dlm_v0.0219
./scripts/verify_release.sh
```

and:

```bash
cd /research/dlm_v0.0219/experiments/dt_variant_lab
./run_lab.sh
```

Expected lab gate: `V0219-VARIANT-LAB-PASS`.

## Scope

- Training is C/LLVM float64; proof remains Maru.
- MLIR is not used or claimed.
- Maru array-view wrapper for the DT selector is still deferred.
