# v0.0219 — Configurable DT variant lab

## What changed

The fixed v0.0218 C trainer is now a template. `variant_lab.py` substitutes
D/F/layers/epochs/lr/posw/prior weight, generates a variant-specific parameter
layout, compiles with clang, runs 10-fold LOCO training, and compares picks.

## Results

| variant | D | F | layers | prior | picks |
|---|---:|---:|---:|---:|---:|
| baseline | 32 | 64 | 6 | 4.0 | 10/10 |
| d16_f32_l3 | 16 | 32 | 3 | 4.0 | 10/10 |
| d32_h2_l6 | 32 | 64 | 6 | 4.0 | 10/10 |
| d16_h2_l3 | 16 | 32 | 3 | 4.0 | 10/10 |
| d32_h4_l6 | 32 | 64 | 6 | 4.0 | 9/10 |
| AdamW+cos | 32 | 64 | 6 | 4.0 | 9/10 |
| input dropout .1 | 32 | 64 | 6 | 4.0 | 9/10 |
| no prior | 32 | 64 | 6 | 0 | 4/10 |
| l3 | 32 | 64 | 3 | 4.0 | 9/10 |

The `d16_f32_l3` result shows the small model is sufficient for this fixture.
Removing the kNN prior drops to 4/10; the prior-only probe reaches 9/10 parity
and the same 8/10 ground-truth accuracy as the full DT. Therefore the fixture
is **prior-saturated** and variant differences are not scientifically
informative; a harder fixture is required.

## Gate

```text
V0219-VARIANT-LAB-PASS
```

## Limits

- Multi-head 1/2/4 tested.
- AdamW weight decay, cosine scheduler, and input dropout are tested variants.
- Dropout is input-token dropout, not a full PyTorch layer-dropout clone.
- No Maru array-view wrapper yet.
- No MLIR.
