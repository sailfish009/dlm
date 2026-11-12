#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for spec in 'E00 0 0 0' 'E01 1 0 0' 'E02 0 1 0' 'E03 0 0 1' 'E04 1 1 0' 'E05 1 0 1' 'E06 0 1 1' 'E07 1 1 1'; do
  set -- $spec; n=$1; a=$2; m=$3; b=$4
  clang -O3 -I. -DPRIOR_WEIGHT=0 -DINT_ATTN=$a -DINT_NORM=$m -DINT_BLOCK=$b dt_full_infer.c -o "p0_$n"
  "./p0_$n" > "p0_$n.out"
done
