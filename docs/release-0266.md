# DLM 0.0266 — where the label gain comes from (review N1–N4)

0.0265 reported +18.1 pp goal / +20.1 pp full from a "proof-path membership"
label and attributed it to the *justification content* and its sharpness. An
independent audit found that attribution unsupported (N1, N2) and asked for four
measurements. All four are done here; the attribution changes.

## N1 — the census was read from the evaluation run

The gate read `LABELCENSUS`/`ONPATH` from `probes_*/cfg_4_4.txt`, i.e. a
`--goaldepth 4` *evaluation* run, while the weights were trained on
`--goaldepth 2` labels. Measured values differ:

```text
train run  (goaldepth 2): states=1360  mean_top=11.65  top_share=0.518
eval  run  (goaldepth 4): states=1360  mean_top= 4.04  top_share=0.180
```

The "0.180 vs 0.563" sharpness story is therefore withdrawn: 0.563 was also an
evaluation-run number from the wrong arm. The census is now emitted per split
(`LABELCENSUS ... split=train|val|test`) and read from the **training** log by the
gate.

## N2 — the label differences were confounded; no shuffle control

0.0265's label changed two things relative to the DP value label: it added a
min-derivation-length term and it dropped the `−rule_cost` term. A 2×2
decomposition plus the missing shuffle control (15 seeds, 51–65) separates them:

```text
arm          value  length  cost   dfs      dfs_full   train top_share
dp            yes     no     yes   0.5370   0.4567     0.175
dp_steps      yes    yes     yes   0.5397   0.4607     0.175
dp_nocost     yes     no      no   0.6614   0.6113     0.524
onpath        yes    yes      no   0.6645   0.6147     0.524
onpathshuf    yes    yes      no   0.3460   0.3073     0.524  (labels shuffled)
```

```text
dp_nocost − dp        goal +0.1243  se1 0.0257  2se 0.0514  SIGNIFICANT
dp_nocost − dp        full +0.1547  se1 0.0280  2se 0.0559  SIGNIFICANT
dp_nocost − dp        greedy +0.0958 se1 0.0260 2se 0.0521 SIGNIFICANT (scorer effect)
dp_steps  − dp        goal +0.0026  se1 0.0026  2se 0.0053  inconclusive (length term is inert)
onpath    − dp_nocost goal +0.0032  se1 0.0032  2se 0.0063  inconclusive
onpath    − onpathshuf goal +0.3185 se1 0.0375 2se 0.0750  SIGNIFICANT (correspondence is used)
```

### Corrected mechanism

The gain is carried by **dropping the rule-cost penalty from the label**, not by
"justification membership" and not by sharpness — the winning label is the *less*
sharp one (top_share 0.524 vs 0.175). The min-derivation-length term contributed
+0.3 pp, i.e. nothing, because on this fixture an optimal derivation usually
consumes the whole remaining budget, so the term is nearly constant.

Interpretation: `−rule_cost` charges every candidate for the cost of *committing*
it, but a rule that is needed two steps later is not "expensive" in the same
sense. The penalty therefore biases the target against multi-step derivations —
the same composition bias that made single-step utility weak. Removing it leaves
the exact value term, which already ranks progress correctly.

This is a label-engineering result. It is **not** yet evidence about deductive
*structure*: the graph is unchanged in 0.0265/0.0266.

## N3 — the interval label

`ci95=` was 2·SE, not a 95 % t-interval. With n=15, t₀.₉₇₅,₁₄ = 2.1448, and the
`dp − util` contrast had t = 2.1446 — exactly at the p≈0.05 boundary. The tool now
prints `2se=` and the earlier table's "SIGNIFICANT (barely)" reading is
`p ≈ 0.05`, not "clearly significant".

## N4 — the ceiling at this protocol

Measured on the 100 test worlds with the budget-exact bound (the same DP used for
the labels, enumerating all rule subsets of size ≤ 4):

```text
bound_goal = 0.8492   bound_full = 0.8200   (bound-assert ok, pairs=100)
bound_goal = 0.8492 on seeds 51, 52, 53   (the scan makes the test fixture identical)
```

So `onpathlem` (0.791 goal / 0.767 full) is at **93 % / 94 % of the exact
reachable ceiling**; the remaining headroom on this fixture and protocol is
**5.8 pp goal / 5.3 pp full**. With paired `se1` of 0.85–2.1 pp any further
architectural effect (A, the looped cell) must be larger than ~2–4 pp to be
detectable here, and cannot exceed 5.8 pp. That frames the next gate.

## Gates (`verify_decomp0266.sh` → `V0266-LABELDECOMP-PASS`)

```text
DECOMP-GRADCHECK  five label regimes (incl. shuffled) pass finite differences
CENSUS-TRAIN      the census the gate reads comes from the training log, per split
SHUFFLE-CONTROL   onpath − onpathshuf significant at 2 SE (correspondence used)
COST-LOCALISATION dp_nocost − dp significant; dp_steps − dp inert
CEILING           bound measured and reported; best arm below it
AGG/WHDR/LLVM/DOC same checks as 0.0265
V0266-LABELDECOMP-PASS
```

## Consequence for the plan

1. The label axis is now understood: value term + no cost penalty is the working
   signal; the "justification" framing was wrong and is retracted.
2. The remaining headroom is ≤5.8 pp on this fixture, which makes a *structural*
   test (A, looped proof-step cell) hard to read unless the fixture changes.
   This strengthens C (relational world) as the prerequisite for A, not a
   substitute: with binding non-trivial the ceiling rises and both the label and
   the loop have room to show an effect.
3. Any future claim about mechanism must name the term it changed; the 2×2 runner
   and the shuffle control are now part of the gate suite.
