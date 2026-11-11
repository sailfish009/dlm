# Release 0.0164 — three-fact chain synthesis (candidate)

- Date: 2026-11-08
- Predecessor: 0.0163. Candidate, not promoted.
- Scope: extend frontier synthesis beyond two-fact composition to a three-fact
  chain, with coverage ranking, negative check, and held-chain transfer.
- Analysis: `/research/analysis-synth-chain-0164.md`.

## Changes

`src/dlm/synth.l`:

- `s-chain3-candidates` — find `P(a,b), Q(b,c), S(c,d)` connecting the target
  endpoints and synthesize `R(x,w) :- P(x,y), Q(y,z), S(z,w)`
- `s-chain-synthesize` — rank three-fact candidates by training-positive coverage
  with zero negative conflict

## Experiment

`scripts/synth_chain.sh`:

```text
TWO_FACT_CANDIDATES 0
THREE_FACT_CANDIDATES 1
SYNTH rule support=(a0 a1 a2)
COVERAGE 2/2
NEGATIVE clean
HELD proof
FROZEN fail
```

The two-fact candidate space cannot explain the target; the three-fact chain
does. The synthesized rule covers both training positives and transfers to a
held chain.

## Self-host

```text
compiler.sh reproduce
→ 20261109T080154Z-535
compiler.sh verify 20261109T080154Z-535
→ Verified
```

Verify includes core, MLIR, typed, proof, synthesis, ranked synthesis, chain
synthesis, and next/third equality. Only benign clang target-triple warnings.

## Measured

```text
native normal   18 checks / 0 FAIL
native safety-2 18 checks / 0 FAIL
self-host       verified
```

## Still not

- Chain length is fixed at 3; no general path/ILP search.
- Fixed tasks/alignments; no new predicate invention.
- Coverage-first ranking; no MDL/cost/independence.
- Provenance remains fact-ID support.
- Not label-free self-supervision.
