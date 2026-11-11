# Release 0.0123 — compiled definition views and plan reuse

- Date: 2026-11-07
- Predecessor: 0.0122. Candidate, not promoted.
- Scope: reuse checked definitions as plans/views. No new facts, no grammar change.

## Added

- `p107-def-plan` compiles a definition to `(plan107 ID VARS STEPS)` and caches
  it by **id + exact body**, so a revision cannot silently reuse a stale plan.
  `p107-def-steps` is the path used by `p107-plan`, `p107-expand-call`,
  `p107-step-apply` and `p107-instantiate`.
- `p107-views` compiles the active 2-atom definitions into the view used to
  compose `b1 + atom -> b2`. It is built once per learn pass and keyed by the
  exact definitions list; `p107-learn` resets it.
- `*p107-plan-reuses*` and `*p107-view-builds*` make reuse auditable.

## Invariants

```text
compiled steps == stored definition body
plan reuse counter advances on the second plan request
active b1 becomes a compiled 2-atom view
view compilation and planning add no facts to the observations
definition plans never appear as evidence predicates
```

The stored observation list is unchanged; a plan is not an `obs107` and not a
derived fact. Plans are invalidated by exact body/defs equality, not by a hash.

Native 244 checks.

## Limits

- Still 2→3 atom composition. Deeper `c0→c1→c2` needs grammar extension and the
  inherited F2 nested-call fix.
- No materialized definition facts; views are plans over fixed evidence.
- F1/provenance/self-evaluation remain open.
