# Release 0.0125 — trust-boundary recovery before EML-style formation

- Date: 2026-11-08
- Predecessor: 0.0124. Candidate, not promoted.
- Input: `/research/analysis-eml-to-dlm-0124.md`.
- Scope: the **0-step** of that analysis. No EML numeric operators, no
  confidence/RMSE promotion, no unit-DAG grammar yet.

## Why this release

The EML analysis recommends recovering DLM's existing trust boundary before
importing its formation loop. This release closes three prerequisites:

| defect | fix |
|---|---|
| 0.0110 F1: answer used witness membership, not proof checking | every answer witness now passes `p107-proof-ok?`; a forged/missing witness proof makes the answer `invalid` |
| 0.0110 F1: symbol `'same` and string `"same"` produced the same fact-ID prefix | observation admission rejects a second observation whose stringified ID already exists |
| 0.0110 F2: nested admitted calls lost planned rows | `p107-expand-items` recursively flattens tagged calls; execution and instantiation use the same deep expansion |
| 0.0110 F8: an 8-variable public query aborted | query patterns are bounded to 6 variables **before** canonicalization; command returns `(rejected107 pattern)` |

## Measured

```text
valid witness proof            -> true
forged / missing witness proof -> false
symbol/string observation IDs  -> second observe (rejected107 observation)
nested d1 -> d2 -> d3:
  raw rows 2, planned rows 2, planned calls 6
8-variable answer             -> (rejected107 pattern), process survives
```

Native 260 checks normal and safety-2; Python 16 tests; contract oracle 256/256.

## What was intentionally not taken from EML

- `exp(x)-ln(y)` or any numeric EML primitive as a logical kernel.
- confidence / RMSE / rational coefficient as proof or admission.
- finite probe equality as definition/theory identity.
- string count/ngram as natural-language grounding.
- Python facade/Axiom objects, LS/Adam master fit.
- The bugs found in the EML copy (premise bypass, scope-insensitive merge,
  rejected-but-stored evidence, ngram NameError) are **not** ported.

## Still open

- 0.0110 F4/F9: non-injective structural identity and FNV32 theory identity.
- 0.0110 F6/F7: exact budget boundary and memoized shared-DAG verification.
- Residual frontier and bounded unit-DAG composition (the analysis's step 1).
- Scope/evidence-conditioned applicability (step 2).
- F1 is now closed for answer; F2 for nested execution; F8 for the public query
  boundary. Deeper grammar still needs explicit ports/dependency versions.
