#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
mkdir -p llvm out

# LLVM matrix + opt-level byte identity (12 seeds, all arms, all diagnostics)
for O in 0 2 3; do
  clang -O$O -Iinclude src/icredit.c -o llvm/icredit_O$O -lm
  ./llvm/icredit_O$O > out/O$O.txt
done
diff -q out/O0.txt out/O2.txt
diff -q out/O0.txt out/O3.txt
echo "LLVM-MATRIX PASS O0/O2/O3"
for O in 0 2 3; do
  clang -S -emit-llvm -O$O -Iinclude src/icredit.c -o llvm/icredit_O$O.ll
done
opt -O2 -S llvm/icredit_O0.ll -o llvm/icredit_O2_opt.ll
llc -O2 llvm/icredit_O2_opt.ll -o llvm/icredit_O2_opt.s

# Maru oracles: hardcoded 6-atom toy + two GENERATED 40-atom worlds
"$ROOT/maru-compiler" "$ROOT/src/maru/boot.l" "$ROOT/src/dlm/logic.l" \
  "$ROOT/src/dlm/infer.l" "$ROOT/src/dlm/deduce.l" "$ROOT/src/dlm/proof.l" \
  src/parity.l > out/maru_parity.txt
cat out/maru_parity.txt
./llvm/icredit_O0 --emit-maru > out/episode.l
"$ROOT/maru-compiler" "$ROOT/src/maru/boot.l" "$ROOT/src/dlm/logic.l" \
  "$ROOT/src/dlm/infer.l" "$ROOT/src/dlm/deduce.l" "$ROOT/src/dlm/proof.l" \
  out/episode.l src/parity-world.l > out/maru_world.txt
cat out/maru_world.txt
echo "RUN-DONE"