# Release 0.0246 — validator repair, seed-persistent goal pool, teacher-state exposure, relation features

- Date: 2026-11-14
- Predecessor: 0.0245 (reviewed, preserved unchanged)
- Type: candidate research release (repair + intervention experiment)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

Applies `/research/code-review-0245.md` R245-1–5.

## R245-1 — strict validator

`tools/gate_check.c` now enforces one schema for SEED and MEAN: identical
required field sets, full token consumption (a `garbage` suffix fails), no
duplicate fields, finite recomputation, all ratios in [0,1], every arm ≤ the
exact bound (`proof_*`, `full_*`), integer non-negative budgets, `seeds=` equal
to the SEED row count, `forwards_model ≤ search_states`, control margins and the
declared direction. `gate_regression.sh` keeps 17 rejected mutations, including
the review's `proof_model=1.0100`, `beam_full_support` tamper, zero/inf budgets,
`seeds=999`, suffix garbage and duplicate fields.

## R245-4 — seed-persistent goal pool and audit semantics

Goal generation, the one-candidate control, reachability and the exact bound all
use `closure(facts, seed ∪ chosen)` (`src/pst.c`, `tools/world_audit.c`). The
audit now also reports the eligible pool (`pool_atoms`) and
`goals_not_in_pool` (0 on the shipped fixture). The hard fixture was re-measured:
bound 94.34 % goal / 85.00 % full, 507 eligible atoms, 265 goal occurrences.

## R245-2 — teacher-state exposure (the dominant effect)

`build_dataset()` gained a full-budget collection mode (`--collect full`) and a
matched-exposure sampler (`--sample root|sub|all`). Measured exposure:

```text
collect=root  train 180 states, hist1=180, reward-bearing steps=0,  candidate labels  4320
collect=full  train 720 states, hist4=180, reward-bearing steps=320, candidate labels 16200
```

## R245-3 — relation-preserving features

`-DRELOB=1` adds goal–entity binding and dependency features to the state
(+3×(6+6)) and candidate (+3×4: head match, head known at the goal entity, body
supported at the goal entity, would-derive) vectors. `tools/alias_audit.c`
(independent) enumerates legal goal-set pairs of the same world: the aggregate
features coincide on **5,906** pairs and differ in optimal action on 1 of them
(the alias); the relation features coincide on **0** pairs.

## Intervention experiment: state collection × representation (2×2)

5 seeds, hard fixture, 180/60/100 worlds, 40 epochs, identical samples per
epoch (matched optimizer updates and validation cadence).

```text
arm                        proof   full    beam    beam_full
A root  × aggregate        0.2958  0.1180  0.3774  0.1620
B full  × aggregate        0.5147  0.3420  0.6294  0.4520
C root  × relation         0.3147  0.1300  0.3955  0.1860
D full  × relation         0.7653  0.5380  0.8498  0.6860
E full  × relation (all)   0.7442  0.5280  0.8309  0.6420
utility_greedy comparator  0.7774           support beam 0.6000 / 0.4100
exact bound                0.9434 / 0.8500
```

- State collection: +21.9 pp (A→B), +45.1 pp together with features (A→D).
- Relation features on top of collection: +25.1 pp (B→D); alone: +1.9 pp (A→C).
- Best arm beam 84.98 % beats the support beam by **+25.0 pp goal**
  [19.4, 34.4] and **+27.6 pp full** [19.0, 36.6] at the same search budget,
  and lands within 9.4 pp of the exact bound and 1.2 pp of `utility_greedy`
  (greedy arm 76.53 vs 77.74).

**Conclusion:** the 0.0245 negative result was a teacher-data exposure defect
(training only on root states with zero goal-reward labels) compounded by an
aggregate representation that cannot distinguish goal bindings. Fixing both
recovers the learned ranker: it now beats the symbolic baselines at matched
search and approaches the exact bound. The "single-step objective is the cause"
reading is **rejected** on this fixture: with the same single-step utility loss,
D reaches 76.5 % greedy.

## R245-5 — CI estimand

The BOOT lines now report the headline estimator (total-goal ratio per resample)
and the world-mean macro estimator separately, plus full-success. All CIs are
conditional on the five trained models.

## Verification

```bash
cd /research/dlm_v0.0246/experiments/proof_state_transformer_maru
./run.sh && ./verify.sh          # V0246-PROOF-STATE-TRANSFORMER-PASS
cd /research/dlm_v0.0246 && ./scripts/verify_release.sh
```

## Limits / remaining

- Value-target objective (remaining-budget labels) is **not implemented**; the
  acceptance sequence's second stage remains open. `capabilities.json` marks it
  `not-implemented`.
- Unary fixture: `bind` (attention bias) is still untested for relations; the
  *feature* representation is what carries binding here.
- Beam width 3, depth 4; bound enumerates subsets ≤4.
- 5 seeds share worlds; only initialization and ordering vary.
- Maru covers the initial-state scoring path (100 states) of the best arm.
