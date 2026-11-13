# Release 0.0237 — Maru Transformer + Deduction Kernel Suite

Candidate release for the native Q16 kernel suite.

## Scope

- Array-view matvec, batched matvec, softmax, layernorm
- Fused QKV attention + residual + layernorm
- Top-k / argmax / candidate ranking
- Valid-rule masking and bucket-chain candidate retrieval
- Proof-frontier closure and missing-frontier reporting
- BFS, Kahn topological sort, union-find, bitset transitive closure
- Incremental index add/remove with tombstones
- BCE, backward matvec, Adam, fused linear/ReLU, fused linear/LN
- Integrated transformer-ranked, proof-gated derivation
- O0/O2/O3 byte-identical execution; LLVM IR emission at O0/O2/O3, opt and llc

## Verification

```bash
cd /research/dlm_v0.0237/experiments/kernel_suite
./run_all.sh

cd /research/dlm_v0.0237
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```

Expected kernel gate:

```text
V0237-KERNEL-SUITE-PHASE11-PASS
LLVM-MATRIX PASS O0/O2/O3
```

Expected release gate:

```text
RELEASE-VERIFY-PASS version=0.0237 runtime=20261113T103714Z-24281
```

## Limits

- No MLIR toolchain; no linalg/vector lowering.
- Deduction kernels are tested on compact fixtures, not a large proof corpus.
- Transformer/deduction integration uses a compact rule-ranking fixture.
