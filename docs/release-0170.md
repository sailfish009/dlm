# Release 0.0170 — two-predicate block synthesis (candidate)

- Date: 2026-11-08
- Predecessor: 0.0169. Candidate, not promoted.
- Scope: synthesize a recursive rule over an ordered predicate pair
  `R(x,z) :- P(x,y), Q(y,z)` instead of a single base predicate.
- Analysis: `/research/analysis-synth-pair-0170.md`.

## Motivation

0.0169 could infer stride but only over one base predicate. Alternating edges
`up`/`down` defeat that search: no single-predicate rule traverses the chain.

## Changes

`src/dlm/synth.l`:

- `s-pair-seed-try` — find a co-occurring `P(a,b), Q(b,c)` block and propose
  `R(x,z) :- P(x,y), Q(y,z)`
- `s-pair-rec-try` — propose `R(x,z) :- P(x,y), Q(y,w), R(w,z)`
- `s-pair-seed-candidates`, `s-pair-rec-candidates` — de-duplicate by ordered
  predicate pair
- `s-pair-synthesize` — pair search with negative rejection and coverage ranking

`experiments/synth_pair_repl/` + `scripts/synth_pair.sh`.

## Experiment

Facts:

```text
up(a,b), down(b,c), up(c,d), down(d,e), up(e,f), down(f,g)
```

Positive: `reach(a,g)` (distance 6).
Negatives: distance 3 and distance 5.

```text
SINGLE coverage=0
PROGRAM pair rules=2 support=(v0 v1)
COVERAGE 1/1
NEGATIVE clean
HELD proof
HELD NEG fail
SEED ONLY HELD fail
FROZEN fail
done-pair
```

Selected program:

```text
reach(x,z) :- up(x,y), down(y,z).
reach(x,z) :- up(x,y), down(y,w), reach(w,z).
```

Single-predicate stride search cannot traverse the alternating chain. The pair
program covers the long positive, rejects the odd-distance negatives, and
transfers to a held alternating chain while rejecting the held negative.

## Self-host

```text
compiler.sh reproduce
→ 20261109T085126Z-29997
compiler.sh verify 20261109T085126Z-29997
→ Verified
```

## Measured

```text
native normal   32 checks / 0 FAIL
native safety-2 32 checks / 0 FAIL
self-host       verified
```

## Still not

- The block is exactly two ordered predicates, selected from co-occurring edges.
- No arbitrary predicate-sequence or guard invention.
- Negative filtering remains template selection.
- Support is the co-occurring block's fact IDs.
