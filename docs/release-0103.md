# Release 0.0103 — fresh minimal native core (M1)

- Date: 2026-11-06
- Predecessor: none copied. `dlm_v0.0102` and earlier are reference only.
- Compiler: Maru baseline unchanged; new release `20261106T111422Z-29724`.
- Status: M1 implemented and measured; learning layers are not started.

## What was built

A new tree with **786 lines of new implementation** (`src/dlm/*.l` 574,
`adapters/reduce.py` 117, native tests 95) and no DLM code copied from the
previous versions:

| file | lines | role |
|---|---:|---|
| `src/dlm/d107-util.l` | 50 | list/string helpers, structural checksum |
| `src/dlm/d107-form.l` | 75 | atoms, rules, substitutions, EDB policy |
| `src/dlm/d107-close.l` | 105 | budgeted closure, proof terms, independent checker |
| `src/dlm/d107-session.l` | 138 | one state, events, replay, snapshot, atomic save |
| `src/dlm/d107-read.l` | 59 | N1–N3 sentences with support |
| `src/dlm/d107-agenda.l` | 17 | deterministic work item |
| `src/dlm/d107-command.l` | 130 | `(dlm ...)` surface |
| `adapters/reduce.py` | 117 | untrusted Python→facts reduction, hash pinned |

## Demonstrated behaviour

```text
./scripts/run.sh test        -> 26 native checks, ALL-CORE-TESTS-PASSED
python3 -m unittest ...      -> 6 tests OK
./scripts/run.sh northstar   -> reduced 209, closure 231, sentences 157, skipped 0
                                levels ((1 135) (2 10) (3 12))
                                library-only view 121 ((1 99) (2 10) (3 12))
```

Every emitted sentence carries a proof that the independent checker accepts.
Scope isolation, retraction, duplicate-observation refusal, event limit, forged
proof rejection, budget→`unknown`, snapshot-tamper refusal, background-law
invalidation, corrupt-file refusal and fresh-process equality are all covered by
tests.

## Verification

`./scripts/compiler.sh reproduce` → `20261106T111422Z-29724`;
`verify` and `promote` completed:

- native core suite and the six Python tests passed **under the verified binary**;
- candidate/next/third LLVM outputs and stripped executables compare equal;
- `src/maru` is unchanged (copied from the baseline, not edited);
- `docs/release.sources.sha256` and `docs/release.tests.sha256` were generated
  from that release and verify.

Evidence: `docs/verification.log`, `docs/release.txt`,
`docs/northstar-m1.log`, `docs/evidence/core-tests.log`.

## Honest limits

- **No learning**: no definition formation, lemma promotion, hypothesis layer,
  revision, or goal selection. `run` only interprets observations.
- **N4–N9 absent**; N1–N3 only, from fixed templates.
- The reduction is a developer-side Python adapter. The kernel never parses
  Python; integrity rests on pinned source/facts hashes.
- Counts are **not** comparable with 0.0062's 42 selected sentences; 0.0103 emits
  all readable facts over its own reduction.
- No SMT/arithmetic/heap/loop/concurrency verification, no LLM/GPU, no
  cooperative idle scheduler (`run N` only).
- Five events per observation are bounded at 256; the closure budget is logical
  steps, not wall time.

## Next (M2)

Definition formation with conservative expansion checks and record-scoped
support; then certified absence (N9) using the same EDB-restricted negation;
then lemma mining with reuse accounting. Each step needs its falsifier to fail
before it is claimed.