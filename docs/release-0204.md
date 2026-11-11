# Release 0.0204 — DT verifier barrier (candidate)

- Date: 2026-11-10
- Predecessor: 0.0203. Candidate, not promoted.
- Scope: require a `verify` op in the DT proof-state module; a module without it
  is rejected before selection/proof.
- Analysis: `/research/analysis-dtir-verifier-0204.md`.

## Changes

`src/dlm/dtir.l`:

```text
dt-check   requires a verify op
dt-run     rejects modules that fail dt-check
```

## Experiment

```text
DT name=dt1 selected=(A-0 A-1) cov=3 proof=proof
BAD (rejected107 dt-verifier-missing) RUN (rejected107 dt-verifier-missing)
done-dtir
```

The valid module selects atomic axioms and proves the goal. The module without
`verify` is rejected before any selection/proof.

## Self-host

```text
compiler.sh reproduce
→ 20261110T122143Z-8395
compiler.sh verify 20261110T122143Z-8395
→ Verified
```

## Measured

```text
native normal   68 checks / 0 FAIL
native safety-2 68 checks / 0 FAIL
self-host       verified
```

## Still not

- verifier requirement is semantic convention, not an MLIR pass
- no tensor/attention ops
- no looped proof block
- no equivalence between DT behavior and transformer teacher
- truth remains with the proof checker
