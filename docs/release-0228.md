# Release 0.0228 — Integral Transformer Variant Matrix

- Date: 2026-11-12
- Predecessor: 0.0227
- Type: candidate research release
- Runtime: `20261112T105830Z-31151`

## What changed

- Added `experiments/integral_transformer_matrix/`:
  - compile-time integral variants of the existing C/Q16 DT transformer;
  - integral attention (trapezoidal value integration);
  - integral layernorm (cumulative mean);
  - integral block (half-step residual integration);
  - E00–E07 factorial matrix;
  - shell-only gate.

## Result

```text
E00-E07 PICKS UNCHANGED
E00 selector 3.378845215
E01 selector 3.270996094
V0228-INTEGRAL-TRANSFORMER-VARIANT-MATRIX-PASS
```

Integral variants change selector magnitudes but not the 10-case picks on this
fixture. This is a neutral/negative result for generalization claims.

## Verification

```bash
cd /research/dlm_v0.0228/experiments/integral_transformer_matrix
./run_matrix.sh
./verify.sh
```

and:

```bash
cd /research/dlm_v0.0228
./scripts/verify_release.sh
```

## Limits

- Integral credit and proof-path integral are deferred.
- No training variants; static inference fixtures.
- Picks are insensitive on this 10-case fixture.
- No MLIR.
