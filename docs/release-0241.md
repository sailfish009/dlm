# Release 0.0241 — Integral Learning: Integrability + Deductive-vs-Gradient Verification

- Date: 2026-11-13
- Predecessor: 0.0239 (0240 is a separate agent's worktree; untouched)
- Type: candidate research release
- Runtime: `20261113T120607Z-976` (reused; `src/` unchanged)

## What changed

- Added `experiments/integral_learning/`: two experiments testing the NOTE 87
  thesis (`integrate.py`/`credit.py`): *"Induction learns by differentiation;
  deduction learns by integration — gradient flow without a gradient."*
- VERSION 0.0241; README/CANDIDATE updated; lab sources in both manifests;
  generated artifacts gitignored.

## E1 — credit-field integrability (the foundational precondition)

For integral learning to define a single objective, the credit field must be
integrable: a potential F(theory) with credit(T,r) = F(T+r) − F(T). Measured the
discrete plaquette curl over **2400 plaquettes** (60 worlds × 40), four credits:

```text
apparatus control: goal/atom/util curl == 0, potential-identity err 0.0 (14400 checks)
STRUCTURE  goal / atom / util credit : INTEGRABLE (curl == 0, scalar potential exists)
ORDER      depth-weighted credit     : NON-INTEGRABLE (37/2400 plaquettes curl != 0, max 0.5)
```

**Verdict:** the *structure* of what is provable (goal/closure/MDL gain) is a
potential difference — integrable, a single objective exists. The *order* of how
it is proved (depth-weighted credit) carries curvature: alternative proof paths
of different length give path-dependent credit. Example: world 1, r1=(head 0,
body [1]) depth-credit 0.25 vs r2=(head 3, body [2,5]) 0.5, curl −0.25.

This is the structure/order split: integral learning can have one objective
**only if it uses integrable (structure) credit**. Depth/search credit is a
connection with nonzero holonomy, not a potential.

## E2 — integral learning vs gradient (the core hypothesis)

Online rule acquisition to close goals; 3 seeds (777/778/779) × 80 test worlds.
The integral learner accumulates kernel-exact utility credit (no gradient, no
parameters); matched against a gradient-trained set ranker closed-loop + controls.

```text
arm        success(mean)  per-seed            coverage  kernel-evals/world
integral   0.967          0.988/0.950/0.963   0.989     57.4   (no training)
single     1.000          1.000/1.000/1.000   1.000     57.4   (no training)
gradient   0.608          0.575/0.525/0.725   0.749      2.2   (+584 training steps)
scramble   0.008          0.000/0.025/0.000   0.118     32.2
permute    0.008          0.000/0.025/0.000   0.118     32.2
random     0.012          0.037/0.000/0.000   0.151      1.4
prior      0.004          0.000/0.000/0.013   0.117      1.3
false_assert = 0 all arms/seeds (kernel gate)
```

### Findings (honest, including the null)

1. **Exact-credit deductive learning works.** Integral success 0.967 vs
   scramble/permute 0.008 — the credit content does decisive work. **The 0223
   PERMUTE confound is fixed**: permute degrades to ~0, so the effect is the
   credit, not the scaffold.
2. **Integral beats gradient** (0.967 vs 0.608) with **no training phase**.
   Exact kernel credit outperforms the learned approximate ranker. The cost is
   online: ~57 kernel evaluations/world vs gradient's ~2.2 + offline training.
   Integral learning trades gradient computation for kernel computation.
3. **Accumulation adds no value here (the integral ≈ single null).** Single
   (memoryless) success 1.000 ≥ integral 0.967 on every seed. Because the exact
   integrable credit is already a *potential difference* (E1), greedy ascent on
   the current credit is optimal; the running sum is redundant. **"Gradient
   flow without a gradient" reduces to greedy exact-credit ascent when credit
   is exact and integrable.** The integral would earn its keep with noisy or
   non-integrable credit (not tested here).
4. **Metric caveat:** raw ∫debt dt rewards early stopping (scramble's low 0.756
   reflects giving up, not efficiency). Read at matched success: rounds-given-
   success are ~2.4 for integral/single/gradient alike — the difference is
   success rate, not speed-given-success.

## Refined thesis

The power of the deductive direction is the **exact credit signal** — deduction
gives an exact, kernel-certified credit where induction needs a numerical
gradient — not the accumulation machinery per se. With exact integrable credit,
learning is greedy potential ascent: no backprop, no parameters, certified
provenance, and (here) higher success than the gradient ranker. The integral
(accumulation) is needed only when the signal is noisy or non-integrable; E1
shows precisely which credits those are (order/depth credit carries curvature).

## Verification

```bash
cd /research/dlm_v0.0241/experiments/integral_learning
./run_all.sh          # E1 -> E2 x3 seeds -> repeat -> verify (V0241-INTEGRAL-LEARNING-PASS)
```

```bash
cd /research/dlm_v0.0241
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```

## Limits

- Propositional unary Horn worlds, 24-candidate pools. Kernel credit is cheap
  here; at large candidate spaces (M4's 8.8M) the online kernel cost of integral
  learning grows — indexed retrieval is required before the efficiency claim
  scales.
- Entity-held-out only; 3 seeds; margins are pre-registered heuristics, not
  significance tests.
- Gradient baseline is the M1 set ranker; stronger statistical baselines are
  future work.
- The integral-vs-single null is task-specific (exact, noiseless, integrable
  credit). Noisy/non-integrable-credit regimes are the next test.
- No native Q16/C port of the integral learner yet (Python research adapter).