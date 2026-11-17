#!/usr/bin/env bash
# 0.0263: multi-register transformer (Screamer state branching inside the model).
#
#   base    one state token, one output head (all earlier versions, 19,939 params)
#   b2      B=2 state registers, shared output head
#   b2max   B=2 registers + per-register head, score = max over registers
#   b3max   B=3 registers + per-register head, max readout
#   b2shuf  B=2 registers, ONE shared register bias and head (duplicate-token control:
#           same token count and parameter block, no distinct branch parameters)
#
# Identical protocol and search; fresh seed base 41..45. Arms are trained in
# parallel (one core each) because the lab is independent per arm.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_r
SEEDS="${SEEDS:-5}"; EPOCHS="${EPOCHS:-40}"
SEED_BASE="${SEED_BASE:-41}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 3 --subsume 1 --prop 1 --no-bound"

declare -A FLAGS=(
  [base]=""
  [b2]="-DBRANCHTOK=2"
  [b2max]="-DBRANCHTOK=2 -DREADMAX=1"
  [b3max]="-DBRANCHTOK=3 -DREADMAX=1"
  [b2shuf]="-DBRANCHTOK=2 -DREADMAX=1 -DREGSHUF=1"
)
ORDER="base b2 b2max b3max b2shuf"

arm_run () { # arm
  local a="$1"
  mkdir -p "probes_r/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/r_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_r/$a/w_$s.bin" --no-bound > "probes_r/$a/train_$s.log" 2>&1
  done
  : > "probes_r/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/r_$a" --train --seeds 1 --seed-base "$s" $CFG $EVAL \
      --load-weights "probes_r/$a/w_$s.bin" >> "probes_r/$a/cfg_4_4.txt"
  done
}

for a in $ORDER; do
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/r_$a" -lm
done
for a in $ORDER; do arm_run "$a" & done
wait
PROBES=probes_r ARMS="$ORDER" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/register.txt
for a in $ORDER; do
  printf "PARAMS %-7s %s\n" "$a" "$(grep -h '^PARAMS' probes_r/$a/cfg_4_4.txt | head -1 | awk '{print $2}')"
done | tee out/register_params.txt