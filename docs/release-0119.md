# Release 0.0119 — total public patterns and shared exact call arity

- Date: 2026-11-07
- Predecessor: 0.0118. New tree is a candidate.
- Scope: close two inherited defects using the same explicit matching/validation
  discipline; no new contract statement.

## Fixed (0.0110 review)

### F3 — malformed public pattern no longer kills the process

A query pattern is now validated before any traversal:

```text
query pattern = proper list of atoms AND connected
```

`answer`, `plan`, `revise` reject a malformed pattern as `(rejected107 pattern)`
at the command boundary. `p107-plan` / `p107-answer-plan` also refuse it
directly, so the API is safe without the command wrapper.

Before: `(dlm 'answer 's 'not-a-pattern)` → SIGSEGV (normal) / native fault
(safety-2). After: clean rejection, covered by tests.

### F5 — admission and execution now share exact call arity

`p107-call-bindings` used to ignore extra actuals while `p107-bind-formals`
rejected them. It now requires exactly as many actuals as formals.

```text
one-formal unit called with two actuals
  admission -> rejected (expand-failed)
  execution -> already rejected
```

## Measured

```text
(dlm 'answer 's 'not-a-pattern)          -> (rejected107 pattern)
(dlm 'plan 'not-a-pattern)               -> (rejected107 pattern)
(dlm 'revise 'missing 'not-a-pattern)    -> (rejected107 pattern)
p107-plan / p107-answer with bad pattern -> status invalid
def body call with extra actuals         -> p107-def-ok? false, expand-failed
exact arity                              -> still admitted
```

Native 193 checks.

## Limits

- Query patterns remain connected conjunctions of atoms; calls in query
  patterns are still not part of the language.
- This does not address F1 (answer proof gate), F2 (nested admitted calls),
  F4/F9 (identity), F6/F7/F8 (budget/DAG/canonicalization).
- Pattern-based definition syntax itself is still surface data, not a macro
  system (see 0.0118).
