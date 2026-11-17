# Release 0.0253 — expressibility diagnosis + closure-primitive discrimination (negative)

- Date: 2026-11-15
- Predecessor: 0.0252 (preserved)
- Type: candidate research release
- Runtime: `20261114T001318Z-27176` (reused; Maru core unchanged)

## Reframing (user)
The goal is to DISCOVER a primitive operation for deductive learning (the attention-analogue),
not to modify the transformer. Discriminating tasks must come before candidate architectures.
This release tests the leading candidate — the "closure layer" — and reports an honest negative.

## 1. Diagnosis: the d4 collapse is composition, not expressibility (observed, 3 seeds)
On the genuine-depth-4 unary fixture (0252 bal weights), budget-exact bound vs model:
- reachability bound = **0.849** (solution exists → not budget arithmetic)
- first-action Q-optimal = **0.79 / 0.96 / 0.83** (model picks the right start → not single-step expressibility)
- greedy coverage = 0.198 / 0.087 / 0.103 ; beam = 0.500 / 0.357 / 0.278
=> per-step signal exists but is not COMPOSED into a derivation. The collapse is in budgeted
SEARCH / plan-execution, not closure expressibility. (docs/diagnosis-0253.md)

## 2. Grounded corrections to the prior "closure layer" plan
- `closure()` is monotone chaotic iteration → confluent least fixed point (order-INDEPENDENT,
  proven + self-check 0 violations). "T3 closure-order sensitivity" is ill-posed; order matters
  only for budgeted search credit. HyperSSM non-commutativity (2611.17162) is about sequence
  tracking, misapplied to closure.
- The unary fixture is per-entity propositional (closure = depth-≤6 Boolean circuit, trivially
  expressible, no binding). Binding needs a relational fixture; binding = join/equality, NOT
  Sinkhorn permutation.

## 3. Closure primitive: sound + expressible + differentiable (apparatus verified)
`experiments/relational_closure_maru`:
- `rc.c`: relational 2-variable fixture (binary preds, composition rules h(X,Z):-b1(X,Y),b2(Y,Z)),
  monotone join closure + BFS depth. SELF-CHECK confluence 0 + hand-transitive PASS; genuine-depth
  census d2-d4 feasible.
- `rc_model.c`: closure layer (softmin-AND + softmax-OR + monotone max; hard min/max).
  KERNEL-MATCH 10800 atoms 0 violations (β→∞ == kernel, SOUND); DEPTH-SCALING 0 mismatch
  (hard L layers == depth≤L, constructive expressibility); GRADCHECK max_abs 6e-9; training converges.
- `rc_chain.c`: chain reachability + primitive length-scaling (solves L=2..10 with ≤4 layers) + MLP baseline.
- `rc_attn.c`: stacked-attention baseline (entity tokens, L=3 D=32, 20033 params), GRADCHECK 1.3e-5.

## 4. Discrimination: NEGATIVE result (observed, 3 difficulty levels)
Chain reachability, train L=2..4 → test L=6..10 (length extrapolation), primitive=1.000 constructive:

| decoy (branching) | attention train | test_short | test_long |
|---|---|---|---|
| 0 (single path) | 1.000 | 1.000 | **1.000** |
| 20 | 1.000 | 0.860 | **0.935** |
| 40 | 1.000 | 1.000 | **0.995** |

**A small stacked attention learns closure computation and extrapolates length essentially
perfectly.** The closure primitive is sound and expressible but provides NO meaningful advantage.
The flat MLP baseline cannot even learn the short task (train 0.62, permutation-sensitive) and is
uninformative. (docs/closure-discrimination-0253.md)

## 5. Conclusion and pivot
- Closure COMPUTATION is not the discriminating task; attention already suffices. The "closure
  layer" is not an attention-grade discovery.
- The measured failure lives in budgeted SEARCH / COMPOSITION (working memory / goal stack /
  credit-over-depth / plan execution). That is the next primitive-discovery target (0254).
- No p-hacking: three pre-distinguishable difficulty levels were tested; the conclusion is the
  observed null, not a tuned positive.

## Verification
`cd experiments/relational_closure_maru && ./run.sh && ./verify.sh` → `V0253-CLOSURE-PRIMITIVE-NEGATIVE-PASS`.
Gates: kernel confluence + hand-transitive; primitive KERNEL-MATCH/DEPTH-SCALING/SOFT-SANITY;
gradchecks (primitive 6e-9, attention 1.3e-5); primitive length-scaling; O0/O2/O3 identity; ASan+UBSan.
Release gate: `bash scripts/verify_release.sh` → `RELEASE-VERIFY-PASS version=0.0253`.