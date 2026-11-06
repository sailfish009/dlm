# Release 0.0107 — reviewed minimal core

- Date: 2026-11-06
- Predecessor: `dlm_v0.0103` preserved; this release fixes the defects found in
  `/research/code-review-0102-0103.md`.
- Compiler: Maru baseline unchanged.
- Status: M1 plus review fixes. **No learning layer is added in this release.**

## Defects reproduced in 0.0103, and the fix

| # | 0.0103 behaviour (reproduced) | 0.0107 fix |
|---|---|---|
| 1 | `(given "d0")` certified a **derived** fact, so a conclusion could pose as a source | `given` must reference a rank-0 extensional fact whose own proof is `given` |
| 2 | a rule could cite its own conclusion (self-support) and the checker accepted it | proofs carry their child ids; the checker rebuilds a rank map and requires every child rank < head rank; a cycle leaves facts unranked and the proof fails |
| 3 | an **extensional** predicate could be a rule head, so closed-world negation could be undermined | rule safety rejects EDB heads and enforces range restriction (head/negative variables must occur positively) |
| 4 | `q(x,y)` and `q(y,x)` produced the same rule checksum, so an old snapshot opened under changed background laws | the digest is now canonical, order-sensitive serialization (`p107-digest`), not an additive summary |
| 5 | `(dlm 'observe ... 'notalist)` caused a **SIGSEGV** | every entry validates list/type/arity first; accessors guard non-states; malformed input returns `rejected107` |
| 6 | observations were not durable until a later step/close; retract/reset ignored checkpoint failure | **every** transition goes through `p107-publish`: save first, publish after, failure keeps the old state |
| 7 | two sessions could open the same store and lose updates (last writer wins) | a session holds `file-lock` from open to close; a second opener gets `rejected107 session-locked` |
| 8 | an externally changed file could be overwritten | a save must match the epoch last seen on disk, else `rejected107 checkpoint`; `.previous` is kept |
| 9 | a read error was treated like a missing file (attach + write) | `missing` is distinguished from `corrupt`/`trailing-data`; only a missing path creates a new store |

Regression checks for 1–5 and 9 are in `tests/core-tests.l`; 6–8 are in
`tests/test_d107.py` (fresh process, second session, stale epoch).

## Results

```text
./scripts/run.sh test        -> 41 native checks, ALL-CORE-TESTS-PASSED
python3 -m unittest ...      -> 10 tests OK
./scripts/run.sh northstar   -> reduced 209, closure 231, sentences 157, skipped 0
                                levels ((1 135) (2 10) (3 12)); library-only 121
```

The north-star counts are unchanged from 0.0103: the fixes add no new sentences;
they make the existing ones supportable. **157 sentences remain N1–N3 output, not
evidence of learning.**

## Known limitation (unchanged, now documented)

Maru's reader aborts the process on a **syntactically invalid** file
(`missing closing delimiter`, exit 20). 0.0107 does not write on a read failure
and keeps the previous snapshot, but it cannot catch the reader abort in-language.
Mitigation today: treat snapshot bytes as trusted, keep `.previous`, and restore
by replacing the damaged file. A length-prefixed or byte-level format would need a
Maru primitive that is not available in this baseline.

## Verification

`reproduce → verify → promote` with three-generation LLVM/stripped equality; the
native suite and the ten Python tests run **under the verified binary**. See
`docs/verification.log` and `docs/release.txt`.

## Limits

No definitions, lemmas, hypotheses, revision, N4–N9, native reducer or
cooperative idle. The reduction is a developer-side adapter with pinned hashes.
Counts are not comparable with 0.0062's 42 selected sentences.