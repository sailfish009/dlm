#!/usr/bin/env bash
# 0.0264: capacity scaling of the native transformer (width x depth x untied phases).
# Arms differ ONLY in model size; data, epochs, search, seeds are identical.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_c
SEEDS="${SEEDS:-5}"; EPOCHS="${EPOCHS:-40}"
SEED_BASE="${SEED_BASE:-51}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 3 --subsume 1 --prop 1 --no-bound"
declare -A FLAGS=(
  [base]=""
  [w48]="-DMD=48"
  [d3]="-DMNL=3"
  [w48d3]="-DMD=48 -DMNL=3"
  [untied]="-DVAR_LOOP=1 -DPHASEUNTIE=1"
)
ORDER="base w48 d3 w48d3 untied"
arm_run () {
  local a="$1"; mkdir -p "probes_c/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/c_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_c/$a/w_$s.bin" --no-bound > "probes_c/$a/train_$s.log" 2>&1
  done
  : > "probes_c/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/c_$a" --train --seeds 1 --seed-base "$s" $CFG $EVAL \
      --load-weights "probes_c/$a/w_$s.bin" >> "probes_c/$a/cfg_4_4.txt"
  done
}
for a in $ORDER; do clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/c_$a" -lm; done
for a in $ORDER; do arm_run "$a" & done
wait
PROBES=probes_c ARMS="$ORDER" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/scale.txt
for a in $ORDER; do
  p=$(grep -h '^PARAMS' probes_c/$a/cfg_4_4.txt | head -1 | awk '{print $2}')
  printf "SCALEPARAM %-7s %s\n" "$a" "$p"
done | tee out/scale_params.txt
