# DLM 0.0265 — the deductive signal: learning from justified derivations

## Framing correction this version answers

`design_20261110 §1.1` frames deductive learning as the **inverse of inductive
learning**: inductive learning maps `data+labels → gradient → θ`, and the target
is the structure on the other side of that map. Every axis tried in 0.0259–0.0264
(top-k attention, residual/path gate, multi-register readout, width, depth,
untied phases) changed similarity computation or capacity and kept the inductive
direction intact. The single *deductive* primitive already integrated — kernel
verified contract actions + certificates — is also where the only large positive
effect appeared. 0.0265 tests the deductive signal itself.

## L_proof_valid: label the justified derivation, not a scalar value

`0.0262` labelled each candidate with the exact value `V(mask∪{c}, rem−1)` and was
null because that value is flat: thousands of completions tie, so the ordering it
carries is weak. `0.0265` labels instead **membership in the optimal derivation
set, cost-aware**:

```text
V2(mask, rem) = (best goal count, MIN commits to reach it)     [kernel DP, lexicographic]
label(c)      = 5 · V2.value(mask∪{c}, rem−1)/|goals|
              + 0.5 · (1 − V2.steps(mask∪{c}, rem−1)/budget)
```

The first term says "this action lies on a derivation that proves the most goals";
the second says "prefer the derivation that needs fewer commits" (MDL / proof-cost).
Both come from the kernel closure; the teacher supplies nothing. The label is a
statement about *derivability*, which makes it the first deductive label in this
line.

Label sharpness, measured (`ONPATH census`, train split, 180 worlds):

```text
states=1360  top_label_cands=5494  mean_top=4.04  mean_nlive=22.50  top_share=0.180
```

18 % of candidates share the top label (4 of 22) — sharp enough to rank, in
contrast with the flat value label that put ~56 % at the top on shallow states.

## Result — 15 seeds (51–65), d4/b4, identical protocol and search

```text
arm         greedy   beam     dfs      dfs_full   nodes
util        0.2667   0.3370   0.4836   0.4140     3597
dp (value)  0.2778   0.3439   0.5370   0.4567     3598
onpath      0.3720   0.4365   0.6645   0.6147     3093
onpathlem   0.3720   0.4365   0.7910   0.7667     3121
```

Paired by seed (`se1` = standard error, `ci95` = 2 SE):

```text
onpath    − util   goal +0.1809  se1 0.0251  ci95 0.0501  SIGNIFICANT
onpath    − util   full +0.2007  se1 0.0288  ci95 0.0576  SIGNIFICANT
onpath    − util   greedy +0.1053 se1 0.0264 ci95 0.0528 SIGNIFICANT
onpath    − util   beam   +0.0995 se1 0.0313 ci95 0.0626 SIGNIFICANT
dp        − util   goal +0.0534  se1 0.0249  ci95 0.0497  SIGNIFICANT (barely)
onpath    − dp     goal +0.1275  se1 0.0249  ci95 0.0498  SIGNIFICANT
onpathlem − onpath goal +0.1265  se1 0.0085  ci95 0.0171  SIGNIFICANT
onpathlem − onpath full +0.1520  se1 0.0095  ci95 0.0190  SIGNIFICANT
onpathlem − util   goal +0.3074  se1 0.0211  ci95 0.0423  SIGNIFICANT
```

## Verdict: PROOF-PATH-LABEL-DEMONSTRATED

The deductive label is **PROOF-PATH-LABEL-DEMONSTRATED**: +18.1 pp goal and
+20.1 pp full-world success over single-step utility at 15 seeds, all contrasts
beyond 2 SE, and — unlike the capacity experiments — it also moves the *scorer*
itself, not only the search: the greedy policy (no backtracking) gains
+10.5 pp and beam gains +10.0 pp. The model's ranking improved, not just the
search around it.

Two further readings:

- **The label, not capacity, was the missing piece.** Same 19,939 parameters,
  same data, same search. `dp → onpath` (+12.8 pp) isolates the difference
  between a flat value target and a justification-membership target.
- **Deductive primitives compose.** On top of `onpath`, kernel-verified contract
  actions add +12.7 pp goal / +15.2 pp full with a tight interval (±1.7), giving
  0.791 goal / 0.767 full — the best measured configuration in this line.

## What this does and does not establish

| claim | status |
|---|---|
| a derivation-membership label beats a value label and utility | established, 15 seeds, 2 SE |
| the scorer itself improves (greedy/beam), not just the search | established |
| deductive signal + deductive action space stack | established (±1.7) |
| capacity is the lever | refuted again inside this regime (0.0264c: +1.3 pp ±5.2) |
| the *loop-structured* cell (state transition inside the forward) works | **not tested** — this version changes the signal, not the graph |
| hard binding / relational world | **not tested** — unary fixture, binding trivial |
| the label is obtainable without a kernel oracle at train time | **no** — it uses the exact DP on train worlds; test-world states are scored from features only |

## Gates (`verify_onpath.sh` → `V0265-ONPATH-PASS`)

```text
ONPATH-GRADCHECK  four label regimes pass finite differences (label-only change)
ONPATH-LABEL      census non-degenerate (top_share in (0,1)) and reported
CONSERVATION      VALMODE=0 is bit-identical to a re-run (label path inert when off)
CONTRAST          onpath−util significant at 2 SE on goal *and* greedy (scorer effect)
AGG               table == per-seed recomputation; 10 mutations rejected
WHDR              value-label mode in the header; cross-label load refused
LLVM              O0/O2/O3 identical; ASan+UBSan clean
DOC               release notes are prose (no shell residue)
V0265-ONPATH-PASS
```

## Next (unchanged priorities from the corrected plan)

1. **A — looped proof-step cell**: move the state transition *inside* the
   forward (soft commit between shared blocks). This is a forward/backward
   refactor (per-step `lnf`/`h` caches, per-step embedding backward); the
   gradcheck gate already exists to police it.
2. **C — hard binding × relational world**: with binding non-trivial, `onpath`
   should sharpen further and `bind` becomes measurable.
3. **B' — sequence/advantage targets**: now that a path-membership label is the
   strongest signal, the sequence version (label over action *sequences*) is the
   natural next step on the same axis.
