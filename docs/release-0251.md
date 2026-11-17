# Release 0.0251 — harness repair and fixture redesign

- Date: 2026-11-15
- Predecessor: 0.0250 (preserved)
- Type: candidate research release (repairs per `/research/code-review-0250.md`)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

## Fixed

| Finding | Repair |
|---|---|
| **R250-1 CRITICAL** rule-sequence arrays sized `SEED_RULES+NSTEPS` (6) while the evaluation budget is 6 | all rollout/policy/bound arrays use `MAXBUDGET`; `-O0` no longer aborts. Gates: `ASAN+UBSAN clean at eval budget 6 (goal depth 4, scan mode)` and LLVM O0/O2/O3 identity **at eval budget 6** |
| **R250-2/3** world stream identity | structure stream seeded only by `(split, idx)`; goal draw uses its own stream; generation is **total** (no retries). `--census` reports genuine vs fallback: d2 92%, d3 46%, d4 7% genuine. `--goal-scan` scans structures until the exact depth is genuine (180 worlds: 194 / 397 / 2335 scans at d2/d3/d4) and is now used by every ladder run, so ladder rungs are genuine |
| **R250-4** probe log gates non-discriminative | new `tools/probe_stats.sh check <prefix> <seeds>`: exact SEED/MEAN row counts, distinct seed ids, finite fields in [0,1], stray-line rejection (catches the `port_beam=` fragment), no `tee` double-write |
| **R250-5** margin 0.01 ≈ SE/8, seed 13 flips it | paired-by-seed statistics with SE and range; directional gates removed. Relation−aligned at d4/b6 = **+0.062 ± 0.061** and aligned−shifted = **−0.019 ± 0.047** → both **INCONCLUSIVE at 2SE**; the 0.0250 "binding tokens hurt" reading is withdrawn as unsupported at n=5 |
| **R250-6** dimension labels | state 8→44, candidate 26→38 (RELOB) →56 (BINDTOK); verify prints `relation(38)`/`aligned(56)` |
| **R250-7** shift permutation recoverable | the control block is taken from **another candidate's** rows (rotation by 7 over the candidate list), not an invertible entity shift |
| R250-8 stale weights | `WHeader {magic, state_dim, cand_dim, variant, hard, relob, bindtok, goaldepth, eval_budget, pchk}` written with the weights; a mismatched build exits 4 with `WEIGHTS-MISMATCH` |

## Open (not repaired here)

- **R250-10**: `REGRET` is computed with at most 3 continuations, so `4_6` equals `4_4`; the regret budget will be printed and the b=6 value computed by sampling in the next version.
- R250-9: `alias_audit.c` is still unchanged; it now reports collisions (22,586 aggregate pairs, relation 0) with the optimal-action case reported, not gated.
- 2-variable relational fixture (the discriminating experiment for binding) is still not implemented.

## Re-measured results (fixture redesigned, all arms genuine depth)

2×2 (5 seeds, 180/60/100): A root×aggregate 0.2630/0.0980, B full×aggregate 0.4974/0.2880,
C root×relation 0.2755/0.0900, D full×relation 0.7538/0.4880, E full×relation-all 0.7839/0.5180.

Ladder (5 seeds, train d=2/b=4, relation arm):
```text
d2 b4 0.7832+-0.0039   d3 b4 0.5977+-0.0091   d4 b4 0.1159+-0.0209
d2 b6 0.9524+-0.0070   d4 b6 0.6651+-0.0391
```
Contrasts (paired by seed, 2 SE): relation−aligned +0.062±0.061, relation−shifted +0.043±0.040,
aligned−shifted −0.019±0.047 → **all inconclusive**. The width/binding question stays open.

## Verification

```bash
cd /research/dlm_v0.0251/experiments/proof_state_transformer_maru && ./run.sh && ./verify.sh
cd /research/dlm_v0.0251 && ./scripts/verify_release.sh
```
