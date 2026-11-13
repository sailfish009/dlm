# Release 0.0239 — Transformer Structure Discovery on Qualified Fixtures

- Date: 2026-11-13
- Predecessor: 0.0238 (candidate worktree)
- Type: candidate research release
- Runtime: `20261113T120607Z-976` (reused; `src/` unchanged)

## What changed

- Added `experiments/structure_discovery/`: P0 fixture qualification + P1
  single-axis structural variants on the M1 proof-state worlds, with learning
  curves, train-time intervention, parity control, and direction-aware gates.
- VERSION 0.0239; README/CANDIDATE updated.
- Fixed the stale `.gitignore` runtime whitelist (was 0236's runtime; now the
  active `20261113T120607Z-976`).
- New lab sources are included in `release.sources.sha256` (generated
  `sd_*.json`, `*.pt`, `*.log`, `qualify.json`, `direction_summary.json`
  excluded and gitignored).

## Why this lab exists

The 0219–0236 variant program could not register learning structure: on the
MNIST 10-case fixture the kNN prior is saturated (prior-only = full DT = 8/10
ground truth; loops/heads/optimizer variants leave picks unchanged), and the
0229 prior-decorrelated matrix's difference-only gate passed on accuracy
**degradation** (E00 6/10 → E01–E07 3–4/10, five variants identical). This lab
moves variants onto the first fixture where learning is demonstrated against
controls, and replaces "must differ" gates with direction-aware measurement.

## P0 — fixture qualification (computed)

```text
worlds 80 (seed 999), steps 264, entity splits disjoint
ceiling 3.7006  support 2.1610  prior -0.4631  random -0.8136
margin ceiling-support 1.5396 >= 0.5
margin ceiling-prior   4.1636 >= 1.0
margin support-random  2.9746 >= 0.5
P0-FIXTURE-QUALIFIED
```

## Harness parity control

`base` (M1 SetRanker replica) seed 11 reproduces the frozen 0238 M1 result:
`top1_utility 2.5462406`, all metric fields of all six result blocks abs < 1e-6
vs `reference_m1_seed11.json`. Base beats all controls on every seed (M1
margins); validation moves from −0.39 (pre-training) to 2.70 (final).
Determinism: base seed 11 retrain byte-identical.

## P1 — direction table (test top1 utility; Δ vs base, same seed)

Pre-registered rule: consistent effect iff all 3 seed deltas share a sign AND
|mean Δ| ≥ 0.2. Params: base/a1 18337, a2 20417, tied2/indep1 9793.

| variant | axis | seed deltas | mean | sd | ep30 deltas | class |
|---|---|---|---|---|---|---|
| a1_cross | candidate↔candidate attention blocked (train-time) | −0.024, −0.078, −0.040 | −0.047 | 0.022 | +0.05, +0.15, −0.00 | no-consistent-effect |
| a2_pe | learned positional embeddings (null control) | +0.073, −0.201, −0.172 | −0.100 | 0.123 | −0.01, +0.08, −0.24 | no-consistent-effect |
| a3_tied2 | one shared block × 2 loops | +0.130, −0.077, +0.158 | +0.070 | 0.105 | −0.03, +0.30, −0.10 | no-consistent-effect |
| a3_indep1 | one independent block (param-matched to tied2) | +0.029, +0.055, +0.102 | +0.062 | 0.030 | +0.12, +0.41, +0.06 | no-consistent-effect |

```text
V0239-STRUCTURE-DISCOVERY-PASS
```

## Result and interpretation

**No axis shows a consistent effect at the pre-registered threshold.** This is
a controlled null result, not a failed gate:

- Inter-candidate attention is barely recruited: blocking it costs only ~0.05
  utility (all seeds negative, below threshold). Utility ranking here is
  mostly state-conditioned per-candidate scoring, not inter-candidate
  comparison.
- Positional information is not recruited (A2 null, as predicted for a set
  task) — the methodological null control behaves as expected.
- Depth beyond one block is not recruited: the half-parameter `a3_indep1` is
  ≥ base on all seeds and learns faster early (ep30 deltas all positive);
  weight-tied depth (`a3_tied2`) ≈ base. Extra depth mildly slows early
  learning without final benefit.

The recruited structure on this task is the feature→utility mapping itself
(base beats support +0.54, prior +2.57, shuffled +3.31 on seed 11), not the
attention topology, depth, or ordering. This mirrors the MNIST-era finding
but is now measured on a qualified, non-degenerate fixture with a
parity-controlled harness — so the null is informative.

**Next questions (P2/P3, not claimed here):** axes that could be recruited on
harder tasks — conflict-sensitive ranking (M2 worlds, where inter-candidate
comparison may matter for conflict avoidance), relation-held-out
generalization, closed-loop credit (M3), and proof-DAG credit structure
(0236 credit graph). Structure discovery should follow task difficulty, not
precede it.

## Verification

```bash
cd /research/dlm_v0.0239/experiments/structure_discovery
./run_all.sh          # qualify -> 5 variants x 3 seeds -> repeat -> verify
```

```bash
cd /research/dlm_v0.0239
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```

## Limits

- PyTorch CPU research adapter; not native Q16/C (M0 path is separate).
- Synthetic propositional Horn worlds; entity-held-out only.
- 3 seeds; the effect rule is a pre-registered heuristic, not a significance
  test. Nulls at |mean Δ| ≥ 0.2 do not exclude smaller true effects.
- A1 masks attention at train and eval; eval-only masking is a follow-up.
- No cross-task replication yet (P3).