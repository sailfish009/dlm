# DLM 0.0263 — multi-register transformer (Screamer branching inside the model)

0.0259/0.0260 changed only the readout (top-k attention, residual gate). 0.0263
changes the **token set**: the single state token becomes `B` state registers, and
each candidate reads from all of them. With `READMAX=1` every register gets its
own output head and the candidate score is the **max over registers** — a
differentiable stand-in for Screamer's "one surviving branch decides".

## Structure

```text
base     L = 1 + nlive     tokens: [state] + candidates       19,939 params
b2       L = 2 + nlive     two state registers                20,199 params
b2max    B=2, per-register output head, score = max_b head_b    20,199 params
b3max    B=3, same readout                                     20,199 params
b2shuf   B=2, ONE shared register bias and head (duplicate-token control)
```

Registers are `state_embedding + Rbias[b]`; the gradient of the max readout is
routed to the winning register's head, and the register bias gradient comes from
the attention path. `param_count()` excludes the register block when the
structure is off, so `base` stays at exactly 19,939 parameters.

## Result (5 seeds, seed base 41–45, d4/b4)

```text
arm      greedy  beam    dfs     dfs_full  nodes
base     0.2809  0.3286  0.4794  0.3880    3632
b2       0.2746  0.3143  0.4905  0.4060    3654
b2max    0.2889  0.3317  0.4921  0.4080    3608
b3max    0.2476  0.3032  0.4556  0.3780    3630
b2shuf   0.2619  0.3143  0.4730  0.3920    3689
```

Paired by seed (2 SE):

```text
b2max − base    goal  +1.3 pp  (inside 2 SE)
b3max − base    goal  −2.4 pp  (inside 2 SE)
b2    − base    goal  +1.1 pp  (inside 2 SE)
b2max − b2      goal  +0.2 pp  (per-register heads add nothing over a shared head)
b2shuf− b2      goal  −1.8 pp  (duplicate-token control is not better either)
```

## Verdict: MULTIREG-NOT-DEMONSTRATED

Multi-register branching is **MULTIREG-NOT-DEMONSTRATED** as an architecture gain:
the best arm is +1.3 pp goal, inside 2 SE at five seeds.

Branching inside the model does not move coverage. Two registers are as good as
three, per-register heads add +0.2 pp over a shared head, and the duplicate-token
control lands in the same band. The +1.3 pp is inside noise at 5 seeds, and the
larger register count is slightly negative.

This is the third architectural axis that fails to reproduce the contract effect:
sparse attention (0.0259), residual/path gating (0.0260), and now multi-register
branching (0.0263). The pattern is consistent: **the transformer's internal
readout has little headroom left on this fixture; the gain sits in the action
space and in search.**

## Gates (`verify_reg.sh` → `V0263-MULTIREG-PASS`)

```text
REG-GRADCHECK   five configurations, incl. the max readout and register bias
REG-OFF         BRANCHTOK=1 bit-identical to base (plumbing inert when off)
REG-PARAMS      base = 19,939 parameters
REG-CLAIM       verdict token required in this note
AGG             table == per-seed recomputation; 10 mutations rejected
WHDR            register configuration in the weight header; cross-load refused
LLVM            O0/O2/O3 identical; ASan+UBSan clean at B=3
V0263-MULTIREG-PASS
```

## Scope

- 5 seeds (41–45), one unary fixture family, d4/b4 evaluation, 40 epochs.
- Capacity is not matched across arms (19,939 vs 20,199, +1.3 %); the register
  arm is slightly larger, so the null result is not an artifact of a smaller model.
- The max readout is a subgradient of a piecewise-linear function; gradcheck
  confirms it away from ties, and the shared-head control (b2shuf) is used to
  avoid the tie pathology entirely.
