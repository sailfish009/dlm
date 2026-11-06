# Release 0.0107 — proof justification, exact snapshot identity, input guards

- Date: 2026-11-06
- Predecessor: `dlm_v0.0104` preserved. Input: `/research/code-review-0104.md`.
- Status: M1 (no learning layer). This release closes the four P1 defects and
  three smaller ones from that review.

## Reproduced in 0.0104, fixed here

| # | 0.0104 (reproduced) | 0.0107 |
|---|---|---|
| P1-1 | a fact with an **invalid** proof still got a rank, and a later conclusion built on it was accepted (`downstream-accepted=true`) | ranks are gone. Validation is an explicit worklist over the derivation DAG: every step must be a valid rule instance **and every child's own stored proof must check**; the walk is bounded so a cycle is refused |
| P1-2 | `q(x,z,y)` and `q(y,x,z)` produced the same digest (`145851`) | FNV-1a 32-bit over canonical serialization; also refuses dotted structures instead of faulting |
| P1-3 | a dotted term aborted the process (`type-of`), and a **negative rule index** hit the recursion guard | proof structure is validated (`index` long ≥ 0, pairs of var/const, child names); `rule-at` refuses non-lists and negatives; **every atom term** must be a constant or variable, so dotted and nested-list terms are rejected at the entry point |
| P1-4 | epoch-only save accepted an externally replaced file with the **same epoch** | saves and loads are identified by the **snapshot digest**; a mismatch is `rejected107 checkpoint` |
| P2-1 | `not p(x), q(x)` never fired, so a literal-order change produced a wrong `complete-empty` | negation is evaluated **after** all positive literals are bound; literal order is irrelevant |
| P2-2 | empty-body rules never fired (an empty child list was falsy) | `child-ids` returns a tagged result; `p107-rule (atom i1 ()) ()` derives and its proof checks |
| P2-3 | re-opening a second store leaked the first session lock | `open` while attached is `rejected107 already-attached`; `close` releases the lock |
| P2-4 | `reduce.py --check` trusted the header and never compared the body | `--check` re-renders and requires the body to match, plus the fact count |

## New oracle

`tests/oracle107.py` generates range-restricted programs with **shuffled literal
order**, negation over EDB, zero-arity heads and empty bodies, evaluates them with
an independent Python reference, and compares the derived atom sets.

```text
python3 tests/oracle107.py 150 105   ->  oracle107: 150/150 agree
```

The review's "35 cases, 9 mismatches" family is now a standing test
(`test_negation_oracle_agrees`, 25 cases inside the suite).

## Results

```text
./scripts/run.sh test        -> 46 native checks, ALL-CORE-TESTS-PASSED
python3 -m unittest ...      -> 14 tests OK
./scripts/run.sh northstar   -> 209 facts -> 231 closure -> 157 sentences, skipped 0
                                levels (1 135)(2 10)(3 12); library-only 121
```

The north-star counts are unchanged: the fixes make existing sentences
justifiable; they add no new output. **157 N1–N3 sentences are not evidence of
learning.**

## Remaining limits

- Maru's reader still aborts the process on syntactically invalid bytes; 0.0107
  never writes on a read failure and keeps `.previous`, but cannot catch the
  abort in-language.
- No definitions, lemmas, hypotheses, revision, N4–N9, native reducer or
  cooperative idle.
- The reduction remains an untrusted developer-side adapter with pinned hashes.

## Verification

`reproduce → verify → promote`, three-generation LLVM/stripped equality, native
and Python suites under the verified binary. See `docs/verification.log` and
`docs/release.txt`.