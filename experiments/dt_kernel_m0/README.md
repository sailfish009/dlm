# M0 — DT-1 real-dimension, integer-Q16 inference path

This is the M0 step of the deductive-transformer modification roadmap.

Goal: promote the compact v0.0237 array-view kernels to the **real DT-1
selector dimensions** and preserve the existing selector semantics:

- D=32, F=64, MAXTOK=64
- one weight-tied transformer block applied six times
- image token (196 bits) + one token per valid rule
- scalar per-rule head
- kNN head prior
- no positional encoding, bidirectional attention

M0 is **not** M1/M2/M3. It does not change the input semantics, the training
objective, or the selfssl loop.

## Files

```text
reference/dt_full_infer.c   frozen v0.0218 DT-1 reference
reference/dt_full_trace.c   same reference with TRACE instrumentation
reference/fixture_all.h     frozen Q16 fixture (MODEL_SIZE=15425)
src/dt_m0_infer.c           M0 candidate through the array-view ABI
run_m0.sh                   build and run all gates
verify_m0.sh                assert every gate
```

## Run

```bash
cd /research/dlm_v0.0238/experiments/dt_kernel_m0
./run_m0.sh
./verify_m0.sh
```

## Gates

```text
M0-BUILD-PASS
M0-SHAPE-PASS
M0-PICKS 10/10
M0-SEL-EXACT
M0-PICK-PARITY-PASS
M0-PROJ-PASS
M0-ATTN-PASS
M0-FFN-PASS
M0-LOOP1-PASS
M0-LOOP6-PASS
M0-O0/O2/O3-IDENTICAL yes
M0-NEGATIVE-PASS
M0-NO-DOUBLE yes
M0-INTEGER-ONLY yes
M0-PARITY-PASS
```

`M0-NEGATIVE-PASS` compiles the candidate with `M0_LAYERS=1`; its output must
not match the six-loop reference. This prevents a vacuous pass.

## What M0 establishes

- The real DT-1 dimensions fit the array-view ABI.
- One weight-tied block × 6 loops is preserved exactly.
- Projection, attention, FFN, and final head traces match the frozen reference
  byte-for-byte.
- The 10/10 picks and `SEL` values match the frozen reference exactly.
- O0/O2/O3 builds produce identical output.
- The candidate has no floating-point arithmetic in the inference path;
  `double` appears only in the `printf` conversion used to print `SEL`.

## Limits

- This is inference parity, not training parity.
- Weight-tied six-loop gradient flow is not verified here.
- `fixture_all.h` rules are ≤64-bit body masks; M1/M2 must use indexed
  retrieval or delegate admissibility to `p-prove`.
- The M0 tree is still based on the v0.0237 runtime/VERSION; it is a worktree
  candidate, not a promoted release.
