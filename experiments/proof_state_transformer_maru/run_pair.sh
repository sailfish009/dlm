#!/usr/bin/env bash
# 0.0261: is the contract PROPOSAL learnable, or does the 0257/0260 gain depend on
# teacher-solution supervision?
#
#   pure    no contract actions (control)
#   mined   pairs read off teacher rollouts (0.0257/0.0260, hand-designed)
#   learn   linear pair scorer fitted on KERNEL labels sampled from random rollouts
#   rand    structurally valid pairs, matched count, no learning (control)
#
# All four arms: same transformer (19,939 params), same data protocol, same search
# budget, same contract budget (g_pair_keep=16 per state). Fresh seed base 21..25.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_p
SEEDS="${SEEDS:-5}"; EPOCHS="${EPOCHS:-40}"
SEED_BASE="${SEED_BASE:-21}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 3 --subsume 1 --prop 1 --no-bound"

declare -A FLAGS=(
  [pure]=""
  [mined]="-DPAIRMODE=1 -DLEMMA=1"
  [learn]="-DPAIRMODE=2 -DLEMMA=1"
  [rand]="-DPAIRMODE=3 -DLEMMA=1"
)
ORDER="pure mined learn rand"
for a in $ORDER; do
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/p_$a" -lm
  mkdir -p "probes_p/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    s=$((SEED_BASE+i))
    "bin/p_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_p/$a/w_$s.bin" --no-bound > "probes_p/$a/train_$s.log" 2>&1
  done
  : > "probes_p/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    s=$((SEED_BASE+i))
    "bin/p_$a" --train --seeds 1 --seed-base "$s" $CFG $EVAL \
      --load-weights "probes_p/$a/w_$s.bin" >> "probes_p/$a/cfg_4_4.txt"
  done
done
PROBES=probes_p ARMS="pure mined learn rand" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/pair.txt
# proposer sizes actually offered (diagnostic, not a gate)
grep '^PAIR-LEARN' probes_p/learn/train_*.log | sed 's/^/  /' | head -3