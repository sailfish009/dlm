# Release 0.0167 — recursive program from one long positive (candidate)

- Date: 2026-11-08
- Predecessor: 0.0166. Candidate, not promoted.
- Scope: synthesize the recursive seed+step program from **one long positive**
  and base edges only, without direct target-edge examples.
- Analysis: `/research/analysis-synth-template-0167.md`.

## Changes

`src/dlm/synth.l`:

- `s-seed-base-candidates` — propose `R(x,z) :- P(x,z)` from each base binary
  predicate, without requiring a direct `R(a,b)` example
- `s-rec-goal-candidates` — propose `R(x,z) :- P(x,y), R(y,z)` from each base
  predicate and the target
- `s-template-synthesize` — pair search, negative conflict rejection, positive
  coverage selection
- `s-uniq` — de-duplicate support fact IDs

`experiments/synth_template_repl/` + `scripts/synth_template.sh`.

## Experiment

Training facts: `parent(a,b), parent(b,c), parent(c,d), parent(d,e)`.
Only target positive: `ancestor(a,e)`. No `ancestor(a,b)` etc.

```text
PROGRAM template rules=2 support=(t0)
COVERAGE 1/1
NEGATIVE clean
HELD proof
SEED ONLY HELD fail
FROZEN fail
done-template
```

The synthesized program is:

```text
ancestor(x,z) :- parent(x,z).
ancestor(x,z) :- parent(x,y), ancestor(y,z).
```

It covers the single long positive and transfers to a held four-hop chain with
no ancestor facts. The seed rule alone fails on that held chain.

## Difference from 0.0166

0.0166 required direct target examples such as `ancestor(a,b)` to propose the
seed and recursive rules. 0.0167 proposes the same recursive template from one
long positive plus the base edges.

## Self-host

```text
compiler.sh reproduce
→ 20261109T081849Z-203
compiler.sh verify 20261109T081849Z-203
→ Verified
```

Verify includes core, MLIR, typed, proof, synthesis, ranked, chain3, chain4,
recursive, template, and next/third equality. Only benign clang target-triple
warnings.

## Measured

```text
native normal   25 checks / 0 FAIL
native safety-2 25 checks / 0 FAIL
self-host       verified
```

## Still not

- The recursive rule shape remains fixed to `P(x,y), R(y,z)`.
- One positive can be consistent with many programs; no MDL/independence test.
- Base predicate candidates come from observed binary facts, not general ILP.
- Provenance is fact-ID support for the template, not a full derivation.
- Not label-free self-supervision; one positive target is still given.
