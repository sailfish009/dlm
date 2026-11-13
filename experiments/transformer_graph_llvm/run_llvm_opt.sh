#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for spec in 'E00 0 0 0' 'E01 1 0 0' 'E02 0 1 0' 'E03 0 0 1'; do
  set -- $spec; n=$1; a=$2; m=$3; b=$4
  clang -Wno-format -S -emit-llvm -O0 -I. -DINT_ATTN=$a -DINT_NORM=$m -DINT_BLOCK=$b dt_full_infer.c -o "llvm/${n}_base.ll"
  for opt in O2 O3; do
    opt -$opt -S "llvm/${n}_base.ll" -o "llvm/${n}_${opt}.ll"
    llc -O3 "llvm/${n}_${opt}.ll" -o "/tmp/${n}_${opt}.s"
    clang -no-pie "/tmp/${n}_${opt}.s" -o "/tmp/${n}_${opt}_opt"
    "/tmp/${n}_${opt}_opt" > "llvm/${n}_${opt}_opt.out"
    picks=$(awk '/RESULT/{printf "%s ",$10}' "llvm/${n}_${opt}_opt.out")
    if [ "$picks" = "211 45 2 22 61 61 34 76 16 5 " ]; then ok=PICKS-OK; else ok=PICKS-CHANGED; fi
    echo "$n $opt $ok ll=$(wc -l < "llvm/${n}_${opt}.ll") s=$(wc -l < "/tmp/${n}_${opt}.s")"
  done
done
