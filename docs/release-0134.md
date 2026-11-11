# Release 0.0134 — claim-order independence and recursive session repair

- Date: 2026-11-08
- Predecessor: 0.0133. Candidate, not promoted.
- Input: `/research/code-review-0133.md`.
- Scope: repair the claim→record, adapter, identity, budget, trust/scope and
  session boundaries before any live/curriculum extension.

## R1 — claim order no longer changes records/admission

- Observation record identity is the claim atom's **logical record key**
  (first argument, else predicate), not the first representative source.
- Corroboration bundle stores all distinct source/version pairs in the record.
- Order-permutation regression: two orders of the same 8 claims now produce the
  same one record and the same `(none)` learning result.

## R2 — cache adapter output loads natively

- `adapters/web_cache.py` quotes the atom, validates predicate/scope/trust and
  JSON-quotes source/version/extractor.
- End-to-end test: JSON → adapter → `run.sh proof claims.l` returns 0.

## R3 — injective observation identity

- Observation ID is `web:` + injective `p107-key-serialize` of the logical
  record key. `(A-B,C)` and `(A,B-C)` no longer collide.
- Name length limit for observation/record provenance is raised to 1024.

## R4 — self report is call-local

- `p107-gaps-with-budget` saves/restores `*p107-budget*`, `*p107-steps*`,
  `*p107-exhausted*`.
- Self report includes `closure-status`; gaps remain a read-only view.
- Regression: setting budget 1, calling self report, then answering still uses
  budget 1 and remains `unknown`.

## R5 — one session per arm, not per round

- `experiments/recursive_web/run.py` now generates **one driver per arm**.
- All rounds share the same DLM state; definitions/observations persist.
- The prior prefix cold-start interpretation is removed.

## R6 — trust/scope policy

- `guessed` claims never enter corroboration or observation conversion.
- `p107-claims->observations-scoped` requires the claim scope explicitly;
  cross-scope claims do not corroborate.
- Functional-predicate conflicts remain an explicit whitelist.
- Supporting source/version pairs are retained in the observation record string.

## R7 — terminal fan-out budget

- The match consumption point now checks the remaining budget before counting a
  new terminal success.
- Fan-out fixture: budget 1/2 -> unknown; budget 3 -> complete with 2 rows.
- Exact-N terminal successes are preserved.

## Measured

```text
native normal      311 ok / 0 FAIL
native safety-2    311 ok / 0 FAIL
Python             17 tests OK
contract oracle    256/256 PASS
```

Experiment (one session per arm) final round:

| arm | train_obs | defs | train_plan | held_obs | held_plan | held_rows | calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| web | 2 | 2 | 2 | 1 | 2 | 6 | 1 |
| no-web | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| single | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| scrambled | 1 | 0 | 3 | 0 | 3 | 0 | 0 |
| frozen | 2 | 0 | 3 | 1 | 3 | 6 | 0 |

## Still not

- Live web (cached structured corpus only).
- Autonomous next-source/goal selection; self report is read-only.
- Empirical world-law induction; only conservative definitions.
- Domain/relation held-out generalization; held records share the same shape.
- Cost beyond plan steps/calls.
- The 0.0114/0.0115 directories are absent; no preservation claim.
