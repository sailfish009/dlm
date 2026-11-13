#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
mkdir -p llvm out
# LLVM matrix + opt-level byte identity (seed 777)
for O in 0 2 3; do
  clang -O$O -Iinclude src/icredit.c -o llvm/icredit_O$O -lm
  ./llvm/icredit_O$O > out/O$O.txt
done
diff -q out/O0.txt out/O2.txt
diff -q out/O0.txt out/O3.txt
for O in 0 2 3; do
  clang -S -emit-llvm -O$O -Iinclude src/icredit.c -o llvm/icredit_O$O.ll
done
opt -O2 -S llvm/icredit_O0.ll -o llvm/icredit_O2_opt.ll
llc -O2 llvm/icredit_O2_opt.ll -o llvm/icredit_O2_opt.s
echo "LLVM-MATRIX PASS O0/O2/O3"
# multi-seed results
for S in 777 778 779; do
  clang -O0 -DSEED=$S -Iinclude src/icredit.c -o llvm/icredit_s$S -lm
  ./llvm/icredit_s$S > out/seed$S.txt
done
# Maru ground-closure parity oracle
"$ROOT/maru-compiler" "$ROOT/src/maru/boot.l" "$ROOT/src/dlm/logic.l" \
  "$ROOT/src/dlm/infer.l" "$ROOT/src/dlm/deduce.l" "$ROOT/src/dlm/proof.l" \
  src/parity.l > out/maru_parity.txt
cat out/maru_parity.txt
echo "RUN-DONE"