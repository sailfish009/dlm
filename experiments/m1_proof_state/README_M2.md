# M2 — kernel-utility objective

M2 extends M1 from "closure gain" to a three-part utility on a sandbox copy:

```text
Δclosure  : all newly derived atoms
ΔMDL      : rule cost
conflict  : newly derived forbidden atoms (hard penalty)
```

Candidate admission label:

```text
admit = 1 iff the candidate derives a goal and injects no forbidden atom
```

Hard negatives are candidates whose bodies are already supported but which
derive a forbidden atom.

## Model

`model_m2.py`: the same set transformer with two heads:

```text
utility score  +  admission logit
```

Training combines listwise utility cross-entropy, top-1 pairwise loss, and
admission BCE.

## Result

```text
M2-SEED-21 top1=1.1496 hit=0.458 support=-0.7083 conflict_reject=0.935 hard_reject=0.847 f1=0.642
M2-SEED-22 top1=0.3250 hit=0.246 support=-1.8201 conflict_reject=0.894 hard_reject=0.738 f1=0.518
M2-SEED-23 top1=0.7865 hit=0.278 support=-1.1396 conflict_reject=0.912 hard_reject=0.778 f1=0.500
M2-MEAN top1=0.7537 support=-1.2227 conflict_reject=0.914 f1=0.553
M2-UTILITY-LABEL-PASS
M2-PAIRWISE-RANK-CORR-PASS
M2-CONFLICT-REJECT-PASS
M2-HELD-OUT-ENTITY-PASS
M2-ADMISSION-BCE-PASS
M2-PASS
```

## Run

```bash
cd /research/dlm_v0.0238/experiments/m1_proof_state
./run_m2.sh
```

## Limits

- Entity-held-out, not yet relation-held-out.
- Research PyTorch adapter; no native Q16 training.
- Conflict is a synthetic forbidden-atom set, not full paraconsistent proof.
