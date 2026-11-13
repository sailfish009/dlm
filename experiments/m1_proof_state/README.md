# M1 — proof-state set ranker (research adapter)

M1 changes the **input semantics** of the DT selector:

```text
M0:  image bits + rule features → rule pick
M1:  proof state + candidate action features → expected kernel utility
```

This is still a research adapter. The symbolic closure oracle produces the
labels; the ranker never decides truth.

## World

A finite propositional Horn world over 6 unary predicates and disjoint entity
splits. Candidate actions are Horn rules. Utility is measured on a sandbox copy
of the current theory:

```text
utility = 5 * newly-derived goal atoms
        + 0.15 * all newly-derived atoms
        - rule cost
```

Entities are split into disjoint train/val/test ranges. The ranker sees
proof-state and candidate features, never entity IDs or oracle utilities.

## Model

A tiny set transformer (PyTorch CPU, research only):

```text
state token + candidate tokens
→ 2 TransformerEncoderLayer blocks
→ scalar score per candidate
```

No positional encoding; the candidate set is permutation-invariant. This is the
architecture carried over from DT-1, but the token meaning is now proof state
and candidate actions.

## Run

```bash
cd /research/dlm_v0.0238/experiments/m1_proof_state
./run_m1.sh
```

The default runs 3 seeds on 180/40/40 worlds (120 epochs).

## Result

```text
M1-SEED-11 model=2.5462 hit=0.474 support=2.0053 prior=0.6241 random=-1.2195 shuffled=-0.7639
M1-SEED-12 model=2.8713 hit=0.537 support=2.2392 prior=-0.1257 random=-1.0034 shuffled=-0.7422
M1-SEED-13 model=2.7326 hit=0.474 support=1.9541 prior=-0.0611 random=-0.9378 shuffled=-0.7078
M1-MEAN model=2.7167 support=2.0662 prior=0.1457 random=-1.0536
M1-HELD-OUT-UTILITY-PASS
M1-PARITY-CONTROL-PASS
M1-PASS
```

Controls:

- `random`: random candidate.
- `prior_only`: mean utility by head predicate, learned on train only.
- `support_only`: hand-crafted body-support + goal-count heuristic.
- `untrained`: same architecture, random weights.
- `shuffled_features`: candidate feature rows permuted while labels stay in
  place; a permutation-equivariant model cannot hide this mismatch.

## Limits

- PyTorch is a research adapter, not the DLM core. A native Q16/C port is a
  later gate.
- Utility is synthetic; no real web text or Maru proof kernel is used here.
- M1 uses entity-held-out splits; relation-held-out splits are a later
  robustness gate.
- The ranker only proposes. Truth remains the symbolic closure/proof gate.
