# DLM 0.0261 — is the contract proposal learnable?

0.0260 measured a +13.0 pp DFS goal gain from kernel-verified 2-rule contracts
and called them the effect. That result had a structural weakness: the contract
set was **hand-designed** (pairs read off teacher rollouts). The macro question
for this line is whether such composition structure can be *learned*. 0.0261
tests the proposal step directly, on a fresh seed base.

## Design

All four arms use the identical transformer (19,939 parameters), the identical
training protocol (180/60/100 worlds, `--collect full --sample sub`,
`--balance-reward`, 40 epochs, train d=2) and the identical search
(`--dfs --branch 3 --subsume 1 --prop 1`, eval d=4/b=4). Only the contract
proposer differs:

| arm | proposer | supervision |
|---|---|---|
| `pure` | none | – |
| `mined` | pairs read off teacher rollouts (0.0257/0.0260) | teacher action sequence |
| `learn` | linear scorer over 8 structural features, fitted by normal equations | **kernel labels only** (Δgoal + Δgoal-reachable atoms under closure), sampled from *random* rollouts |
| `rand` | structurally valid pairs, matched count, no learning | none |

Matching: `learn` and `rand` offer `g_pair_keep = 16` contracts per state from
the world's own ruleset; every contract is re-checked by the kernel at apply
time (`held && derived`), and a failed check is counted (`pair_viol`) instead of
being applied. Seeds 21–25 (new base, disjoint from 0.0259/0.0260's 11–15).

## Result (5 seeds, per-seed means, d4/b4)

```text
arm     dfs     dfs_full  nodes  pair_uses  pair_viol
pure    0.4683  0.3900    3553   0          0
mined   0.6302  0.5880    3519   479        0
learn   0.6778  0.6400    3437   887        0
rand    0.6841  0.6480    3444   922        0
```

Paired by seed (5 seeds, 2 SE verdict):

```text
learn − rand    goal  −0.6 pp ± 0.7   INCONCLUSIVE  (sign slightly negative)
learn − rand    full  −0.8 pp ± 0.9   INCONCLUSIVE
learn − mined   goal  +4.8 pp ± 1.4   significant, but see coverage note
rand  − mined   goal  +5.4 pp ± 1.9   significant, same coverage note
mined − pure    goal +16.2 pp ± 1.9   significant
learn − pure    goal +21.0 pp ± 3.1   significant
rand  − pure    goal +21.6 pp ± 3.4   significant
```

## Verdict: PAIR-LEARN-NOT-DEMONSTRATED

The learned contract proposer is **PAIR-LEARN-NOT-DEMONSTRATED**: the difference
from the matched random proposer is inside 2 SE over five seeds.

**The learned proposer does not beat a matched-count random proposer.** The
difference is inside 2 SE and, if anything, points the other way. Two facts
follow, and both matter for the programme:

1. **The 0.0260 contract gain is an action-space effect, not composition
   knowledge.** Adding kernel-verified 2-rule actions to the DFS raises goal
   coverage by +16…+22 pp with node count unchanged. Which pairs are chosen
   barely matters: 16 structurally valid, kernel-admissible contracts per state
   already capture the gain.
2. **The teacher-mined set is a coverage restriction, not a smarter set.**
   `mined` offers at most 64 pairs globally (479 uses/seed), the proposers offer
   16 per state (887–922 uses/seed). `learn`/`rand` beat `mined` by +5 pp
   because they cover more applicable pairs, not because they are better scored.
   This also re-reads 0.0257/0.0260: "verified contracts" was measured against a
   matched *search* budget but not a matched *contract-coverage* budget.

Why the learner fails here: the kernel label is sparse (positives ≈ 1,200 of
≈ 6,300 sampled pairs, 19 %; ≥1 goal-delta is rarer still), the linear scorer has
8 features, and the top-16 cut is insensitive to score order once the admissible
set is large (mean 24 candidate rules ⇒ ~350 structurally valid pairs per world).
A scalar pair score cannot separate 16 out of 350 with that signal.

The boundary is therefore confirmed in the direction the review anticipated:
**composition is supplied by a symbolic structure (verified contract actions),
and the proposal step at this granularity does not internalise it.** The next
test for the learning side is a budget-aware value target over *contract
sequences* (DP/rollout labels), not a pointwise pair score — that experiment is
not implemented here.

## Gates (`verify_pair.sh` → `V0261-PAIRLEARN-PASS`)

```text
PAIR-LABEL          label set non-empty, positives>0 every seed, weights non-degenerate
PAIR-BUDGET         pure applies 0 contracts; proposers apply >0; offers/state=16
PAIR-VERIFY         pair_viol=0 (kernel re-check at apply time)
PAIR-CLAIM          learn−rand inside 2SE => verdict token required in this note
AGG                 table == per-seed recomputation; 10 mutations rejected
WHDR                proposer mode in weight header; cross-proposer load refused
LLVM                O0/O2/O3 identical; ASan+UBSan clean
V0261-PAIRLEARN-PASS
```

## Scope

- 5 seeds on a fresh base (21–25), one fixture family (6 unary predicates, 24
  candidate rules, 3 goals), goal depth 4, eval budget 4.
- `learn` fits per seed, on the train split only, from random-rollout states; the
  model-independent state distribution avoids teacher coupling but is not the
  evaluation distribution.
- No relational fixture yet: the binding problem (which entity satisfies which
  premise) is trivial in a unary world, so contract coverage is artificially
  broad here. A relational fixture is the next required test for both `focus`
  and this proposer.
- Maru parity covers the transformer's initial-state scoring path (0.0246
  artifact); the contract machinery lives in the C/LLVM IR search.
