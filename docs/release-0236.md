# Release 0.0236 — Transformer Graph IR × LLVM IR Variant Matrix

- Date: 2026-11-13
- Predecessor: 0.0235
- Type: candidate research release
- Runtime: `20261113T100319Z-20309`

## What changed

- Added `experiments/transformer_graph_llvm/`:
  - explicit 14-node transformer block graph;
  - graph checks, CSE/DCE and topology variants;
  - LLVM IR lowering for E00–E03 at O0/O2/O3, opt/llc;
  - structural training graph and LLVM IR training credit 0/1/2;
  - proof-path integral credit reuse;
  - invalid-edge and cycle graph controls.
- Added the graph/LLVM variant matrix to the source manifest.

## Results

```text
GRAPH ok NODES 14 EDGES 17
CSE 14 DCE 14
LLVM PICKS-OK 8/8
LLVM-OPT PICKS-OK 8/8
TRAIN-GRAPH ok NODES 5 EDGES 6
LLVM-TRAIN PICKS-OK 3/3
G-SHARED/GATED/PROOF ok
PROOF-PATH-INTEGRAL credit ok
BAD-EDGE/CYCLE rejected
V0236-GRAPH-LLVM-STAGE5-PASS
```

## Verification

```bash
cd /research/dlm_v0.0236/experiments/transformer_graph_llvm
./run_all.sh
```

and:

```bash
cd /research/dlm_v0.0236
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```

## Limits

- Graph is an explicit structural model; only the base block graph is
  executable.
- LLVM IR is produced by clang from C/Q16 source, not graph-to-IR lowering.
- Graph topology variants are structural probes.
- Training graph is structural; LLVM training kernels are C-derived.
- No MLIR.
