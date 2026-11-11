# Deductive transformer — native Maru inference

Native Maru inference for the MNIST per-rule deductive transformer (DT-1).

```text
image facts
→ unifier-valid rule set
→ compact masked self-attention over [image] + valid rules (6 blocks)
→ selector logit + 4 · log P(head | image)   (k-NN, k=5, 190 images)
→ best valid rule
→ Maru p-prove / p-proof-check
```

Training remains PyTorch; Maru runs the complete inference and proof pipeline
using Q16 fixed point. No Python is called by `run.sh`.

## Files

```text
export_dt.py         train 10 LOCO selectors, export Q16 weights/data/rules
src/models.l         10 fold selectors (18 tensors each)
src/data.l           case bits, 190 kNN images/labels, rule heads/bodies
src/rules218.l       218 l-rules (109 real + 109 same-body decoys)
src/prior_table.l    log((count+1)/15) Q16 for kNN prior counts 0..5
src/fx.l             Q16 mul/div/sqrt/exp/softmax/layernorm
src/exp_table.l      exp(-i/32) table
src/dt.l             compact attention, selector, kNN, proof pipeline
src/main.l           10-case runner with scores and proof status
run.sh               Maru-only inference
verify.py/sh         compare against PyTorch exports
reference_folds.json PyTorch fold models: valid sets, logits, picks, correctness
verification.json    last verification result
```

## Why compact attention

The PyTorch reference uses a key-padding mask that excludes every invalid rule.
Therefore valid tokens attend only to the image and other valid tokens. Maru
computes exactly that compact set (usually 2 rules + image), avoiding the
O(219²) full vocabulary attention while preserving the masked model's result.

## Result (10 LOCO folds)

```text
valid rule sets:         10/10 match PyTorch
selected rules:          10/10 match PyTorch
selected heads:          10/10 match PyTorch
selector max abs error:  3.27e-4
proof gate:              10/10
held-out answer:         8/10
failures:                cases 0 and 6 (no correct valid rule)
```

## Commands

```bash
cd /research/dlm_v0.0204/experiments/deductive_transformer_maru
./run.sh        # native Maru inference + proof (~78 s)
./verify.sh     # full verification (~79 s)
python3 export_dt.py   # retrain/export (PyTorch, ~10 s)
```

Monitor command:

```bash
cd /research/dlm_v0.0204 && ./experiments/deductive_transformer_maru/verify.sh
```

## Limits

- **Inference only.** Selector training, mask learning and weight export are Python.
- The selector is a masked-attention DT-1 on 10 measured cases; this is not a
  general MNIST model.
- 8/10 is bounded by the two cases with no correct valid rule (0 and 6), not by
  numeric error. The Maru selector reproduces PyTorch logits to 3e-4.
- The k-NN head prior uses 190 non-measured MNIST images, as in the RE38 setup.
- No promotion; isolated experiment under `dlm_v0.0204`.

---

# Training in Maru (structure search)

The softmax attention selector cannot be trained in Maru (no autograd/float).
The experiment therefore replaces learned softmax attention with a **hard
unification mask** and trains the readout with an integer perceptron.

## Trainable variant

```text
image bits
→ valid rules by unification mask
→ rule token = head one-hot + body stats + sat
→ linear integer head readout w_d · image + b_d
→ perceptron update on misclassified images
→ proof gate on the selected rule
```

Files:

```text
src/learn.l       Maru perceptron training + hard-binding inference
src/curve.l       learning curve + no-mask ablation
src/rulelearn.l   LOCO structured perceptron over rule tokens
run_learn.sh      train 10 epochs, then run 10 cases + proof (~40 s)
run_curve.sh      epochs 1/3/5/10 + no-mask ablation (~80 s)
run_rulelearn.sh  LOCO rule perceptron (~6 min)
verify_learn.sh   training verification
```

Results:

```text
Maru-trained head readout, 10 epochs:  8/10 held-out, proof 10/10
Maru-trained rule-token perceptron:    8/10 LOCO
Learning curve (epochs):               1→7, 3→7, 5→6, 10→8
No mask:                               9/10 label, 1/10 proof-valid
```

The no-mask result is the key ablation: the mask, not the perceptron, is what
makes the rule application deductively valid. The proof gate rejects the
high-label-accuracy but invalid selections.

Caveat: training uses MNIST labels as observations. It is observation-supervised
and proof-gated, not label-free. The proof gate validates rule application, not
head truth.

Full analysis: `/research/analysis-deductive-transformer-maru-training.md`
