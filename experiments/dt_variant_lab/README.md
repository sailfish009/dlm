# dt_variant_lab (v0.0219)

Configurable DT-1 training variant lab, built on the v0.0218 C/LLVM port.

```bash
./run_lab.sh
```

The lab generates a variant-specific C trainer from the fixed v0.0218 baseline,
compiles it with clang, runs 10-fold LOCO training, and compares held-out picks
against `expected_all.json`.

## Supported config

```text
D              model width
F              FFN width
layers         number of transformer blocks
heads          currently 1 only
epochs         training epochs
lr             Adam learning rate
posw           BCE positive weight
prior_weight   0 disables kNN prior; 4.0 = baseline
```

## Results

```text
baseline            10/10  acc 8/10
baseline_seed62     10/10  acc 8/10
baseline_seed63      9/10  acc 8/10
d16_f32_l3          10/10  acc 8/10
d32_h2_l6           10/10  acc 8/10
d16_h2_l3           10/10  acc 8/10
d32_h4_l6            9/10  acc 8/10
d32_adamw_cos        9/10  acc 8/10
d32_dropout          9/10  acc 8/10
d32_f64_l6_noprior   4/10  acc 3/10
d32_f64_l3           9/10  acc 7/10
prior-only           9/10  acc 8/10
```

`PRIOR_SATURATED yes`: the prior-only control has the same ground-truth
accuracy as the full DT on this fixture, so this fixture cannot distinguish
transformer variants scientifically.

`d16_f32_l3` is a useful result: a much smaller model (D=16, F=32, 3 layers)
still reproduces all 10 held-out picks.

## Files

- `variant_lab.py` — config → generated C → compile → train → compare
- `configs/` — baseline and variant configs
- `variants/<name>/` — generated C, layout, binary, training output, result JSON
- `verify_lab.py` — baseline/variant gate
- `run_lab.sh` — full lab command

## Boundaries

- Training is C/LLVM float64; proof remains Maru.
- No PyTorch training.
- No MLIR.
- Multi-head is implemented in the generated C kernel.
- Eval-time dropout removed; train-time inverted scaling added.
- AdamW and cosine scheduler are implemented; scheduler uses a global step
  while Adam bias correction resets per fold.
- `T` is now `MAXV+1`; `L2_W` init uses `sqrt(F)`.
- `verify_lab.py` checks all picks lengths, seed variants, no-prior, prior-only,
  accuracy, and eval-dropout absence.
- Maru array-view wrapper is deferred.
