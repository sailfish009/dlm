# Release 0.0169 — general stride inference (candidate)

- Date: 2026-11-08
- Predecessor: 0.0168. Candidate, not promoted.
- Scope: infer the recursive step width from positives and negatives instead of
  choosing only between fixed stride 1 and stride 2.
- Analysis: `/research/analysis-synth-stride-0169.md`.

## Changes

`src/dlm/synth.l`:

- `s-vars`, `s-path-atoms` — build k base edges with fresh variables
- `s-seedk-rule` — `R(x0,xk) :- P(x0,x1), ..., P(x(k-1),xk)`
- `s-reck-rule` — `R(x0,z) :- P(x0,x1), ..., P(x(k-1),xk), R(xk,z)`
- `s-stride-synthesize` — search strides 1..maxk, reject negative conflicts,
  maximize positive coverage, prefer the shortest consistent stride

`experiments/synth_stride_repl/` + `scripts/synth_stride.sh`.

A fresh recursive-tail variable is used in `s-reck-rule`; reusing the last base
variable made the head and recursive body share the wrong variable.

## Experiment

Training chain: 6 parent edges `a..g`.
Positive: `ancestor(a,g)` (distance 6).
Negatives: distance 2, 4, and 5.

```text
ONE none conflict=n/a
TWO none conflict=n/a
PROGRAM stride=3 rules=2 support=(u0)
COVERAGE 1/1
NEGATIVE clean
HELD proof
HELD NEG fail
SEED ONLY HELD fail
FROZEN fail
done-stride
```

Selected program:

```text
ancestor(x,z) :- parent(x,y), parent(y,w), parent(w,z).
ancestor(x,z) :- parent(x,y), parent(y,w), parent(w,v), ancestor(v,z).
```

Stride 1 and stride 2 derive the distance-2/4 negatives, so they are rejected.
Stride 3 covers distance 6 and rejects 2, 4, 5.

## Self-host

```text
compiler.sh reproduce
→ 20261109T084331Z-25279
compiler.sh verify 20261109T084331Z-25279
→ Verified
```

## Measured

```text
native normal   30 checks / 0 FAIL
native safety-2 30 checks / 0 FAIL
self-host       verified
```

## Still not

- Stride search is bounded by `maxk` (tested to 4).
- Only a single base predicate is used in the step.
- Negative filtering is still template selection, not general theory revision.
- Provenance is template fact-ID support.
