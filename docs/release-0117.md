# Release 0.0117 — Shen-inspired surface notation for contracts and units

- Date: 2026-11-07
- Predecessor: 0.0116 (promoted). New tree is a candidate.
- Scope: notation and explicit matching of surface forms. No new contract
  semantics.

## Added

`src/dlm/d107-surface.l` expands two readable forms into the canonical IR:

```text
(contract NAME (VARS...)
  (pre EXPR) (body (STMT...)) (post EXPR) (frame (VAR...)))
      -> (c107 NAME VARS PRE BODY POST FRAME)

(unit NAME (contract NAME ...) (CASES...))
      -> (unit107 NAME CONTRACT CASES)
```

- Matching uses `d107-match.l`: exact field count, dotted values rejected as
  `surface-shape`, and the unit form uses the same `(pat name)` twice so a unit
  whose name differs from its contract name is rejected.
- The expander re-validates the canonical result with `p107-c-valid?` before
  returning `(ok CANONICAL)`; it never weakens the contract checker.
- `p107-sc-write` / `p107-su-write` make round-trips testable.

## Measured

```text
surface contract -> canonical c107 -> verified
surface contract round-trip -> exact canonical
surface unit round-trip -> exact unit107
missing/extra field, dotted value, invalid body, repeated-name mismatch
  -> (invalid surface-shape) / (invalid contract)
```

Native 173 checks.

## Limits

- This is an expander, not a macro system or a Shen port. Surface forms are
  ordinary quoted Maru data.
- The canonical IR is still the only accepted input to the verifier, checker,
  library and evidence boundaries.
- Definitions and plans do not yet have surface forms (0.0118).
