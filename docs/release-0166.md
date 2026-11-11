# Release 0.0166 — recursive seed+step program synthesis (candidate)

- Date: 2026-11-08
- Predecessor: 0.0165. Candidate, not promoted.
- Scope: synthesize a recursive two-rule program
  `R(x,z) :- P(x,z)` and `R(x,z) :- P(x,y), R(y,z)` from direct target
  examples, instead of only fixed-length chains.
- Analysis: `/research/analysis-synth-recursive-0166.md`.

## Changes

`src/dlm/synth.l`:

- `s-seed-candidates` — seed rule `R(x,z) :- P(x,z)` from a base fact and a
  matching target example
- `s-rec-candidates` — step rule `R(x,z) :- P(x,y), R(y,z)` from a base fact and
  a target example whose left argument is the base fact's right argument
- `s-rec-synthesize` — pair search, negative conflict rejection, positive
  coverage ranking
- `s-rec-program`, `s-rec-program?`, `s-rec-rules`, `s-rec-support`

`experiments/synth_recursive_repl/` + `scripts/synth_recursive.sh`.

## Experiment

Training: parent chain `a-b-c-d-e` with direct ancestor examples.
Target positives: `ancestor(a,e)`, `ancestor(c,e)`.

```text
PROGRAM recursive rules=2 support=(p0 p1 r2)
COVERAGE 2/2
NEGATIVE clean
HELD proof
SEED ONLY HELD fail
FROZEN fail
done-recursive
```

Held chain `f-g-h-i-j` has no ancestor facts. The synthesized pair derives
`ancestor(f,j)`; the seed rule alone does not, and the frozen empty theory does
not.

## Self-host

```text
compiler.sh reproduce
→ 20261109T081559Z-4366
compiler.sh verify 20261109T081559Z-4366
→ Verified
```

Verify includes core, MLIR, typed, proof, synthesis, ranked, chain3, chain4,
recursive, and next/third equality. Only benign clang target-triple warnings.

## Measured

```text
native normal   23 checks / 0 FAIL
native safety-2 23 checks / 0 FAIL
self-host       verified
```

## Still not

- Base predicate candidates are generated from observed two-argument facts;
  not general ILP.
- Ranking is coverage-first; no MDL/cost/independence.
- Fixed task/alignment vocabulary.
- Provenance is fact-ID support, not full source/span/quote.
- Not label-free self-supervision.
