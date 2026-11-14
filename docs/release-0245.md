# Release 0.0245 — review repairs for the native proof-state transformer

- Date: 2026-11-14
- Predecessor: 0.0244 (reviewed, preserved unchanged)
- Type: candidate research release (repair + re-measurement)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

## What changed

Applies `/research/code-review-0244.md` F1–F7 to a new version:

- **F1** per-entity goal generation (reference semantics) + independent
  witness/reachability audit; two fixtures reported separately (reference
  distribution and a declared composition-requiring one).
- **F2** every control mean printed on MEAN and recomputed from SEED rows.
- **F3** strict log validator (row counts, unique seeds, finite required fields,
  recomputed means, control margins, declared direction) + a 10-mutation
  regression suite; empty/zero-row/one-row/model-below-baseline inputs fail.
- **F4** `utility_greedy` comparator renamed; the impossible-upper-bound gate is
  removed; a budget-exact bound enumerates all rule subsets of size <= 4 and
  asserts model <= bound on all 500 seed-world pairs.
- **F5** Maru parity runs on the main-protocol checkpoint (hard, 180/60/100,
  seed 11, 40 epochs), records its config and weights checksum, and reproduces
  100/100 initial-state picks.
- **F6** six matched-search beam arms with identical budgets and a paired world
  bootstrap CI.
- **F7** mask-aware shared loss for training and the finite-difference checker;
  gradcheck for all six variants.

## Result

Reference fixture (F1-correct) is **saturated**: exact bound 100%, greedy
comparator 100%, model 93.07%, support 86.00%. It cannot discriminate rankers.

Declared hard fixture (goals need >=2 candidate steps; bound 95.57% / 88.00%):

```text
model greedy      0.3247 / 0.1240
support greedy    0.3579
utility_greedy    0.7565
model beam        0.4066 / 0.1680
support beam      0.5535 / 0.3600
model beam - support beam  -14.7pp goal [-22.7,-5.9], -19.2pp full [-28.0,-10.6]
```

**Negative result:** on the repaired composition-requiring fixture the learned
ranker loses to a symbolic support heuristic and is far below the utility-greedy
comparator; the 0.0244 model-minus-support advantage was a property of the
broken goal distribution. Architecture variants (utilhead/mask/goalx/loop/bind)
stay within noise on both fixtures (hard: 32.5–35.3% proof).

## Verification

```bash
cd /research/dlm_v0.0245/experiments/proof_state_transformer_maru
./run.sh && ./verify.sh                 # ~13 min, V0245-PROOF-STATE-TRANSFORMER-PASS
./run_variants.sh                       # 12 arms x 5 seeds
cd /research/dlm_v0.0245 && ./scripts/verify_release.sh
```

Gate summary: reference parity, six-variant gradcheck, LLVM O0/O2/O3 identity,
F1 witness/reachability invariants, bound==independent audit and model<=bound,
strict validator + regression suite, matched-search budgets and CI, Maru 100/100.

## Limits

- Unary world (binding trivial); relational fixture still pending.
- Hard fixture is a declared deviation from the reference generator.
- Single-step utility training target; no plan/value labels yet.
- 5 seeds share the same worlds; only init/order vary.
