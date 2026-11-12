# Release 0.0229 — Proof-Path Integral Rebuild + Prior-Decorrelated Matrix

- Date: 2026-11-12
- Predecessor: 0.0228
- Type: candidate research release
- Runtime: `20261112T112126Z-9526`

## What changed

- Rebuilt the proof-path integral probe with two **distinct ground rules**,
  different path costs, and cost-weighted credits.
- Added a prior-decorrelated inference matrix: E00–E07 with `PRIOR_WEIGHT=0`.
- Added shell-only gates for both.

## Proof-path result

```text
DISTINCT-RULES true
PATHS 2 OK1 1 OK2 1
COSTS 2 3 WEIGHTS 21845 16384 Z 38229
CREDITS 37448 28087 (not 1/count)
SINGLE-RULE-INDEX 0 NEG 0 (want 0)
```

The credits are cost-weighted, not `1/path_count`.

## Prior-decorrelated matrix

```text
PRIOR0-BASELINE 211 154 2 22 61 61 34 76 125 5
E01 211 154 2 131 170 170 34 76 125 5
E02 211 154 2 131 61 170 34 76 125 5
E03–E07 211 154 2 131 170 170 34 76 125 5
```

With the prior removed, integral attention/norm/block variants change picks.
This is the first matrix where integral component choices are discriminative.

## Verification

```bash
cd /research/dlm_v0.0229/experiments
./run_all.sh
```

and:

```bash
cd /research/dlm_v0.0229
./scripts/verify_release.sh
```

## Limits

- The proof-path probe has two ground paths and fixed cost formula.
- The prior-decorrelated matrix is inference-only; no training credit coupling.
- Picks change, but accuracy improvement is not claimed.
- No MLIR.
