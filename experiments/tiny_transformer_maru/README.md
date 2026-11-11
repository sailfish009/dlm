# Tiny transformer — Maru Q16 inference port

Port of `/research/tiny-transformer-from-scratch/transformer.py` (2-layer
encoder-decoder, D=32, 2 heads, 8 English→Chinese sentences) to **native Maru**.

## Scope

- **Inference only.** Training remains PyTorch; weights are exported as Q16.
- No float, tensor, matmul, softmax, `sqrt`/`exp`/`sin`/`cos`, or autograd in Maru.
- Q16 means `real = integer / 65536`; integer `bitwise-shift` is used for mul/div.
- Positional tables and the `exp` table are precomputed and stored as constants.
- Attention uses explicit loops; softmax uses a 514-entry `exp(-i/32)` table with
  linear interpolation.
- Greedy decoding, 16 steps max.

## Artifacts

```text
reference.py        PyTorch reference (train / save / greedy)
checkpoint.pt       trained reference weights (seed 42, 100 epochs)
export_weights.py   Q16 S-expression export
src/weights.l       exported tensors (126 tensors, 45,964 params)
src/exp_table.l     exp table for softmax
src/fx.l            Q16 kernels (mul/div/sqrt/exp/softmax/layernorm)
src/transformer.l   encoder/decoder/attention/FFN + greedy decode
src/main.l          runs all 8 sentences
src/dump.l          encoder/logit dump for numerical verification
src/fxtest.l        exact kernel tests
verify.py           compares Maru against PyTorch
run.sh              run all 8 sentences
verify.sh           full verification (kernels, numerics, translations)
reproduce.sh        retrain → export → verify
```

## Results

```text
greedy translations: 8/8 exact
encoder max abs error: 8.16e-4 (max over 8 cases)
first-step logits max abs error: 1.81e-3 (max over 8 cases)
first-step logit argmax: 8/8 cases
kernel checks: 7/7
Maru dump deterministic: yes
```

Runtime: about 70 s for full verification (Maru-native execution);
`./run.sh` alone takes about 50 s.

## Commands

```bash
cd /research/dlm_v0.0204/experiments/tiny_transformer_maru
./run.sh                 # print 8 translations
./verify.sh              # full verification, writes verification.json
./reproduce.sh           # retrain from scratch, export, verify
```

Override the Maru binary with `MARU=/path/to/maru`.

## Limits

- This is a **port of inference**, not a Maru-native training implementation.
- Q16 arithmetic is approximate; translations are exact for this tiny model but
  no general error bound is claimed.
- Attention is O(T²·D); the current dimensions are tiny. This is a demonstration,
  not a performance-oriented transformer runtime.
- The model/task is the upstream toy translation task, not MNIST and not DLM
  deductive learning.
