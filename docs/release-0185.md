# Release 0.0185 — accumulated basis axioms (candidate)

- Date: 2026-11-08
- Predecessor: 0.0184. Candidate, not promoted.
- Scope: keep data-driven rule learning independent of NL, accumulate learned
  programs as versioned basis axioms, and activate/deactivate/rollback them for
  proof.
- Analysis: `/research/analysis-basis-0185.md`.

## Architecture

```text
data / observations
  → synth candidate rule programs
  → basis axiom (rules + evidence + support + version + status)
  → active rules
  → p-prove / p-proof-check
  → answer
```

NL is a separate boundary layer:

```text
English sentence / question
  → nl-parse / nl-build
  → p-prove
  → English answer
```

The basis layer does not depend on NL.

## Changes

New `src/dlm/basis.l`:

```text
b-axiom ID RULES EVIDENCE SUPPORT VERSION STATUS HISTORY
b-add
b-activate / b-deactivate / b-rollback
b-active-rules / b-active-ids
b-find / b-status / b-version
```

`scripts/run.sh` loads `basis.l` after `synth.l`.

`experiments/basis_repl/` + `scripts/basis.sh`.

## Experiment

```text
A status=active ...          (recursive reach program active)
A proof=proof
B proof=proof                (pair path program active)
B OFF path=fail reach=proof  (B deactivated; A remains)
B ROLLBACK status=active path=proof
done-basis
```

Two independently learned programs accumulate in one basis. Deactivating B
removes only its inference effect; A remains. Rollback restores B.

## Self-host

```text
compiler.sh reproduce
→ 20261110T005004Z-23861
compiler.sh verify 20261110T005004Z-23861
→ Verified
```

## Measured

```text
native normal   55 checks / 0 FAIL
native safety-2 55 checks / 0 FAIL
self-host       verified
```

## Still not

- Basis is in-memory; no persistent axiom file.
- Decomposition currently means learned rule programs → rules/axiom, not full
  fragment-level decomposition of observations.
- No automatic promotion policy or cross-axiom consistency check.
- `nl-run` still builds its own small KB at the boundary; it is not yet routed
  through the basis store.
- Proof remains the truth gate.
