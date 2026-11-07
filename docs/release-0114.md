# Release 0.0114 — `if` with every feasible branch checked

- Date: 2026-11-06
- Predecessor: `dlm_v0.0113` preserved. Input: 0.0113 review order.
- Scope: the `if` fragment only. `call` summaries and library dependency checks
  are **not** in this release.

## Added

- `(if E THEN ELSE)` where `E` is a Boolean expression over declared variables
  and `THEN`/`ELSE` are **assign-only** bodies (nested `if` is rejected as
  invalid in this step, by design).
- Verification is still universal over every input satisfying Pre: the case
  table has one row per eligible input, and the branch actually taken is recorded
  in the output row. Across inputs both branches are exercised, so a feasible
  branch that violates Post is caught.
- Structural validation extends to `if`: guard expression over declared
  variables, flat branch bodies of `assign` with Boolean literals, depth guard.
- The independent checker (`p107-c-check`) is unchanged and still recomputes the
  eligible inputs and every row from the contract.

## Measured

```text
if with both branches, Post = (f == c)  -> verified, 4 cases
   (case (1 1) (1 1)) (case (0 1) (0 0)) (case (1 0) (1 1)) (case (0 0) (0 0))
if without else, Post requires f when c  -> refuted (c = 0 branch)
if guard uses an undeclared variable     -> invalid
```

Native 102 checks; Python 15 tests. Release `20261107T001902Z-17924`;
three-generation LLVM/stripped equality; manifests 27/27.

## Not yet

- `call` with a verified summary; the 0.0112 review's "unverified library
  injection" item therefore remains open.
- Library prefix/dependency validation, failure of a callee's Pre as a
  counterexample, loops, old-values, non-Boolean state.
- The `if` fragment alone is still not a Silicon-style verifier for a language;
  it is a checked core to build on.
