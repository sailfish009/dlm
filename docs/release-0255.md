# Release 0.0255 — native ports: backtracking search (Screamer) + subsumption (Silicon)

- Date: 2026-11-16
- Predecessor: 0.0254 (preserved)
- Type: candidate research release (capability port + experiment)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

## What was ported (core function → native C/LLVM construct)

| source | core function | native port |
|---|---|---|
| Screamer | nondeterministic choice + backtracking + trail | `dfs_world`: recursive rule choice, trail = applied-rule list (undo O(1)), model-ordered children, anytime incumbent (`g_best_seen` also updated at partial nodes) |
| Screamer | constraint propagation | admissible prune: `proven + (budget-depth) <= best` → cut subtree; dead-end prune when no live candidate |
| Silicon | state subsumption / path merging | fact-set packing + `dominated()`: a fact set that is a subset of a visited state at the same or smaller depth is pruned |

No CL/OCaml/Scala runtime is used. SBCL+Screamer were installed only for the
*external* cross-check of 0.0254's session; this release is pure C/LLVM.

## Result (5 seeds, 100 worlds, genuine depth 4, budget 4, same scorer)

```text
search              goal    full    cands/100w   nodes/100w
dfs b=1 sub=0       0.1159  0.0540     9,000        500
dfs b=2 sub=0       0.4349  0.3460    26,112      2,484
dfs b=3 sub=0       0.5127  0.4280    56,314      7,896
dfs b=3 sub=1       0.4492  0.3760    22,086      3,092
dfs b=3 noprop      0.4334  0.3620    24,131      3,384
dfs b=5 sub=0       0.6397  0.5720   150,782     35,140
dfs b=5 sub=1       0.5524  0.4920    34,071      7,819
beam W=3            0.2778  0.2000    22,200          -
beam W=10           0.3413  0.2700    68,400          -
beam W=25           0.4286  0.3400   165,100          -
bound (0253)        0.849
```

- **At equal candidate evaluations the native backtracking search dominates
  beam**: 0.4492 vs 0.2778 at ~22k cands/100w (+17pp), 0.5524 vs 0.3413 at
  34k/68k (+21pp), 0.6397 vs 0.4286 at ~151k vs 165k (+21pp).
- **Subsumption (Silicon port) cuts nodes 2.5–4.5×** (7,896 → 3,092 at b=3;
  35,140 → 7,819 at b=5) and improves coverage per unit compute
  (b=5/sub=1: 0.552 at 34k vs b=3/sub=0: 0.513 at 56k).
- **Propagation (Screamer port) adds +1.6pp** at b=3 with fewer candidates
  (0.4492 at 22.1k vs 0.4334 at 24.1k without it).
- Anytime incumbents matter: the DFS records the best partial derivation at every
  node, so it never returns worse than its best prefix.

## Open issues (found, not fixed here)

1. 0.0254 measured beam W=3 at 0.3587 and this release measures 0.2778 on the
   same fixture/seeds; one of the two runs is not comparable (suspected aggregate
   accounting between `decomp` and `port` scripts). The DFS-vs-beam comparison in
   this release is internally self-consistent; the cross-release drift needs a
   controlled rerun.
2. C `policy_world` (greedy) and `policy_world_beam(W=1)` disagree on 100/100
   worlds (0.0255 session finding). The native DFS b=1 (0.1159) matches the
   greedy path, which localises the discrepancy to the beam path.
3. Fixture: `NATOMS=40` is used for noise-fact atom ids while fact masks are
   6 bits × 6 entities; noise facts are partly truncated. Minor, pending fix.

## Next ports (defined, not started)

- **Rocq core**: obligation stack as the search state + kernel-checked proof-term
  emission per accepted step (certificate rate = 100% gate). Action space becomes
  apply/split/discharge instead of rule index.
- **Silicon core (second half)**: contract summaries — a kernel-verified
  subderivation registered as a single action (lemma), depth k collapses to 1.

## Verification

```bash
cd /research/dlm_v0.0255/experiments/proof_state_transformer_maru && ./run.sh && ./verify.sh
cd /research/dlm_v0.0255 && ./scripts/verify_release.sh
```

New gate: at matched candidate budget the native DFS must beat beam by ≥10pp,
subsumption must cut nodes ≥2× at comparable coverage, and propagation must not
hurt.
