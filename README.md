# DLM v0.0072 -- minimal nondeterministic constraint search

A small Screamer-inspired finite-domain solver in Maru. No Screamer dependency or
Common Lisp compatibility layer. Retains 0071 learned-controller and 0070 model /
compiler lifecycle. No PyTorch, GPU or LLM runtime.

```sh
./scripts/run.sh constraints
./scripts/run.sh interaction
./scripts/run.sh test
./scripts/run.sh repl
```

## New mechanism

src/dlm/constraints.l provides:
- explicit finite choices and depth-first backtracking;
- immutable per-branch domain maps (no undoable global side effects);
- binary neq/table constraints with arc-consistency propagation;
- optional minimum-remaining-values (MRV) variable ordering;
- enumeration of all solutions, with complete/incomplete status;
- expanded nodes, primitive relation checks and removed domain values reported.

```lisp
(csp-solve '((x (a b)) (y (a b))) '((neq x y)) 100 'propagate-mrv)
```

Result shape: `(csp-result STATUS SOLUTIONS NODES RELATION-CHECKS PRUNED)`.
An incomplete result may contain some solutions but never certifies exhaustive
absence. The node budget is not a strict relation-check/time/memory budget.
Inputs must be finite well-formed domains with distinct variable names and valid
constraint references; a hostile-input validator is not implemented.

## Fixed experiment

| Problem | Solutions | DFS nodes | Propagation nodes | DFS checks | Propagation checks |
|---|---:|---:|---:|---:|---:|
| Anchored coloring | 6 | 40 | 11 | 108 | 284 |
| Unsatisfiable triangle | 0 | 15 | 3 | 24 | 68 |
| Symbolic role candidates | 2 | 15 | 3 | 16 | 64 |
| Total | 8 | 70 | 17 | 148 | 416 |

All three arms (DFS, propagation, propagation+MRV) enumerate identical solution
sets. MRV ties propagation on these examples; no independent MRV improvement is
claimed. Propagation expands fewer nodes but performs MORE relation checks in
this naive implementation. This is a correctness/mechanism experiment, not a
runtime speed claim.

The role example preserves two interpretations of pump/valve and uses/used-by
under supplied table constraints. Those relation meanings are HANDWRITTEN. There
is no raw-text parsing, learned semantics, automatic axiom discovery or unique
interpretation claim. Ambiguity is retained instead of fabricated resolution.

## Learning boundary

0072 introduces the search substrate, not another learner. The 0071 controller
still learns only the list-action task; it does not yet choose CSP variables or
constraints. Future integration can rank legal choices while propagation and
final constraint validation remain independent. Search never writes Ground,
Experience, files, network requests or compiler promotion state.

## Checks

Full suite: 44 PASS assertions (31 inherited + 13 constraint checks). Optional
`python tests/differential.py` compares 20 Horn closure cases against sibling0066;
this is development-only and does not validate CSP completeness generally.

The active maru-compiler symlink points to runtime/releases/initial/maru.
Compiler commands remain scripts/compiler.sh rebuild|reproduce|verify ID|promote
ID|rollback. Model inputs are not an OS sandbox. See LICENSE.maru and NOTICE;
confirm DLM source authorship/license before publication.
