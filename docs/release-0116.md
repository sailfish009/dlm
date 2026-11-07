# Release 0.0116 — bounded `call` summaries over a prefix-checked library

- Date: 2026-11-07
- Predecessor: `dlm_v0.0114` (last promoted release). Inputs: the 0.0115 review
  (`/research/code-review-0115.md`) and the 0.0116 candidate review
  (`/research/code-review-0116.md`).
- Status: **promoted.** Release `20261107T064706Z-31624`; predecessor runtime
  `20261107T001902Z-17924` (0.0114) is `runtime/previous`. `dlm_v0.0115`
  remains a review-only artifact.
- Runtime: self-reproduced by `scripts/compiler.sh reproduce` from the 0.0114
  compiler, then `verify` + `promote`. Three-generation LLVM and stripped
  binaries are identical (`16b9b39c…`, `cce40f99…`).

## Review items and this tree

### From the 0.0115 review

| Item | 0.0116 |
|---|---|
| F1 missing implementations / load failure | all helpers are defined in dependency order; the tree loads and runs |
| F2 `admitted` is not evidence | no marker; `(unit107 NAME CONTRACT CASES)` is checked by recomputing CASES under the prefix |
| F3 refuted wrapped as invalid | `(refuted (0) call-precondition NAME)` survives `run → scan → verify-lib` |
| F4 no tests for the new feature | separate blocks in `tests/core-tests.l`; the 0.0114 checks are unchanged |
| F5 duplicate vars / arity / duplicate rows | distinct variables, exact IR arity, exact table equality |
| Q1 dependency shape | `run → scan → verify-with → lib-check → public boundary`, no cycle |
| Q2 ambient library | removed; every evaluator/checker entry point takes an explicit library |
| Q3 dependency digest | no digest; prefix revalidation + exact structural evidence |

### From the 0.0116 review

| Item | 0.0116 |
|---|---|
| F1 malformed RESULT crashes `check-evidence` | RESULT is shape-checked before any `nth`/`car`/`cdr`; integer, symbol, dotted, empty and extra-field results return `(invalid evidence-result)` |
| F2 RESULT tag ignored | only `(verified CASES)` is admissible; the checker recomputes the **full** result under LIB and requires exact equality. A refuted/unknown tag, a wrong table, or a fabricated `verified` for an inapplicable contract returns `(invalid evidence-result)` / `(invalid evidence-mismatch)` |
| F3 no size limit, 14 variables abort | bounded finite Boolean; over-limit input is `(invalid unsupported-limit KIND)` before enumeration/deep traversal, in normal and safety-2 runtimes |
| F4 stale docs / witnesses | README counts, learning text and capability witnesses updated; the checker is described as a recompute with the same library, not an independent verifier |

## Supported language (explicit limits)

```text
variables per contract          8     (2^8 = 256 Boolean states)
states enumerated             256
statements per body/branch     32
cons cells per contract       512
expression depth               16
units per library              16
summary rows per unit         256
```

These are checked by `p107-c-limit` before state enumeration. A contract one step
over a limit is rejected as `(invalid unsupported-limit vars|states|statements|
frame|depth|nodes)`. `p107-c-lib-check` reports `units`/`cases` limits, and a
huge case table or case row is rejected without traversing it.

`unknown` is still propagated by `run/scan`, but this layer has **no budget
scheduler**, so it never produces `unknown` itself. Resource exhaustion is
prevented by the bounds above, not converted into `unknown`.

## Trust boundary

```text
raw units  ── lib-check ──▶ checked prefix ── verify-with/run ──▶ result
                                │
                                └── evidence stores this exact value
```

- `p107-c-lib-check` accepts a unit only if its contract verifies under the
  earlier units and its declared case table is exactly the recomputed table.
- `p107-c-verify-lib` / `p107-c-check-lib` validate first and pass the checked
  prefix to the evaluator, so the evaluator cannot read a different library
  through the public path.
- `p107-c-run` is the internal evaluator; it assumes an already-checked library.
  Making it call `lib-check` would create the `run → lib-check → verify → run`
  cycle the 0.0115 review warned about.
- Evidence is `(evidence CONTRACT RESULT LIB)`. Only `(verified CASES)` is
  admissible, and `p107-c-check-evidence` recomputes the full result under the
  current library and compares exactly. A different library reports
  `stale-library` before any reuse.
- `p107-c-check` recomputes with the same library. It is an independent
  *recomputation*, not a separately implemented second verifier.

## Measured

```text
callee clear  (b) -------- (b 1) / (assign b 0) / (not (v b))
  summary          ((case (1) (0)) (case (0) (0)))
caller        (a b) ------ (v b) / (call clear) / (not (v b)) / frame (b)
  verified-lib     ((case (1 1) (1 0)) (case (0 1) (0 0)))
  => the callee bit changes, a is preserved, 2 summary rows applied
```

```text
direct run of (call clear): applied=1 verified=0 call-runs=1
public verify-lib:          verified=2  applied=2   (prefix + caller)
callee Pre false, caller valid: (refuted (0) call-precondition needflag)

8 variables  -> verified, 256 cases
9 variables  -> (invalid unsupported-limit vars)
14 variables -> (invalid unsupported-limit vars)   (no process exit)
32 statements -> verified ; 33 -> (invalid unsupported-limit statements)
depth 2 -> verified      ; depth 20 -> (invalid unsupported-limit depth)
```

Independent review oracle (`review-0116-evidence/contract_oracle.py`, seed 116,
Python inlines callee bodies while native consumes the generated prefix summary
tables): **256/256 PASS**, outcomes verified 84 / refuted 95 / invalid 39 /
inapplicable 38, 111 callers exercising a real call. It still passes after the
bounded/evidence fixes.

Rejections exercised by the suite: forged/empty summary, duplicate unit name,
forward and self call, caller missing a callee variable (interface), unknown
unit, duplicate declared variable, extra IR arity, duplicated input row,
over-long case row, malformed evidence RESULT, refuted/unknown tag over correct
cases, verified evidence for an inapplicable contract, and callee change making
old evidence `stale-library`.

## Known limits

- Contract language is finite Boolean, assign/if/call only. `if` branches remain
  assign-only; calls are top-level statements.
- Prefix validation re-runs every module on each public check. Correct, not
  incremental; no digest/cache shortcut is claimed.
- The compiler binary and Maru sources are unchanged from 0.0114; only the
  contract layer, tests and documentation differ.
- No SMT, loops, arrays, non-Boolean state, or procedure synthesis from
  contracts.

## Reproduce

```sh
./scripts/run.sh test
MARU="$PWD/runtime/safety2/maru" ./scripts/run.sh test
python3 -m unittest discover -s tests -p 'test_d107.py' -v
```