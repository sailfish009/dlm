# Release 0.0120 — Shen-inspired surface notation, total patterns, and `assert`

- Date: 2026-11-07
- Predecessor: 0.0116 (promoted). This tree is a **candidate**, not promoted.
- Runtime: reuses the promoted 0.0116 release `20261107T064706Z-31624`.
- Scope: notation and two inherited boundary fixes, plus the missing `assert`
  statement. No SMT, heap, loops or non-Boolean state.

## What 0.0117–0.0120 adds

| version | change |
|---|---|
| 0.0117 | `d107-surface.l`: surface `contract` / `unit` forms expand to canonical `c107` / `unit107`, then re-validate |
| 0.0118 | surface `define` form expands to `def107`, with `(call ...)` sugar for `call107`; canonical definition body steps are now validated |
| 0.0119 | total query-pattern validation at `answer`/`plan`/`revise` and in the plan/answer APIs (0.0110 F3); admission and execution share exact call arity (F5) |
| 0.0120 | `assert` statement in bodies and `if` branches; surface forms accept it |

## Surface notation (expander, not a macro system)

```text
(contract NAME (VARS...)
  (pre EXPR) (body (STMT...)) (post EXPR) (frame (VAR...)))
      -> (c107 NAME VARS PRE BODY POST FRAME)

(unit NAME (contract NAME ...) (CASES...))
      -> (unit107 NAME CONTRACT CASES)

(define NAME (VARS...)
  (pattern (ATOM...))
  (body (STEP...)))              STEP = ATOM | (call NAME (TERM...))
      -> (def107 NAME VARS PATTERN BODY)
```

- Matching uses `d107-match.l`: exact fields, dotted values rejected, and the
  unit form repeats `(pat name)` so unit and contract names must agree.
- The expander re-validates the canonical result (`p107-c-valid?` /
  `p107-def?`). Surface data is never admitted directly.
- `p107-sc-write` / `p107-su-write` / `p107-sd-write` make round-trips exact.

## `assert`

```text
(assert E)   evaluate E in the current state
  true  -> continue
  false -> (refuted IN assert E) for that input
```

`assert` does not change the state, is allowed at top level and in `if` branches,
and remains subject to the declared-variable and size limits.

## Fixed

- **0.0110 F3**: `(dlm 'answer 's 'not-a-pattern)` and the `plan`/`revise`
  variants previously crashed (SIGSEGV in normal, native fault in safety-2); they
  now return `(rejected107 pattern)`. The plan/answer APIs also refuse the same
  input with status `invalid`.
- **0.0110 F5**: admission ignored extra actuals while execution rejected them;
  both now require exact arity.
- **0.0118**: `p107-def?` accepted an arbitrary list as a body step; body steps
  must now be atoms or `call107`.

## Measured

```text
surface contract/unit/definition round-trips     exact
malformed surface fields / repeated name         (invalid surface-shape)
assert true                                      verified
assert false                                     refuted with input + cause
assert in both if branches                       verified
assert undeclared / extra fields                 invalid
malformed public answer/plan/revise              (rejected107 pattern)
extra actuals in an admitted call                rejected / expand-failed
```

```text
native normal        200 ok / 0 FAIL
native safety-2      200 ok / 0 FAIL
Python               15 tests OK
independent review contract oracle (seed 116)
                     256/256 PASS
                     verified 84 / refuted 95 / invalid 39 / inapplicable 38
```

## Still missing

These are not closed by 0.0120:

- Rocq: answer proof gate (F1), typed IR/ports, context-aware memoized DAG (F7),
  collision-free theory identity (F4/F9).
- Silicon: nested admitted calls (F2), local path-condition scope/rollback,
  `old`, permission/effect, learned-definition summary reuse.
- Budget-driven `unknown` (F6), bounded canonicalization (F8).
- GraphReasoning candidate search: still not implemented; the learner keeps its
  fixed 2/3-atom, 24-fact search.
- A real Shen macro/reader: deliberately not adopted. Maru has no macro system,
  and the surface layer is data -> data with canonical revalidation.

## Reproduce

```sh
./scripts/run.sh test
MARU="$PWD/runtime/safety2/maru" ./scripts/run.sh test
python3 -m unittest discover -s tests -p 'test_d107.py' -v
```
