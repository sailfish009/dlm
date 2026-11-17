# Release 0.0247 — structure-probe ladder for deductive-learning architectures

- Date: 2026-11-14
- Predecessor: 0.0246 (reviewed measurement; preserved)
- Type: candidate research release (method + first measurement)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

## What this release adds

A measurement harness for **structural discovery**, after 0.0246 fixed the two
confounds (teacher-state exposure, goal-binding representation):

1. Goal-depth knob (`--goaldepth k`): goals are atoms in
   `closure(seed ∪ all) \ union_{|S|<k} closure(seed ∪ S)`, i.e. they need at
   least k candidate steps. The goal shuffle uses a local RNG stream, so the
   worlds (facts, seed rules, candidates) are **identical across depths**.
2. Evaluation-budget knob (`--eval-budget b`) for policy, beam and the exact
   subset bound (up to 6).
3. Weight save/load (`--save-weights`, `--load-weights`) so one trained cell is
   evaluated on every structural shift without retraining.
4. Ladder runner `run_probes.sh` and the design document `docs/design-0247.md`.

## First measurement (baseline cell, trained d=2/b=4, 3 seeds)

```text
config     goal    full    beam
d=2 b=4   0.7464  0.5100  0.8442     ID
d=3 b=4   0.4302  0.3100  0.5930     depth -31.6pp
d=4 b=4   0.1333  0.1100  0.2741     depth -61.3pp
d=2 b=6   0.9275  0.8400  0.9529     budget +18.1pp / +33.0pp full
d=4 b=6   0.5111  0.4000  0.6889     budget recovers 13.3 -> 51.1
```

Reading: the shipped cell extrapolates in **search budget** and collapses in
**composition depth**. Extra search recovers more than half of the depth loss
(13.3 → 51.1), so the discovery target is a cell that represents composition
inside one scoring pass.

## Search protocol (design)

`docs/design-0247.md` defines the structural space (`setx`, `hyper`, `bilinear`,
`recur`, `obligation`, `monotone`), a two-tier proxy/confirmation protocol
(1 seed × 15 epochs → top-2 × 5 seeds × 40 epochs), the adoption rule
(depth-gap reduction ≥ 10pp with ID loss ≤ 5pp) and the reporting rule (all
cells, including nulls, with parameter and update budgets).

## 0.0247 re-measurement of the 0.0246 2×2 (depth-independent goal stream)

The local goal RNG changes the sampled goal sets, so every comparator was
re-measured (5 seeds, d=2/b=4, matched updates):

```text
A root×aggregate 30.07/12.80   B full×aggregate 48.04/23.00
C root×relation  27.54/11.40   D full×relation  75.80/52.40
E full×relation(all) 75.80/50.40   utility_greedy 80.07   bound 94.57/85.00
```

The 0.0246 conclusion is unchanged (state collection dominant, relation features
add ~28pp on top). Ladder numbers above use the same stream.

## Gates

Everything from 0.0246 (validator schema, seed-persistent pool, 2×2, alias
audit, Maru parity) plus:

```text
STRUCTURE-PROBE-LADDER ID=.. d3=.. d4=.. d4b6=.. (depth gap, budget recovery)
```

The ladder gate checks harness validity (monotone depth decline, budget
recovery > 10pp, ID sanity floor), not a performance win.

## Limits / next

- Only the baseline cell is measured on the ladder; the five candidate cells are
  designed, not implemented.
- The remaining-budget value target stays `not-implemented` in
  `capabilities.json` (planned as the `obligation` auxiliary target).
- Probe CIs: the ladder currently reports 1–3 seeds; the confirmation tier
  (5 seeds + paired bootstrap) is specified but not run.
