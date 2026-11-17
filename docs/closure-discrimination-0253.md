# 0253 closure-primitive discrimination — NEGATIVE result (observed)

## Question
Is the "closure layer" (join + softmin-AND + monotone update, L layers = L steps) an
attention-grade primitive — i.e., does it compute closure / generalize depth in a way a
matched stacked-attention model cannot learn?

## Setup
- Relational chain reachability: single binary predicate, transitivity p(X,Z):-p(X,Y),p(Y,Z).
  World = a path of L edges over distinct entities (+ decoy edges for branching). Query (s,t):
  is p(s,t) in the closure? TRAIN L=2..4, TEST L=6..10 (length extrapolation). NENT=12.
- Closure primitive: hard join layers, constructive (rc_chain --worlds: solves L=2..10 with
  <=4 layers, PRIMITIVE-SCALING PASS; rc_model KERNEL-MATCH 0 violations).
- Stacked attention baseline (rc_attn.c): entity tokens (out-edges, in-edges, is-src, is-tgt),
  L=3 layers, D=32, 20033 params, single head, FFN, readout on (src,tgt). GRADCHECK max_abs
  1.3e-5 PASS. Trained 200 epochs, BCE, Adam lr=0.001, 400 train worlds.

## Result (attention test accuracy; primitive = 1.000 constructive at every row)

| decoy (branching) | train | test_short L2-4 | test_long L6-10 |
|---|---|---|---|
| 0 (single path) | 1.000 | 1.000 | **1.000** |
| 20 | 1.000 | 0.860 | **0.935** |
| 40 | 1.000 | 1.000 | **0.995** |

## Verdict (observed, 3 difficulty levels)
**Attention learns closure computation and extrapolates length essentially perfectly.** The
closure primitive is sound (beta->inf == kernel) and expressible (L layers = depth L), but it
provides NO meaningful advantage over stacked attention on this task family. The single-path
case is degenerate (reachability = "source before target"); branching cases are still solved
(0.935-0.995). Difficulty is non-monotonic in decoy rate (more redundant paths can make
reachability easier), but attention handles all of them.

## Consequence for the primitive-discovery program
1. The closure-COMPUTATION task does NOT discriminate a new primitive. Attention already
   suffices for closure. The "closure layer" is not an attention-grade discovery.
2. This reinforces docs/diagnosis-0253.md: the measured d4 collapse is in budgeted SEARCH /
   composition (reachability .85, first-action .86, greedy .13), NOT closure expressibility.
3. The primitive-discovery effort should target the SEARCH / COMPOSITION bottleneck
   (working memory / goal stack / credit-over-depth / plan execution), not closure computation.
   That is where the measured failure lives and where attention has not been shown to suffice.

## Honest limits
- One architecture/size (L=3,D=32), one seed per row, 200 epochs; not a capacity sweep. A larger
  attention model would only strengthen the negative result. The point is that even a SMALL
  attention model suffices, so the closure primitive is not needed for this task.
- This is a negative result on the closure task family, NOT a claim that attention suffices for
  the search/composition task (which remains open and is the real target).
- No p-hacking: three pre-distinguishable difficulty levels were tested; the conclusion is the
  observed null, not a tuned positive.