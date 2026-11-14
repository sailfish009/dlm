#!/usr/bin/env bash
# 2x2: teacher state collection (root-only vs full budget) x features
# (aggregate vs goal-binding preserving). Updates are matched: every arm trains
# on the same number of samples per epoch; --sample sub draws those samples from
# every collected state, --sample root from the root state only.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out
SEEDS="${SEEDS:-5}"
EPOCHS="${EPOCHS:-40}"
build () { clang -O2 -DHARD_GOALS=1 "$@" src/pst.c -Iinclude -Isrc -o "bin/$1x" -lm 2>/dev/null || true; }
clang -O2 -DHARD_GOALS=1 -Iinclude -Isrc src/pst.c -o bin/pst_hard_agg -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc src/pst.c -o bin/pst_hard_relob -lm
run () { # arm binary collect sample name
  ./"$2" --train --seeds "$SEEDS" --epochs "$EPOCHS" --train-n 180 --val-n 60 --test-n 100 \
    --collect "$3" --sample "$4" > "out/2x2_$1.txt"
  grep '^MEAN' "out/2x2_$1.txt" | sed -E "s/^MEAN variant=base fixture=hard seeds=$SEEDS /$1 /" | cut -c1-190
}
run A_root_agg    bin/pst_hard_agg   root root
run B_full_agg    bin/pst_hard_agg   full sub
run C_root_relob  bin/pst_hard_relob root root
run D_full_relob  bin/pst_hard_relob full sub
run E_full_all    bin/pst_hard_relob full all
