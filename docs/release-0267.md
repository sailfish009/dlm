> **Correction (0.0268/0.0269, audit F1/F2/F3/F6):** the claim that labels were
> independent of the evaluation budget was false (`rem = min(eval_budget - st, 4)`);
> the weight header did not carry the label flags; the 0.9286 ceiling was
> single-seed and hardcoded (5-seed mean is 0.9365, D = 94.2 %). The node-matched
> control (A_b5) shows the contract gain survives (D − A_b5 = +9.5 pp at 7236 vs
> 7331 nodes). E's 0.9905 below became 0.9889 once the F1 fix changed eval-time
> contract mining at budget 6 (LEMMA-MINE unique 64 → 47); trained parameters
> were unchanged. Corrected numbers and gates: `docs/release-0268.md`.

# DLM 0.0267 — recombination of the working parts, and the label-DP budget fix

Two things happened here: a build defect in the label DP was found and fixed by an
independent audit (the `--eval-budget 6` hang), and a recombination matrix over the
parts that already work produced the best budget-4 configuration in this line.

## Fix: the label DP was coupled to the evaluation budget

`dp_labels()` used `rem = g_eval_budget - step`, so an `--eval-budget 6` run built a
label dataset over `C(22,<=6) = 110,056` DP keys against a 32,768-cell memo with a
64-slot linear probe. The table overflowed silently and every miss fell back to
exponential recomputation: budget 4 `<1 s`, budget 5 `9 s`, budget 6 `> 90 s`.

Three changes:

1. the label budget is now independent of the search budget (`--label-rem`, default
   4): labels are defined at budget 4, where the ceiling was measured, and a search
   at budget 6 no longer changes the training data;
2. `DPMEMO` 32,768 → 1,048,576 cells, probe 64 → 256;
3. memo overflow is **counted** (`LABELMEMO ... store_fail=`) instead of silently
   degrading, and `--eval-budget` above `MAXBUDGET` fails loudly instead of
   segfaulting (budget 7 did).

Timing after the fix (<1 s at every budget on the smoke fixture, `store_fail=0`):

```text
budget 4: 317 ms   budget 5: 386 ms   budget 6: 457 ms
```

## Recombination matrix (5 seeds, 71–75, label = exact DP value, no cost)

```text
arm                   greedy   beam     dfs      dfs_full   nodes
A nocost              0.3889   0.4698   0.6841   0.6400     3006
B + pair16            0.3889   0.4698   0.8079   0.7860     3070
C + pair64            0.3889   0.4698   0.8079   0.7860     3070
D + pair16, branch 5  0.3889   0.4698   0.8825   0.8720     7236
E + pair16, budget 6  0.9032   0.9333   0.9905   0.9900     5641
F + pair16, integral  0.3587   0.4222   0.7825   0.7700     3159
G + pair16, lifted    0.4222   0.4667   0.8349   0.8160     3194
H + pair16, focus     0.3889   0.4698   0.8079   0.7860     3070
```

```text
B − A  goal +0.1238  se1 0.0132  2se 0.0264  SIGNIFICANT
B − A  full +0.1460  se1 0.0201  2se 0.0403  SIGNIFICANT
D − B  goal +0.0746  se1 0.0092  2se 0.0185  SIGNIFICANT
D − B  full +0.0860  se1 0.0121  2se 0.0242  SIGNIFICANT
C − B  goal  0.0000                          identical (coverage saturates at 16)
F − B  goal −0.0254  se1 0.0277  2se 0.0553  inconclusive (negative direction)
G − B  goal +0.0270  se1 0.0287  2se 0.0574  inconclusive (positive direction)
H − B  goal  0.0000                          focus removes nothing at budget 4
```

## Ceilings, measured (this is where 0.0266 was wrong)

```text
no-contract bound, subsets <= 4 rules          0.8492 goal / 0.8200 full
exhaustive DFS WITH contract actions, b4
  (branch = POOL, subsumption on, seed 71)     0.9286 goal / 0.9200 full
no-contract bound at budget 6                  1.0000 goal / 1.0000 full
```

The 0.0266 note compared contract-using arms against the *no-contract* bound
(0.8492). That is not an upper bound for an action space in which one slot commits
two rules — arm D (0.8825) legitimately exceeds it. The correct reference for the
contract arms is the exhaustive contract-action DFS: D reaches **95 %** of it, B
**87 %**. At budget 6 the fixture is nearly saturated (E = 0.9905 against 1.0000).

## Verdict

- The recombination that pays is **contracts + wider branching** (D): +19.8 pp goal
  over the label-only arm and +7.5 pp over the same contracts at branch 3, both
  beyond 2 SE. D is the best budget-4 configuration measured in this line.
- Contract **coverage** saturates at keep=16 (C ≡ B): a wider proposal set adds
  nothing, consistent with 0.0261's coverage interpretation.
- The feature add-ons remain inconclusive (integral negative, lifted positive,
  focus vacuous at budget 4). They are not part of the working configuration.
- Budget is the dominant remaining lever: budget 6 leaves 1 % of the ceiling, so
  further gains at budget 4 must come from search efficiency, not from learning.

## Caveat on D

D consumes 2.4× the nodes of B (7236 vs 3070). The gain is "more search per world at
a wider branch factor", not a proven efficiency gain. A node-matched comparison
(B and D at equal node budgets) is the correct next measurement for that claim.

## Gates (`verify_recomb.sh` → `V0267-RECOMB-PASS`)

```text
RECOMB-GRADCHECK   eight arms pass finite differences
LABEL-BUDGET       labels are built at budget 4 for any eval budget; store_fail=0
BUDGET-LADDER      b4/b5/b6 all under 30 s on the smoke fixture (overflow regression)
BUDGET-GUARD       eval budget above MAXBUDGET exits with EVAL-BUDGET-FAIL
CEILING            D <= contract-exhaustive ceiling; E <= budget-6 bound
RECOMB-CLAIM       B−A and D−B significant at 2 SE; C≡B reported as saturation
AGG/WHDR/LLVM/DOC  same checks as 0.0266
V0267-RECOMB-PASS
```
