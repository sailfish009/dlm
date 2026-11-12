# v0.0218 — DT full port without MLIR: status

## Inference: PASS

Full 10-case/fold selector ported to C/LLVM.

```text
VALID 10/10
PICKS 10/10
PY_MAX_ERR 3.27e-4
MARU_MAX_ERR 4.53e-10
```

The C Q16 selector matches the Maru Q16 selector essentially exactly and
matches all PyTorch picks. Proof/admission remains the Maru reference
(`maru_main_10.out`); no C kernel is allowed to certify truth.

## Training: PASS (selector parity)

`dt_train_c.c` has a full forward/backward/Adam implementation. With the kNN
head prior in evaluation and 50 epochs, held-out picks match the reference:

```text
C:         [211,45,2,22,61,61,34,76,16,5]
reference: [211,45,2,22,61,61,34,76,16,5]
TRAIN_PICKS 10/10
DT-TRAIN-C-PICK-PARITY-PASS
```

This is C/LLVM numeric training; proof remains Maru. It is not yet a Maru
array-view primitive.

## Next work

1. Align C training features/scale with the exported Q16 model.
2. Gradient-check attention, layernorm and softmax backward.
3. Match PyTorch initialization/dropout/mask semantics.
4. Re-run 10-fold LOCO and compare picks to `reference_folds.json`.
5. Keep proof gate in Maru.

## No MLIR

No MLIR toolchain, dialect, or linalg/vector lowering is used or claimed.
