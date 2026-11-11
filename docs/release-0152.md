# Release 0.0152 — versioned evidence-carrying axiom candidates (candidate)

- Date: 2026-11-08
- Predecessor: 0.0151. Candidate, not promoted.
- Scope: store learned rule programs as versioned axiom candidates with
  evidence/support, and activate/deactivate/rollback their inference effect.
- Analysis: `/research/analysis-axiom-lifecycle-0152.md`.

## Changes

New `src/dlm/d107-axiom.l`:

```text
(axiom107 ID RULES EVIDENCE SUPPORT VERSION STATUS HISTORY)
```

- axiom starts `inactive` at version 0;
- activate/deactivate increments version and appends history;
- rollback restores the previous history entry;
- `p107-axiom-active-rules` exposes only active rules to inference;
- evidence and support lists are retained with the axiom.

The axiom never asserts truth by itself; activation only makes its checked
rules available to the existing kernel.

## Experiment

`experiments/axiom_lifecycle/`: a recursive ancestor program is learned from
web-grounded claims, stored as an axiom with 7 evidence entries and 2 support
atoms.

| state | active rules | answer rows |
|---|---:|---:|
| active | 2 | 1 |
| inactive | 0 | 0 |
| rollback to active | 2 | 1 |

After deactivate→rollback, version returns to 1 and status to `active`.

## Measured

```text
native normal   371 ok / 0 FAIL
native safety-2 371 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Axioms are in-memory; no persistent axiom store.
- Evidence is a list, not per-rule/per-step provenance.
- Activation is explicit; no autonomous promotion policy.
- No independence/minimality/consistency check between axioms.
- No automatic extraction-to-axiom pipeline; the rules are still induced from
  hand-normalized claims.
- No global rollback of dependent proofs/definitions.
