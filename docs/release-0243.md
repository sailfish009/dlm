# Release 0.0243 — native integral-credit protocol repair + torch-free release gate

- Date: 2026-11-14
- Predecessor: 0.0242 (candidate; reviewed, claims retracted here)
- Type: candidate research release
- Runtime: `20261114T001318Z-27176` (rebuilt with the local clang 23.1.5;
  `src/` unchanged. The 0242 runtime `20261113T120607Z-976` was built with
  clang 23.1.4, so its `.comment`/GNU build-id could not reproduce
  byte-identically and the self-host gate failed on toolchain drift.)

## Why 0.0243 exists

A read-only review of 0.0242 (`/research/code-review-0242.md`) found the headline
"integral beats single by +11–18pp" confounded and the release gate dependent on
PyTorch. 0.0243 is the repair. 0.0242 is preserved unchanged as the reviewed
candidate.

Review findings acted on:

| Finding | Disposition in 0.0243 |
|---|---|
| F2 `integral` = 400 episodes vs `single` = 1 | data/compute-matched `last` arm + distribution of 100 single-episode policies; sample-size curve |
| F10 (new) fixed shuffled rule index acts as a hidden prior | randomized tie-break in credit collection and search; rule shuffle varies per seed; `ABLATION` line reproduces the old setting |
| F7 credit noise never measured; "noise is the resource" asserted | tight-vs-exact disagreement counted; `exact` credit arm; L1 estimation-error curve against an independent sample |
| F3 hot/cold diagnostic invalid after shuffle | topic/position derived from the head atom; per-rule table emitted; rank agreement with exact credit (Kendall τ = 0.798) |
| F9 +3pp heuristic, 3 seeds, no CI | paired per-episode wins/losses, integer z ≥ 1960 gate, native bootstrap 95% CI, 12 seeds |
| F4 Maru parity only a 6-atom toy | C emits two generated 40-atom worlds; Maru `p-close` re-derives them; gate diffs the two `WORLD` lines |
| F5 `verify_release.sh` did not run the lab | lab gate is now part of release verification |
| F1 release gate required torch | teacher observations frozen; gate verifies them with Maru only; scope pinned by `docs/native-scope-0243.md` + `docs/research-snapshots.sha256` |
| F8 `capabilities.json` version drift | version synced and checked in `verify_release.sh` |
| F6 "array-view / Q16" label-only | axiom base is now read through `MaruArrayView`/`mav_get`; the unused Q16 label is dropped |

## Result — what survives, what is retracted

12 seeds × 400 held-out episodes, randomized tie-break, 6-firing budget:

```text
arm          mean %   note
prior        40.81    accumulated tight-budget participation credit
last         12.13    memoryless, same episodes (data/compute matched)
uniform      12.13    no learning
random       12.73    fixed random weights
ema          40.83    recency weighting (alpha=1/8)
exact        43.73    accumulated full-budget credit
online       40.28    accumulated weights feed back into training closure
pos_oracle   40.43    hand-written depth-first + hot-topic oracle
```

Survives: **accumulation beats no accumulation** by +28.7pp mean (minimum seed
margin +25.3pp), paired wins 346 / losses 0 at seed 777, z ≥ 1960 and bootstrap
CI excluding 0 on all 12 seeds. One hundred single-episode policies average
13.45% (max 23.39%), so the gap is accumulation, not one lucky sample.

Retracted from 0.0242:

1. **"Noise is what makes the integral win."** Exact credit accumulates *better*
   (`exact` − `prior` = +2.92pp mean). Noise is a cost of the tight credit
   budget, not the resource.
2. **"The learned weights recover hot/cold topics."** They recover the full
   depth-first structural policy (chain position weights s0/s1/s2 = 13/30/83 at
   seed 777) plus topic hotness (hot 98 vs cold 28). Hot/cold is a partial
   description.
3. **"Integral over composition."** Online feedback adds nothing (−0.53pp mean)
   and is unstable (seed 784: −5.85pp). Offline accumulation is invariant to
   episode order; the path-dependent (online) variant changes weights but not
   accuracy. At this scale the "integral" is an empirical prior over rule
   participation.

## Verification

```bash
cd /research/dlm_v0.0243 && ./scripts/verify_release.sh
cd /research/dlm_v0.0243/experiments/native_integral && ./run_all.sh
```

Gates: toy + generated-world Maru parity; LLVM O0/O2/O3 byte identity over 12
seeds; `prior > last/uniform/random + 10pp` on all 12 seeds; paired z ≥ 1960 and
bootstrap CI excluding 0 on all 12 seeds; positive control (`pos_oracle >
uniform + 5pp`); measured denoising (L1 337 → 97 milli, n = 1 → 400); offline
prior order-invariance; determinism; version consistency; torch-free release
scope; lab gate inside release verification.

## Limits

- Synthetic 40-atom propositional world; the learned object is a static rule
  priority, so this does not demonstrate a proof-path integral or an
  order-non-integrable credit structure.
- Credit is binary backward participation; depth-weighted and failure-frontier
  blame remain future work.
- Maru parity covers ground closure, not the credit-weighted budgeted search.
- 12 seeds resolve +10pp differences on this fixture only.