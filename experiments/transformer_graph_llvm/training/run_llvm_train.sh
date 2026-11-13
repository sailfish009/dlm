#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for n in 0 1 2; do
  clang -Wno-format -S -emit-llvm -O0 -DINT_CREDIT=$n -I. dt_train_c.c -o "credit_${n}_base.ll"
  opt -O2 -S "credit_${n}_base.ll" -o "credit_${n}_O2.ll"
  llc -O3 "credit_${n}_O2.ll" -o "/tmp/credit_${n}_O2.s"
  clang -no-pie "/tmp/credit_${n}_O2.s" -o "/tmp/credit_${n}_llvm" -lm
  "/tmp/credit_${n}_llvm" > "credit_${n}_llvm.out"
  p=$(awk '/PICK/{printf "%s ",$4}' "credit_${n}_llvm.out")
  [ "$p" = "211 45 2 22 61 61 34 76 16 5 " ] && ok=PICKS-OK || ok=PICKS-CHANGED
  echo "CREDIT $n $ok ll=$(wc -l < "credit_${n}_O2.ll")"
done
