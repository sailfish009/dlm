# Release 0.0249 — input representation vs the deduction-cell hypothesis

- Date: 2026-11-14
- Predecessor: 0.0248 (preserved)
- Type: candidate research release (variant experiment with the 0.0248 criteria)
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

## Question

The alternative hypothesis to a binding+AND deduction cell is: *general attention
learns the same computation when it is given the same inputs.* 0.0249 tests that
directly by handing the existing set transformer the **exact binding inputs** a
cell would consume (`-DBINDTOK=1`): per premis slot × entity support (2×6) and
per-entity head-atom status (6). Same architecture, same optimizer budget, same
reward-balanced exposure.

## Arms (3 seeds, train d=2/b=4 balanced, same weights evaluated on the ladder)

| config | aggregate | relation (RELOB) | relation + binding tokens |
|---|---|---|---|
| d2 b4 | 0.4797 | **0.7826** | 0.7630 |
| d3 b4 | 0.1768 | **0.4663** | 0.4628 |
| d4 b4 | 0.0711 | 0.1645 | **0.1896** |
| d2 b6 | 0.7573 | **0.9413** | 0.9239 |
| d4 b6 | 0.4015 | **0.6444** | 0.5778 |
| regret d2 (opt) | 0.130 (87.4%) | 0.092 (90.8%) | 0.102 (90.0%) |
| regret d4 (opt) | 0.270 (75.4%) | 0.198 (80.4%) | 0.168 (83.2%) |

## Result

- **Input representation is the first-order factor.** Relation features beat
  aggregate features by +0.24 at d4/b6 and +0.30 at ID.
- **Binding tokens as iid features do not substitute for a structured cell.**
  Adding them to the relation arm changes d4/b6 by **−0.067 goal** (−0.013 beam)
  and ID by −0.020; the only cell where they lead is d4/b4 (0.190 vs 0.165).
  The general-attention arm that receives the cell inputs is not better on the
  structural shift that matters.
- Regret decomposition: at depth 4 the binding-token arm has the lowest
  first-step regret (0.168 vs 0.198 relation, 0.270 aggregate) yet the lowest
  d4/b6 coverage among the relation arms. First-action quality and end-to-end
  coverage move in opposite directions here, which is why both are reported.

This is evidence *against* "just give attention the binding tokens" at this
scale. It supports trying an explicit binding→AND→update cell, and it also says
what that cell must beat: the relation arm's 0.6444 at d4/b6, with a matched
parameter and update budget, and it must move the **regret** numbers, not only
coverage.

## Caveats

- `bindtok` widens the input (44 → 62 candidate features) with 180 training
  worlds; part of the loss may be overfitting rather than structure. A matched
  parameter/feature-count control is required before using this as a clean
  falsification.
- The cell itself (binding+AND+shared repeat) is **not implemented** here;
  `capabilities.json` keeps `bounding_and_shared_repeat_cell: not-implemented`.
- 3 seeds; CIs conditional on the fixed generator.

## Verification

```bash
cd /research/dlm_v0.0249/experiments/proof_state_transformer_maru && ./run.sh && ./verify.sh
cd /research/dlm_v0.0249 && ./scripts/verify_release.sh
```

New gate: relation features must beat aggregate features by ≥10pp at d4/b6; the
binding-token arm is reported with its sign (exploratory, no directional gate).
