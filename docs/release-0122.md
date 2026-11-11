# Release 0.0122 — sparse indexed routing for candidate generation and joins

- Date: 2026-11-07
- Predecessor: 0.0121. Candidate, not promoted.
- Scope: CPU-native sparse routing. No dense attention, no grammar change.

## Added

`src/dlm/d107-index.l` indexes ground facts by:

```text
(pa predicate arity)                 all facts of one predicate/arity
(pv predicate arity position value)   exact value in one ordered argument slot
(v value)                             facts sharing a ground value
```

- `p107-join-indexed` uses the first bound argument of a literal to fetch
  candidates, then validates the rest with `p107-match`.
- `p107-patterns2-from` / `p107-patterns3-from` generate candidates from
  value-sharing edges and connected triples instead of all pairs/triples.
- `p107-support` now uses the indexed join; `p107-support-ref` keeps the
  exhaustive reference for differential tests.
- Per-record indexes are cached by observation id + fact digest; `p107-learn`
  resets the cache at the start of each pass.

## Bounds and status

```text
*p107-max-candidates*   512
*p107-max-join-probes*  50000
```

Exceeding a bound sets a reason and returns `(incomplete107 candidate-limit |
join-limit)`. The agenda surfaces it as `incomplete`, the step returns
`(incomplete S REASON)`, and the resident tick classifies it as `unknown`
(waiting), not as a silent empty result.

## Differential evidence

```text
indexed patterns2 == exhaustive patterns2   (same canonical keys)
indexed patterns3 == exhaustive patterns3   (same canonical keys)
indexed support    == exhaustive support    (q2, q3)
support is record-scoped (2 records -> 2)
ordered roles p(x,y) != p(y,x)
retraction lowers indexed support 2 -> 1 and still matches the reference
candidate cap -> incomplete107; learning recovers after restoring the cap
```

Native 238 checks.

## Limits

- Still 2→3 atom grammar. This is an execution/generation refactor, not new
  logical power.
- Index keys use exact structural equality; no FNV identity is introduced.
- F1/F2/provenance/self-evaluation remain open.
