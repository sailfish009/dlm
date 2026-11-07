# Release 0.0118 — surface notation for checked definitions

- Date: 2026-11-07
- Predecessor: 0.0117. New tree is a candidate.
- Scope: definition notation plus a canonical validator fix.

## Added

```text
(define NAME (VARS...)
  (pattern (ATOM...))
  (body (STEP...)))            STEP = ATOM | (call NAME (TERM...))
    -> (def107 NAME VARS PATTERN BODY)
```

- `p107-sd` matches the surface form with `d107-match.l`, expands `(call ...)`
  to `call107`, then re-validates with `p107-def?` before returning
  `(ok CANONICAL)`.
- `p107-sd-write` emits the surface form and makes round-trips testable.
- The surface file now loads after `d107-def.l` so definition expansion can use
  the canonical validator directly.

## Fixed

`p107-def?` validated the pattern but **not the body**: any list was accepted
as a body step. It now requires every body step to be an atom or `call107`.
This was found while adding the surface form and is covered by a canonical
regression test.

## Measured

```text
surface definition -> def107 -> p107-def? = true
surface (call ...) -> call107; writer -> surface; round-trip exact
missing field / arbitrary body step -> (invalid surface-shape) / (invalid definition)
canonical def107 with (assign x 1) in the body -> p107-def? = false
```

Native 182 checks.

## Limits

- Atoms remain canonical `(atom PRED (TERMS...))`; the surface form does not
  invent a second atom syntax.
- This is still an expander over quoted data, not a Shen macro system.
- Definition admission (`p107-def-ok?`) still has the inherited nested-call and
  arity issues (0.0119).
