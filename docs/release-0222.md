# Release 0.0222 — Closed-Loop Transitivity + Acquisition

- Date: 2026-11-12
- Predecessor: 0.0221
- Type: candidate research release
- Runtime: `20261112T084828Z-17591`

## What changed

- Added same-predicate transitivity candidates to `src/dlm/synth.l`:
  - `s-trans-candidates`
  - `s-trans-synthesize`
- Added `experiments/transitivity_acquisition_lab/`:
  - initial failure detection;
  - `s-trans-synthesize` on failed goals;
  - kernel admission and re-evaluation;
  - need-driven acquisition of the residual bridge fact;
  - content-scramble control.

## Result

```text
WEB 8 FACTS 6 RULES0 2
BEFORE 1/3 FAILED 2
LEARNED 1 RULES1 3
AFTER 3/3 HELD0 1/2 HELD1 2/2
NEG 0 SCRAMBLE 0/3
PROV-ACQ synthetic BRIDGE acq-bridge
```

The transitivity rule is induced by the system, not hand-added. The residual
held failure is resolved by an explicitly synthetic/acquired bridge fact.

## Verification

```bash
cd /research/dlm_v0.0222/experiments/transitivity_acquisition_lab
./pipeline.sh
```

```text
V0222-CLOSED-LOOP-TRANSITIVITY-ACQUISITION-PASS
```

Release:

```bash
cd /research/dlm_v0.0222
./scripts/verify_release.sh
```

## Limits

- Bridge is synthetic/acquired, not fetched.
- DT is not part of this learning loop.
- MLIR not used.
