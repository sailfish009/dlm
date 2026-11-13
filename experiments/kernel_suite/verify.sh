#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^MATVEC PASS' run.out || { echo 'matvec failed'; exit 1; }
grep -q '^BATCH PASS' run.out || { echo 'batch failed'; exit 1; }
grep -q '^SOFTMAX PASS' run.out || { echo 'softmax failed'; exit 1; }
grep -q '^LAYERNORM PASS' run.out || { echo 'layernorm failed'; exit 1; }
grep -q '^FUSED-ATTENTION PASS' run.out || { echo 'fused attention failed'; exit 1; }
grep -q '^TOPK PASS' run.out || { echo 'topk failed'; exit 1; }
grep -q '^MASK PASS' run.out || { echo 'mask failed'; exit 1; }
grep -q '^INDEX PASS' run.out || { echo 'index failed'; exit 1; }
grep -q '^FRONTIER PASS' run.out || { echo 'frontier failed'; exit 1; }
grep -q '^FRONTIER-MISSING PASS' run.out || { echo 'frontier missing failed'; exit 1; }
grep -q '^BFS PASS' run.out || { echo 'bfs failed'; exit 1; }
grep -q '^TOPO PASS' run.out || { echo 'topo failed'; exit 1; }
grep -q '^UNION-FIND PASS' run.out || { echo 'union-find failed'; exit 1; }
grep -q '^BITSET-CLOSURE PASS' run.out || { echo 'bitset closure failed'; exit 1; }
grep -q '^INDEX-UPDATE PASS' run.out || { echo 'incremental index failed'; exit 1; }
grep -q '^BCE PASS' run.out || { echo 'bce failed'; exit 1; }
grep -q '^BACKWARD-MATVEC PASS' run.out || { echo 'backward matvec failed'; exit 1; }
grep -q '^ADAM PASS' run.out || { echo 'adam failed'; exit 1; }
grep -q '^LINEAR-RELU PASS' run.out || { echo 'fused linear/relu failed'; exit 1; }
grep -q '^LINEAR-LN PASS' run.out || { echo 'fused linear/ln failed'; exit 1; }
grep -q '^INTEGRATE PASS' run.out || { echo 'integration failed'; exit 1; }
grep -q '^PROOF-GATE PASS' run.out || { echo 'proof gate failed'; exit 1; }
grep -q '^LLVM-MATRIX PASS' run.out || { echo 'LLVM matrix failed'; exit 1; }
echo 'MATVEC/BATCH/SOFTMAX/LAYERNORM/FUSED/TOPK/ARGMAX/MASK/INDEX/FRONTIER/BFS/TOPO/UF/CLOSURE/UPDATE/BCE/BACKWARD/ADAM/LINEAR/INTEGRATE/PROOF-GATE PASS'
echo 'LLVM-MATRIX PASS'
echo 'V0237-KERNEL-SUITE-PHASE12-PASS'
