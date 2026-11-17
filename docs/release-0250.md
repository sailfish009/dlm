# Release 0.0250 — matched-width control for the binding-token experiment

- Date: 2026-11-14
- Predecessor: 0.0249 (preserved)
- Type: candidate research release (control repair)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

## Why

0.0249 handed the set transformer the binding inputs a deduction cell would
consume (`-DBINDTOK=1`) and observed a drop at d4/b6. That arm also widened the
candidate vector from 44 to 62 features on 180 training worlds, so the drop could
be width/overfitting. 0.0250 adds the control: `-DBINDTOK=2` keeps the same 18
extra features but applies a **per-rule entity shift**, preserving row sums and
marginal statistics while destroying the correspondence to the actual premise
and goal entities.

## Arms (3 seeds, train d=2/b=4 balanced, same weights on the ladder)

| config | relation (44) | aligned binding (62) | shifted binding (62, control) |
|---|---|---|---|
| d2 b4 | **0.7826** | 0.7630 | 0.7645 |
| d4 b6 | **0.6444** | 0.5778 | 0.6222 |
| beam d4 b6 | **0.7570** | 0.7437 | 0.7012 |

## Result

- **The 0.0249 drop is a width effect.** Both 62-feature arms fall below the
  44-feature arm at d4/b6, and the *aligned* binding tokens are **worse than
  their scrambled control** (0.5778 vs 0.6222; in a separate standalone sweep
  0.5037 vs 0.6296).
- Aligned-minus-shifted is −0.044 goal at d4/b6 (−0.012 at ID). No evidence that
  giving general attention the aligned binding tokens helps; no clean evidence
  that it hurts *because of the binding*. Run-to-run spread of the 44-vs-62 gap
  is 0.022–0.059, so the gate uses the stable sign with a 0.01 margin.
- The alternative hypothesis ("general attention suffices with the same inputs")
  therefore stays **open** at this fixture: the honest statement is that the
  unary fixture cannot separate the two hypotheses, because the AND step is
  informationally identical to `support` and the binding variable is a single
  entity.

This is a negative-control result that revises 0.0249's interpretation. It does
not support the explicit cell either; it says the unary fixture has no headroom
for a binding-specific mechanism.

## Implication for the next experiment

The discriminating test needs a **2-variable relational fixture** (binary
predicates, variable patterns in rules, multiple eligible bindings per rule),
where choosing *which binding* is a real decision and the kernel mask cannot be
summarised by a support count. Until then, a binding+AND cell comparison on this
fixture measures width and optimisation noise.

## Verification

```bash
cd /research/dlm_v0.0250/experiments/proof_state_transformer_maru && ./run.sh && ./verify.sh
cd /research/dlm_v0.0250 && ./scripts/verify_release.sh
```

New gates: relation-44 must beat both 62-feature arms by ≥0.03 at d4/b6; the
aligned-minus-shifted contrast is reported with its sign. Exposure control,
ladder, regret, 2×2, validator and Maru gates are unchanged.
