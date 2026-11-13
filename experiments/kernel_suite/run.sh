#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for O in 0 2 3; do
  clang -O$O -Iinclude src/kernels.c -o kernels_O$O -lm
done
./kernels_O0 > llvm/out_O0.txt
./kernels_O2 > llvm/out_O2.txt
./kernels_O3 > llvm/out_O3.txt
diff -q llvm/out_O0.txt llvm/out_O2.txt
diff -q llvm/out_O0.txt llvm/out_O3.txt
cat llvm/out_O0.txt
for O in 0 2 3; do
  clang -S -emit-llvm -O$O -Iinclude src/kernels.c -o llvm/kernels_O$O.ll
done
opt -O2 -S llvm/kernels_O0.ll -o llvm/kernels_O2_opt.ll
llc -O2 llvm/kernels_O2_opt.ll -o llvm/kernels_O2_opt.s
echo LLVM-MATRIX PASS O0/O2/O3
