# Release 0.0248 — discovery criteria for deductive-learning transformers

- Date: 2026-11-14
- Predecessor: 0.0247 (preserved)
- Type: candidate research release (criteria + exposure control experiment)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

The 0.0247 criteria measured outcomes. 0.0248 adds the missing discovery
signals (step-level regret, reward-exposure control) and runs the first
controlled experiment with them.

## New criteria

1. **Exact first-step regret** (`--regret`, `REGRET-MEAN`): for every live
   candidate at the root state, `Q(a)` = max goals reachable within the budget
   (subset enumeration), so `regret = max_a Q(a) − Q(chosen)` and
   `model_opt` = fraction of states where the chosen action is optimal.
   This separates **action quality** from **state reachability**, which coverage
   alone cannot do. Support and `utility_greedy` are scored with the same Q.
2. **Reward-exposure control** (`--balance-reward`): keep every reward-bearing
   training state, then fill to the same sample count, so the number of
   optimizer updates is unchanged and goal-reward exposure is matched across
   collection modes. 0.0247's depth gap mixed "harder goals" with "25× fewer
   reward labels" (303 / 45 / 12 at depth 2 / 3 / 4); this control removes that
   confound.
3. The ladder runner reports regret per config; `verify.sh` gates the balance
   direction (d4b6 ≥ unbalanced + 2pp) and `model_regret ≤ support_regret` at ID.

## Experiment: exposure balancing (3 seeds, train d=2/b=4, same weights on ladder)

```text
config   goal unbal  goal bal   beam unbal  beam bal   regret(model) unbal/bal
d2 b4    0.7573      0.7862     0.8394      0.8490     0.1133 / 0.0933
d3 b4    0.3953      0.4709     0.5717      0.6919     0.0700 / 0.0433
d4 b4    0.1358      0.1753     0.2593      0.3679     0.2133 / 0.1933
d2 b6    0.9287      0.9529     0.9541      0.9577     0.1133 / 0.0933
d4 b6    0.5753      0.6889     0.6864      0.7679     0.2133 / 0.1933
```

- Balancing reward exposure lifts every ladder cell, most on the structural
  shifts: d3 +7.6pp, d4b6 **+11.4pp goal / +8.2pp beam**.
- Regret decomposition: at ID the model's first step is near-support
  (0.09 vs 0.12 regret, 91% vs 88% optimal); at d4 the model's first action is
  *worse* than support (0.19 vs 0.17) while its coverage is higher — the depth
  gain comes from state reachability and beam, not from better first actions.
  This is the kind of distinction the old criteria could not make.

## Honest scope

- The deduction-cell comparison (binding+AND+shared repeat) is **not run here**;
  it remains the next experiment, now with the improved criteria attached.
- Regret is computed at the root state only (extending it along the policy's
  trajectory is straightforward and cheap at budget 4).
- 3 seeds for the probe ladder; the confirmation tier (5 seeds) is not run.
- All numbers remain conditional on the fixed fixture generator.

## Verification

```bash
cd /research/dlm_v0.0248/experiments/proof_state_transformer_maru
./run.sh && ./verify.sh     # V0248-PROOF-STATE-DISCOVERY-CRITERIA-PASS
cd /research/dlm_v0.0248 && ./scripts/verify_release.sh
```
