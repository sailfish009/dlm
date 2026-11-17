# Release 0.0254 — search-vs-scorer decomposition of the depth collapse

- Date: 2026-11-15
- Predecessor: 0.0253 (preserved)
- Type: candidate research release (diagnosis experiment)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

## Question

0253 established that the depth-4 collapse is composition, not expressibility
(bound 0.849, greedy 0.13). 0254 splits that collapse into **search width** and
**scorer quality**, and locates it in the **step index**.

## 1. Search width with the SAME scorer (5 seeds, train d2/b4 balanced)

| depth | W=1 | W=3 | W=10 | W=25 | bound |
|---|---|---|---|---|---|
| d2 b4 | 0.7861 | 0.8527 | 0.9106 | **0.9268** | 0.9414 |
| d4 b4 | 0.2365 | 0.3587 | 0.4651 | **0.5365** | 0.849 |

- d2: width 25 reaches 92.7% vs bound 94.1% → search nearly saturated; the scorer
  is adequate at depth 2.
- d4: width 25 reaches 53.7% vs bound 84.9% → **+30pp from search width alone**,
  with **31pp left to the bound** that the scorer's ordering cannot recover.

## 2. Step-indexed optimality on the model's own trajectory (exact Q per step)

| depth | step 1 | step 2 | step 3 | step 4 |
|---|---|---|---|---|
| d4 opt | **0.602** | 0.732 | 0.824 | **0.972** |
| d4 regret | 0.422 | 0.282 | 0.192 | 0.028 |
| d4 optimal-set size | 7.1 | 12.3 | 16.0 | 18.2 |
| d2 opt | 0.958 | 0.928 | 0.896 | 0.832 |

- At depth 4 the **first decision is the hardest** (60% Q-optimal, regret 0.42,
  only ~7 Q-optimal candidates) and the **last decision is nearly free**
  (97%, regret 0.03, 18 optimal candidates).
- This **disfavours the compounding/covariate-shift hypothesis** (later steps are
  fine) and supports the **myopic-credit hypothesis**: the scorer is weakest
  exactly where a long-horizon value is needed and the choice is decisive.
- Depth 2 shows the opposite monotone decline (0.958 → 0.832), consistent with
  its near-saturated search: at d2 the decision-critical step is the first.

## Conclusion

The remaining deficit has two terms: **search breadth through decisive early
steps** (+30pp available cheaply) and **depth-aware credit at those steps**
(31pp at d4). The primitive target is therefore a value/credit operator over the
remaining budget, combined with search that keeps alternatives alive early.
Beam width is a usable proxy; a learned value is the candidate primitive.

Note on comparability: 0253 reported root Q-optimal 0.79–0.96 on 0252 bal
weights; 0254 measures 0.602 on retrained weights with the genuine-depth-4 scan
stream. The absolute value is fixture/weight dependent; the **early-hard /
late-easy profile is the new 5-seed observation**.

## Verification

```bash
cd /research/dlm_v0.0254/experiments/proof_state_transformer_maru && ./run.sh && ./verify.sh
cd /research/dlm_v0.0254 && ./scripts/verify_release.sh
```

New gates: beam coverage must be monotone in width; d2 W=25 ≥ 0.85; d4 W=25 ≥
0.45; the own-trajectory profile must increase over steps at d4 and its step-1
optimality must be below d2's. All 0251–0253 gates are retained.
