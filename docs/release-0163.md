# Release 0.0163 — candidate ranking for frontier synthesis (candidate)

- Date: 2026-11-08
- Predecessor: 0.0162. Candidate, not promoted.
- Scope: replace first-fit synthesis with a checked candidate ranking by coverage
  of all training positives, then support size.
- Analysis: `/research/analysis-synth-rank-0163.md`.

## Changes

`src/dlm/synth.l`:

- `s-coverage` — number of training positives entailed by a candidate rule set
- `s-ranked-synthesize` — choose candidate with:
  - zero negative conflict
  - maximum positive coverage
  - larger support on ties

## Experiment

`scripts/synth_rank.sh` constructs an ambiguous frontier:

```text
alt1(r,u), alt2(u,t)   also connects path(r,t)
hop1(r,s), hop2(s,t)   correct connection
```

Training positives:
```text
path(r,t), path(v,p)
```

| arm | coverage | held path |
|---|---:|---|
| first-fit | 1/2 | fail |
| ranked | 2/2 | proof |
| frozen | 0/2 | fail |

The ranked candidate is selected because it generalizes to both training
positives; the first candidate only explains the triggering goal.

## Self-host

```text
compiler.sh reproduce
→ 20261109T075858Z-18858
compiler.sh verify 20261109T075858Z-18858
→ Verified
```

Verify includes core, MLIR, typed, proof, synthesis, ranked synthesis, and
next/third equality. Only benign clang target-triple warnings remain.

## Measured

```text
native normal   16 checks / 0 FAIL
native safety-2 16 checks / 0 FAIL
self-host       verified
```

## Still not

- Candidate space is still two binary facts sharing endpoints.
- Training positive/negative facts are fixed constraints; not label-free.
- Ranking is coverage-first; no MDL/cost/independence.
- No general ILP search or theory revision.
- Provenance remains fact-ID support.
