# DLM 0.0268 — corrected recombination claims (audit F1/F2/F3/F6) and the node-matched contract result

The 0267 audit reproduced every number and left four defects. All four are fixed
here, and two of the three claims in 0267 change.

## F1 — the label was still coupled to the evaluation budget

`rem = min(g_eval_budget - step, 4)` kept the coupling for every non-root state,
so `--eval-budget 6` produced a different label dataset. The gate only echoed the
config, so it passed. Fixed to `rem = label_rem - step` (label budget follows the
step, never the search budget).

Behavioural proof, same seed, budgets 4 and 6:

```text
b4:  pchk=8943.499165   census train top_share=0.559
b6:  pchk=8943.499165   census train top_share=0.559    (identical weights and labels)
```

The gate now trains under both budgets and requires identical parameter
checksums; it no longer reads a config line.

## F2 — the weight header did not carry the label definition

`label_ncost`, `label_steps`, `label_rem` are now part of `WHeader` and compared
on load. Cross-load tests in the gate:

```text
weights trained with LABEL_NCOST=1  ->  binary with LABEL_NCOST=0   exit 4
weights trained with label_rem=4    ->  run with --label-rem 3      exit 4
same configuration                                                  exit 0
```

(The initialiser order and the mismatch message had to be aligned with the struct;
both were wrong on the first attempt and are covered by these tests.)

## F3 — the ceiling was hardcoded, single-seed and unshipped

The runner now writes a per-seed contract-exhaustive ceiling (branch = POOL,
subsumption on) and the gate recomputes from those files:

```text
ceiling goal per seed 71..75: 0.9286  0.9365  0.9365  0.9444  0.9365   mean 0.9365
ceiling full per seed        : 0.9200  0.9300  0.9300  0.9400  0.9300   mean 0.9300
budget-6 bound (fixture)     : 1.0000 / 1.0000
```

The 0267 claim "D is at 95 % of the ceiling" was computed against a single seed.
Corrected: **D = 0.8825 is 94.2 % of the mean ceiling and below the per-seed
ceiling on every seed.**

## F6 — the guard gate did not check the exit code

`--eval-budget` above `MAXBUDGET` must exit 2 with `EVAL-BUDGET-FAIL`; the gate
now asserts both the message and the code.

## The matrix with the missing controls (5 seeds, 71–75, budget 4 unless noted)

```text
arm                    contractions  branch  budget  dfs      dfs_full   nodes
A_nocost               no            3       4       0.6841   0.6400     3006
A_b5                   no            5       4       0.7873   0.7500     7331
A_b6                   no            3       6       0.9826   0.9820     5427
B_pair16               yes           3       4       0.8079   0.7860     3070
C_pair64               yes (64)      3       4       0.8079   0.7860     3070
D_pair16_b5            yes           5       4       0.8825   0.8720     7236
E_pair16_e6            yes           3       6       0.9889   0.9880     5586
F (+integral)          yes           3       4       0.7825   0.7700     3159
G (+lifted)            yes           3       4       0.8349   0.8160     3194
H (+focus)             yes           3       4       0.8079   0.7860     3070
```

```text
B  − A        goal +0.1238  2se 0.0264  SIGNIFICANT   (contracts, branch 3)
A_b5 − A      goal +0.1032  2se 0.0254  SIGNIFICANT   (branch width alone)
D  − A_b5     goal +0.0952  2se 0.0214  SIGNIFICANT   (contracts at branch 5)
D  − B        goal +0.0746  2se 0.0185  SIGNIFICANT
E  − A_b6     goal +0.0063  2se 0.0059  detectable but negligible (0.6 pp)
C  − B        goal  0.0000              identical     (coverage saturates at 16)
```

### What changed in the reading

- The contract gain **survives a node-matched comparison**: D uses 7236 nodes and
  its own no-contract control A_b5 uses 7331 — D is 9.5 pp ahead at slightly
  fewer nodes. The 0267 caveat ("contract gain might be node cost") is withdrawn.
- The **branch-width** gain (+10.3 pp) remains node-unmatched (3× nodes) and is
  therefore a search-budget effect, not an efficiency claim.
- At **budget 6 the contract contribution collapses** from +12.4 pp to +0.6 pp
  (E − A_b6 = +0.0063, se1 0.0030: statistically detectable, practically
  negligible). E's 0.9889 is a budget effect — the no-contract arm already reaches
  0.9826 of the 1.0000 bound — so reporting E as a contract result would be wrong.
- The label (exact DP value, no cost) remains the basis: it is what makes A reach
  0.6841 with no contracts and no extra search, and every arm above is built on it.

## Gates (`verify_recomb0268.sh` → `V0268-RECOMB-PASS`)

```text
RECOMB-GRADCHECK   ten configurations
LABEL-INDEPENDENT  b4 and b6 training give identical pchk (behavioural, not config echo)
HEADER-LABELFLAGS  ncost / steps / label_rem cross-loads refused (exit 4), own accepted
BUDGET-LADDER      b4/b5/b6 under 30 s (memo-overflow regression)
BUDGET-GUARD       exit code 2 and EVAL-BUDGET-FAIL
CEILING             per-seed ceilings recomputed from artefacts; D <= ceiling on every seed
CLAIMS             B−A, A_b5−A, D−A_b5 significant; E−A_b6 reported as <2 pp (negligible)
AGG/WHDR/LLVM/DOC  as in 0.0267
V0268-RECOMB-PASS
```
