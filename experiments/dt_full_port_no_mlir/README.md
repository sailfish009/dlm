# dt_full_port_no_mlir (v0.0218)

DT-1 full inference on C/LLVM, plus a C/LLVM training prototype.

## Full inference

```bash
./run_full.sh
```

Current result:

```text
VALID 10/10
PICKS 10/10
PY_MAX_ERR 3.266330e-04
MARU_MAX_ERR 4.531251e-10
DT-FULL-INFER-C-PASS
```

The C selector reproduces the Maru Q16 selector exactly (within 5e-10) and
matches all PyTorch picks. The Maru proof status is taken from the preserved
v0.0204 10-case reference (`maru_main_10.out`); proof stays in Maru.

## Training prototype

```bash
./dt_train_c
```

`dt_train_c.c` implements (50 epochs, kNN prior at evaluation):

```text
Q16-float forward
6 transformer blocks
attention/softmax/layernorm backward
embedding backward
BCE loss
Adam
```

With the kNN head prior in evaluation and 50 epochs, it now matches all
reference picks:

```text
FOLD 0..9 picks: [211,45,2,22,61,61,34,76,16,5]
reference:       [211,45,2,22,61,61,34,76,16,5]
TRAIN_PICKS 10/10
DT-TRAIN-C-PICK-PARITY-PASS
```

The training backend is C/LLVM (float64 forward/backward/Adam); proof remains
Maru.

## Fixtures

- `fixture_all.py` → `fixture_all.h` (all 10 Q16 folds, cases, rules)
- `train_fixture.py` → `train_fixture.h` (compact training sequences/targets)
- `fixture_all.h`, `train_fixture.h` are preserved generated fixtures.

## Source references

DT reference:

```text
/research/dlm_v0.0204/experiments/deductive_transformer_maru
```

No MLIR is used.
