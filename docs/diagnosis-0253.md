# 0253 diagnosis — the d4 collapse is composition, not expressibility

Measured on the genuine-depth-4 unary fixture (0252 bal weights, train d2/b4), budget-exact
reachability bound vs model, 3 seeds (11/12/13):

| quantity | seed 11 | seed 12 | seed 13 | meaning |
|---|---|---|---|---|
| bound_goal (reachability) | 0.849 | 0.849 | 0.849 | fraction of depth-4 goals reachable with budget 4 (seed-independent) |
| first-action opt | 0.96 | 0.79 | 0.83 | model's ROOT pick maximizes exact Q (a + 3 continuations) |
| first-action regret | 0.05 | 0.22 | 0.17 | maxQ − Q(chosen) at root |
| greedy coverage | 0.198 | 0.087 | 0.103 | model's sequential 4-step execution |
| beam coverage | 0.500 | 0.357 | 0.278 | external search over model scores |

BOUND-ASSERT ok=1, violations=0 (model never exceeds the reachability bound).

## Verdict (observed, 3 seeds)

1. **Not budget arithmetic.** Reachability bound = 0.849 ≫ model 0.13. The solution exists and is
   reachable at budget 4.
2. **Not single-step expressibility.** The model's FIRST action is Q-optimal 79–96% of the time.
   It can identify the right start and score candidates well.
3. **It is multi-step composition / plan execution.** Greedy sequential coverage collapses to ~0.13
   while the first action is ~0.86 optimal; external beam search recovers to ~0.38. The per-step
   signal exists but is not composed into a full derivation. This reproduces the 0248 finding
   ("depth gains come from state reachability and beam, not better first actions").

## Consequence for the primitive-discovery framing

- The user's primitive spec ("closure layer: apply rules to facts to fixpoint, L layers = L steps,
  β→∞ = kernel") targets **closure COMPUTATION**. The current lab is **budgeted SUBSET SELECTION /
  search**. These are different tasks. The measured d4 collapse is the SEARCH task, and it is a
  composition/credit failure — NOT evidence that closure is inexpressible.
- Therefore the closure-primitive hypothesis has NOT been tested yet. To test it faithfully, build a
  **closure-computation task** (facts + rules → fixpoint / goal derivability) on a **relational**
  fixture (the unary fixture's closure is a depth-≤6 per-entity Boolean circuit, trivially expressible).
- T3 "closure order sensitivity" is ill-posed: closure() is monotone chaotic iteration → confluent
  least fixed point (order-independent, proven). Order matters only for budgeted search credit.
- T2 binding needs the relational 2-variable fixture (current fixture is unary/per-entity, no joins).

## Corrected program

```
⓪ DONE: search-task collapse = composition (reachability .85, first-action .86, greedy .13, beam .38)
① build relational 2-variable fixture (binary preds, shared-variable join binding)
② closure-COMPUTATION task on it: facts+rules → fixpoint, depth ladder, β→∞ kernel-match gate
   -> THIS discriminates the closure primitive (stacked attention vs closure layer, L=depth)
③ candidates C1(join, not Sinkhorn-permutation)/C2/C3 on ②; matched-budget baselines
④ separately: search-composition primitive (working memory / goal stack / credit-over-depth)
   for the budgeted-search collapse — a DIFFERENT primitive than closure
```