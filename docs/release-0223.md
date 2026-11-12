# Release 0.0223 — Deductive Learning Mechanism Discovery

- Date: 2026-11-12
- Predecessor: 0.0222
- Type: candidate research release
- Runtime: `20261112T092235Z-18872`

## What changed

- Added `experiments/deductive_mechanism_lab/`:
  - proof-frontier signature mechanism (no fact-pair enumeration);
  - axiom-store admission;
  - retraction;
  - fact-permutation invariance;
  - frontier-missing-atom acquisition;
  - content-scramble control.
- The candidate shape is derived from the failed proof frontier's
  predicate/arity, not from enumerating example pairs.
- The acquired premise is the frontier's `missing107` atom, labeled
  synthetic/acquired, not hardcoded by name.

## Results

```text
M2 BEFORE 1/3 AFTER 3/3 LEARNED 1
M2 SOURCE frontier-signature ENUMERATED false
M3 FRONTIER (missing107 (atom isa (MNIST pixel-grid))) ACQ acq-frontier HELD0 1/2 HELD1 2/2
RETRACT 1/3 PERMUTE 3/3 SCRAMBLE 0/3
NEG 0 ACQ-TIER synthetic
```

## Verification

```bash
cd /research/dlm_v0.0223/experiments/deductive_mechanism_lab
./pipeline.sh
```

and:

```bash
cd /research/dlm_v0.0223
./scripts/verify_release.sh
```

## Limits

- The composition schema is selected from frontier signature/arity; this is a
  mechanism probe, not a general schema-invention proof.
- Acquisition uses the frontier atom itself as a synthetic/acquired hypothesis.
- DT is not part of this loop; MLIR not used.
