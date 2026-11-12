# Release 0.0220 — Hardened DT Variant Lab + Prior-Saturation Gate

- Date: 2026-11-12
- Predecessor: 0.0219
- Type: candidate research release
- Runtime: `20261112T081459Z-17277`, built from this tree.

## Fixes

- Eval-time dropout removed from `predict()`; training now uses inverted
  dropout scaling.
- Cosine scheduler uses a global scheduler step while Adam bias correction
  resets per fold.
- `T = MAXV + 1` with a compile-time assertion.
- `L2_W` initialization uses `sqrt(F)`, not `sqrt(64)`.
- Loss denominator uses `RULE_COUNT`.
- Variant generator fails closed on unsubstituted template fragments.
- `verify_lab.py` checks 10 picks per variant, seed variants, no-prior, a
  prior-only control, ground-truth accuracy, and eval-dropout absence.
- Added a prior-only probe; on this fixture it reaches 9/10 parity and 8/10
  ground-truth accuracy, equal to the full DT. The fixture is prior-saturated.

## Variant results

```text
baseline            10/10  acc 8/10
baseline_seed62     10/10  acc 8/10
baseline_seed63      9/10  acc 8/10
d16_f32_l3          10/10  acc 8/10
d32_h2_l6           10/10  acc 8/10
d16_h2_l3           10/10  acc 8/10
d32_h4_l6            9/10  acc 8/10
d32_adamw_cos        9/10  acc 8/10
d32_dropout          9/10  acc 8/10
d32_f64_l6_noprior   4/10  acc 3/10
d32_f64_l3           9/10  acc 7/10
prior-only           9/10  acc 8/10
PRIOR_SATURATED yes
```

## Verification

```bash
cd /research/dlm_v0.0220
./scripts/verify_release.sh
```

```bash
cd /research/dlm_v0.0220/experiments/dt_variant_lab
./run_lab.sh
```

Expected: `RELEASE-VERIFY-PASS version=0.0220 ...` and
`V0220-VARIANT-LAB-HARDENED-PASS`.

## Scope

- C/LLVM training; proof remains Maru.
- No MLIR.
- Maru array-view wrapper for the DT selector remains deferred.
- The current fixture is prior-saturated; a harder fixture is required for
  meaningful variant comparisons.
