# Release 0.0165 — bounded four-fact chain synthesis (candidate)

- Date: 2026-11-08
- Predecessor: 0.0164. Candidate, not promoted.
- Scope: replace the fixed three-fact synthesis with a bounded chain walker that
  finds a four-fact rule when shorter candidates cannot reach the target.
- Analysis: `/research/analysis-synth-long-0165.md`.

## Changes

`src/dlm/synth.l`:

- `s-walk-candidates` — bounded chain walk (length 2..4) using shared variables
- `s-long-synthesize` — combine 2/3/4-fact candidates, reject negatives, rank by
  positive coverage then shorter body

## Experiment

`scripts/synth_long.sh`:

```text
C2 0
C3 0
C4 1
SYNTH rule body=4 support=(a0 a1 a2 a3)
COVERAGE 2/2
NEGATIVE clean
HELD proof
FROZEN fail
done-long
```

The four-fact rule is:

```text
path(x,v) :- hop1(x,y), hop2(y,z), hop3(z,w), hop4(w,v)
```

It covers both training positives and transfers to a held four-hop chain.

## Self-host

```text
compiler.sh reproduce
→ 20261109T080559Z-25061
compiler.sh verify 20261109T080559Z-25061
→ Verified
```

Verify includes core, MLIR, typed, proof, synthesis, ranked, chain3, chain4,
and next/third equality. Only benign clang target-triple warnings.

## Measured

```text
native normal   20 checks / 0 FAIL
native safety-2 20 checks / 0 FAIL
self-host       verified
```

## Still not

- Bounded chain length is 4; no general path/ILP search.
- Fixed tasks/alignments.
- Coverage-first ranking; no MDL/cost/independence.
- Provenance remains fact-ID support.
- Not label-free self-supervision.
