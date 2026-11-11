# Release 0.0153 — persistent axiom store (candidate)

- Date: 2026-11-08
- Predecessor: 0.0152. Candidate, not promoted.
- Scope: persist axiom candidates with rules, evidence, support, version, status
  and history; reload them in a fresh process.
- Analysis: `/research/analysis-axiom-persistence-0153.md`.

## Changes

`src/dlm/d107-axiom.l`:

- `p107-axiom-snapshot` / `p107-axiom-snapshot?`
- `p107-axiom-save` writes `(dlm-axiom107 1 store)` and verifies read-back.
- `p107-axiom-load` validates the stored snapshot.
- Evidence/support/version/status/history survive the round-trip.

## Experiment

`experiments/axiom_persistence/`: three processes.

```text
1. create active axiom (version 1, evidence 2), save
2. load, prove, deactivate (version 2), save
3. reload, check status/version/evidence and answer
```

| step | status | version | evidence | answer rows |
|---|---|---:|---:|---:|
| save | active | 1 | 2 | — |
| load+active | active | 1 | 2 | 1 |
| deactivate+save | inactive | 2 | 2 | 0 |
| reload | inactive | 2 | 2 | 0 |

## Measured

```text
native normal   373 ok / 0 FAIL
native safety-2 373 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Axiom store is separate from the DLM session/state snapshot.
- Evidence is a list, not per-rule/per-step provenance.
- No concurrency/owner lock or atomic compare-and-swap for the axiom file.
- No independence/minimality/consistency check across axioms.
- No automatic extraction-to-axiom pipeline.
