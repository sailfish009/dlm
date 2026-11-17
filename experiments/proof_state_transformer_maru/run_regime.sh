#!/usr/bin/env bash
# 0.0264c (review F3): is the capacity null regime-dependent?
# Same capacity arms, but under the dplem regime (DP value label + verified
# contracts) that produced +14.5pp at 19,939 params. 15 seeds, base 51..65.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_cr
SEEDS="${SEEDS:-15}"; EPOCHS="${EPOCHS:-40}"; SEED_BASE="${SEED_BASE:-51}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 3 --subsume 1 --prop 1 --no-bound"
REG="-DVALMODE=1 -DLEMMA=1 -DPAIRMODE=1"
declare -A FLAGS=(
  [dplem]="$REG"
  [dplem_w48]="$REG -DMD=48"
  [dplem_b2max]="$REG -DBRANCHTOK=2 -DREADMAX=1"
)
arm_run () {
  local a="$1"; mkdir -p "probes_cr/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/rg_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_cr/$a/w_$s.bin" --no-bound > "probes_cr/$a/train_$s.log" 2>&1
  done
  : > "probes_cr/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/rg_$a" --train --seeds 1 --seed-base "$s" $CFG $EVAL \
      --load-weights "probes_cr/$a/w_$s.bin" >> "probes_cr/$a/cfg_4_4.txt"
  done
}
for a in dplem dplem_w48 dplem_b2max; do
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/rg_$a" -lm
done
for a in dplem dplem_w48 dplem_b2max; do arm_run "$a" & done
wait
PROBES=probes_cr ARMS="dplem dplem_w48 dplem_b2max" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/regime.txt
for a in dplem dplem_w48 dplem_b2max; do
  printf "REGIMEPARAM %-11s %s\n" "$a" "$(grep -h '^PARAMS' probes_cr/$a/cfg_4_4.txt | head -1 | awk '{print $2}')"
done | tee out/regime_params.txt
