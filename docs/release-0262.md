# DLM 0.0262 — budget-exact DP value labels

0.0246 named the open problem: the ranker is trained on single-step utility, so it
cannot plan a 2–3 step composition. 0.0261 showed that learning the *contract
proposal* pointwise does not beat random. 0.0262 replaces the label itself with an
exact value target and measures whether composition is internalised.

## Label

For a state with committed candidate mask `m` and remaining budget `b`:

```text
P(m)      = goals proved by closure(theory + m)                     [kernel]
V(m, b)   = max(P(m), max_{c ∉ m} V(m ∪ {c}, b-1))
label(c)  = V(m ∪ {c}, b-1) / |goals| * 5.0 - cost(c)
```

`V` is memoised over `(mask, remaining)`; every leaf is a kernel closure. State
space at the root is `C(22,≤4) = 9109` masks, so the label is affordable
(+1 s/epoch at 180 worlds). The label is an **oracle**, not a rollout: the gate
compares the memoised recursion against an independent no-memo brute-force
enumeration (`DP-AUDIT-SUMMARY checks=24 mismatches=0`).

## Arms (5 seeds, seed base 31–35, d4/b4)

```text
arm      greedy  beam    dfs     dfs_full  nodes  note
util     0.2953  0.3746  0.5095  0.4340    3506   single-step utility (all earlier versions)
dp       0.2905  0.3334  0.5318  0.4560    3584   exact DP value label
dpshuf   0.0508  0.0841  0.1746  0.1660    2763   same DP multiset, shuffled (control)
dplem    0.2905  0.3334  0.6540  0.6080    3450   dp + hand-mined verified contracts
```

Paired by seed (2 SE):

```text
dp     − util    goal  +2.2 pp ± 2.8   INCONCLUSIVE   beam −4.1 pp ± 2.0 (significant loss)
dplem  − util    goal +14.5 pp ± 2.4   significant
dplem  − dp      goal +12.2 pp ± 1.1   significant    full +15.2 pp ± 1.2
dp     − dpshuf  goal +35.7 pp ± 4.8   significant
```

## Verdict: DP-VALUE-NOT-DEMONSTRATED

The exact DP value label is **DP-VALUE-NOT-DEMONSTRATED** as a substitute for the
single-step utility target at this scale (+2.2 pp goal, inside 2 SE).

An exact, oracle-grade value label **does not** substitute for the missing
learning signal at this scale. `dp − util` is +2.2 pp goal and −4.1 pp beam: the
value head is slightly better on the DFS split and clearly worse under beam
search, and neither difference is attributable to label quality — the shuffled
control collapses to 0.17, so the model *does* use the labels; it simply does not
convert them into a better policy than a single-step target at 19,939 parameters,
40 epochs and ~500 states.

The one large effect is again the **action space**: adding hand-mined verified
2-rule contracts on top of the DP labels gives +12.2 pp over the same label and
+14.5 pp over the utility baseline (`dplem` = 0.654 goal / 0.608 full, the best
number measured in this line on a fresh seed base). Consistent with 0.0261, the
composition is carried by the symbolic actions, not by the value target.

Why the value label underperforms: the DP target is a *bounded-horizon optimum*
over the remaining candidate set, and it saturates — at a 4-step budget most
states admit a completion proving more goals than the single-step target
suggests, so the label becomes nearly flat across candidates and loses the
ordering information the loss needs. `dp` therefore learns a smoother but less
discriminative ranking. A dense advantage/regret target, or a value head over
sequences rather than per-candidate scalars, is the next attempt; it is not
implemented here.

## Gates (`verify_value.sh` → `V0262-DPVALUE-PASS`)

```text
DP-EXACT        memoised DP == brute-force enumeration (checks=24, mismatches=0)
VAL-LEARNED     shuffled DP labels collapse (+35.7 pp for the true correspondence)
VAL-TARGET      verdict token DP-VALUE-NOT-DEMONSTRATED required in this note
CONSERVATION    VALMODE=0 deterministic, no DP work on the utility path
AGG             table == per-seed recomputation; 10 mutations rejected
WHDR            value-label mode in the weight header; cross-label load refused
LLVM            O0/O2/O3 identical; ASan+UBSan clean
V0262-DPVALUE-PASS
```

## Scope

- 5 seeds (31–35), one unary fixture family, goal depth 4, eval budget 4, 40
  epochs, 180/60/100 worlds. The DP label is computed from the train split only.
- `dplem` uses hand-mined contracts (0.0260), not the learned proposer (0.0261),
  because the learned proposer was not demonstrated.
- The label is exact for the *commit-and-close* semantics used by the search; it
  is not a value function over the transformer's own belief state.
- Maru parity still covers only the transformer's initial-state scoring path.
