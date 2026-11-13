# M3 — selfssl ranker seam

M3 connects the learned ranker to the symbolic admission/rollback loop:

```text
rank one candidate
→ kernel gate (utility > 0 and conflict == 0)
→ admit or rollback / abstain
→ next proof state becomes the next input
```

The ranker only proposes. The symbolic closure gate decides admission.

## Controls

```text
model            learned score
random           random candidate
prior            head-predicate utility prior
support          hand-crafted body-support heuristic
no_mask          model score but conflict gate disabled
```

## Result (3 test seeds)

```text
M3-SEED-21 goal=0.504 closure=0.079 support_goal=0.450 support_closure=0.079 false=0.0 no_mask_false=0.05 invalid_accepted=0
M3-SEED-22 goal=0.508 closure=0.066 support_goal=0.354 support_closure=0.050 false=0.0 no_mask_false=0.025 invalid_accepted=0
M3-SEED-23 goal=0.562 closure=0.080 support_goal=0.433 support_closure=0.064 false=0.0 no_mask_false=0.05 invalid_accepted=0
M3-MEAN goal=0.525 support=0.412 random=0.104
M3-SELFSSL-SEAM-PASS
M3-FALSE-INJECTION-0
M3-CLOSURE-GAIN-OVER-CONTROLS-PASS
M3-HELD-OUT-GOAL-RECOVERY-PASS
M3-INVALID-HIGH-SCORE-BLOCKED-PASS
M3-PASS
```

## Run

```bash
cd /research/dlm_v0.0238/experiments/m3_selfssl
./run_m3.sh
```

## Limits

- The ranker remains a PyTorch research adapter.
- One proposal per round; rejection is abstention/rollback, not a search.
- The no-mask control injects forbidden atoms, as intended.
- `invalid_probe` directly tests the gate, not the ranker's top-1 choice.
