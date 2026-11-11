# Release 0.0126 — pre-composition hardening

- Date: 2026-11-08
- Predecessor: 0.0125. Candidate, not promoted.
- Input: `/research/code-review-0125.md`.
- Scope: close R1/R2/R3 and the open structural identity before any 0.0127
  unit-DAG expansion. No residual frontier or new grammar yet.

## R1 — canonicalization is bounded on every path

- `p107-conj-key` is total: a pattern over the 6-variable limit gets a
  size-prefixed structural key instead of running a factorial permutation.
- Each of these now rejects or skips unsupported patterns:
  - public query patterns,
  - definition admission (`p107-def-ok?`),
  - learner pair/triple candidates,
  - active 2-atom views.
- Verified repro:
  - an 8-variable definition admission is `(rejected107 definition)`;
  - a 1-variable public answer still completes;
  - `(dlm 'learn)` over 8-arity observations returns `nothing107` instead of
    aborting.

## R2 — admission and runtime share depth/size limits

```text
max expansion depth = 16
max expansion nodes = 512
```

`p107-def-executable?` walks the body dependency DAG at admission:
depth 16 is accepted, depth 17 is `(rejected107 definition)`. Runtime
`p107-expand-call-deep` enforces the same depth and the node cap.
The 20-step driver now admits d0..d16 and rejects d17..d19; planned answers stay
complete for the admitted prefix.

## R3 — execution and validation counters are separate

- `*p107-calls*`: execution-only call count.
- `*p107-expansions*`: execution + answer-validation expansions.
- `p107-expand-items` / `p107-expand-call-deep` take an `exec?` flag; planning
  passes true, answer instantiation passes false.
- `experiments/learn/run.l` prints both. The learning demo is now:

```text
plan-calls-after=1 plan-expansions-after=19 plan-steps=45
```

The Python test asserts the full line/token, not the substring `calls=1`.
The nested fixture is exactly `calls=2 expansions=6`.

## F4/F9 — structural identity

- `p107-key-serialize`: injective, length-prefixed codec for identity keys.
  A symbol `"a b"` no longer collides with two symbols `a`, `b`.
- `p107-exact-key` and `p107-conj-key` use it.
- `p107-rules-check` is now the **content string** of the rule set, not an FNV32
  digest. A theory change cannot silently reuse an old snapshot identity; old
  FNV-digest snapshots are rejected as stale rather than reinterpreted.
- `p107-digest` remains a change hint for observation facts; it is not used as
  definition/theory identity.

## Measured

```text
native normal      270 ok / 0 FAIL
native safety-2    270 ok / 0 FAIL
Python             16 tests OK
contract oracle    256/256 PASS
```

## Still open

- F6/F7: exact budget boundary and memoized shared-DAG verification.
- Residual frontier + bounded unit-DAG composition (0.0127).
- Scope/evidence-conditioned applicability (after that).
- No numeric EML/confidence/RMSE/LS/Adam/Python facade was imported.
