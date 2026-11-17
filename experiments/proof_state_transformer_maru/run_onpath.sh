#!/usr/bin/env bash
# 0.0264b: decide the width axis with 15 seeds (base / w48 / untied).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_o15
SEEDS="${SEEDS:-15}"; EPOCHS="${EPOCHS:-40}"; SEED_BASE="${SEED_BASE:-51}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 3 --subsume 1 --prop 1 --no-bound"
declare -A FLAGS=( [util]="" [dp]="-DVALMODE=1" [onpath]="-DVALMODE=3" [onpathlem]="-DVALMODE=3 -DLEMMA=1 -DPAIRMODE=1" )
arm_run () {
  local a="$1"; mkdir -p "probes_o15/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/o_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_o15/$a/w_$s.bin" --no-bound > "probes_o15/$a/train_$s.log" 2>&1
  done
  : > "probes_o15/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/o_$a" --train --seeds 1 --seed-base "$s" $CFG $EVAL \
      --load-weights "probes_o15/$a/w_$s.bin" >> "probes_o15/$a/cfg_4_4.txt"
  done
}
for a in util dp onpath onpathlem; do clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/o_$a" -lm; done
for a in util dp onpath onpathlem; do arm_run "$a" & done
wait
PROBES=probes_o15 ARMS="util dp onpath onpathlem" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/scale15.txt
