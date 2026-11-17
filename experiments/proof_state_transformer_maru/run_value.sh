#!/usr/bin/env bash
# 0.0262: does a budget-exact DP value label replace single-step utility?
#
#   util    single-step kernel utility (all previous versions)
#   dp      budget-exact DP value V(mask, rem) from the kernel oracle
#   dpshuf  same DP label multiset, correspondence to candidates destroyed (control)
#   dplem   dp + hand-mined verified contracts (composition + value target)
#
# Identical transformer (19,939 params), protocol and search; fresh seed base 31..35.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_v
SEEDS="${SEEDS:-5}"; EPOCHS="${EPOCHS:-40}"
SEED_BASE="${SEED_BASE:-31}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 3 --subsume 1 --prop 1 --no-bound"

declare -A FLAGS=(
  [util]=""
  [dp]="-DVALMODE=1"
  [dpshuf]="-DVALMODE=2"
  [dplem]="-DVALMODE=1 -DLEMMA=1 -DPAIRMODE=1"
)
ORDER="util dp dpshuf dplem"
for a in $ORDER; do
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/v_$a" -lm
  mkdir -p "probes_v/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    s=$((SEED_BASE+i))
    "bin/v_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_v/$a/w_$s.bin" --no-bound > "probes_v/$a/train_$s.log" 2>&1
  done
  : > "probes_v/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    s=$((SEED_BASE+i))
    "bin/v_$a" --train --seeds 1 --seed-base "$s" $CFG $EVAL \
      --load-weights "probes_v/$a/w_$s.bin" >> "probes_v/$a/cfg_4_4.txt"
  done
done
PROBES=probes_v ARMS="util dp dpshuf dplem" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/value.txt
# the exact oracle ceiling at the same budget (kernel DP over the full candidate set)
"bin/v_dp" --dp-bruteforce-check --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 \
  --eval-budget 4 --goal-scan 2>&1 | tee out/dp_audit.txt | tail -1