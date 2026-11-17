#!/usr/bin/env bash
# 0.0270 relational-fixture structure matrix (design-components-0269.md plan).
# Same label (kernel DP, no cost), same episode trainer, same search (branch 5,
# budget 4), 5 seeds 71-75. No contracts here: the question is whether typed
# structure carries binding information, isolated from the contract axis.
#   S0       set transformer on relational S0 features (entity-blind)
#   S0e      + absolute entity/role numeric features (binding info, no tokens)
#   S1       typed tokens (fact/candidate/obligation) + typed-pair attention
#   S2       S1 + obligation-conditional readout
#   S1shuf   S1 with fact-token identities deranged (content control)
#   S0_focus S0 + obligation focus (FOCUS re-measurement on relational)
#   S1_focus S1 + obligation focus
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_r probes_r/ceiling
SEEDS="${SEEDS:-5}"; EPOCHS="${EPOCHS:-40}"; SEED_BASE="${SEED_BASE:-71}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
BASE="-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1"
declare -A FLAGS=(
  [S0]="$BASE"
  [S0e]="$BASE -DENTFEAT=1"
  [S1]="$BASE -DTYPED=1"
  [S2]="$BASE -DTYPED=1 -DOBLREAD=1"
  [S1shuf]="$BASE -DTYPED=1 -DTYPEDSHUF=1"
  [S0_focus]="$BASE -DFOCUS=1"
  [S1_focus]="$BASE -DTYPED=1 -DFOCUS=1"
  [S1_assert]="$BASE -DTYPED=1 -DASSERT=1 -DASSERTW=0.5"
  [S1_assert_rand]="$BASE -DTYPED=1 -DASSERT=1 -DASSERTW=0"
  [S1_assert_union]="$BASE -DTYPED=1 -DASSERT=1 -DASSERTW=0.5 -DASSERTUNION=1"
)
declare -A EXTRA=(
  [S0]="--branch 5"
  [S0e]="--branch 5"
  [S1]="--branch 5"
  [S2]="--branch 5"
  [S1shuf]="--branch 5"
  [S0_focus]="--branch 5 --goal-directed 1"
  [S1_focus]="--branch 5 --goal-directed 1"
  [S1_assert]="--branch 5"
  [S1_assert_rand]="--branch 5"
  [S1_assert_union]="--branch 5"
)
ORDER="S0 S0e S1 S2 S1shuf S0_focus S1_focus S1_assert S1_assert_rand S1_assert_union"
arm_run () {
  local a="$1"; mkdir -p "probes_r/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/r_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_r/$a/w_$s.bin" --no-bound > "probes_r/$a/train_$s.log" 2>&1
  done
  : > "probes_r/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/r_$a" --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --beam 3 --dfs --subsume 1 --prop 1 --no-bound ${EXTRA[$a]} \
      --load-weights "probes_r/$a/w_$s.bin" >> "probes_r/$a/cfg_4_4.txt"
  done
}
for a in $ORDER; do clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DRELATOM=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/r_$a" -lm; done
for a in $ORDER; do arm_run "$a" & done
wait
PROBES=probes_r ARMS="$ORDER" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/rel0270.txt

# no-contract exhaustive ceiling: branch 24 = POOL covers the whole action
# space (no contract actions here), so the ceiling is weight-independent.
for i in $(seq 0 $((SEEDS-1))); do
  s=$((SEED_BASE+i))
  "bin/r_S0" --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --eval-budget 4 \
    --dfs --branch 24 --subsume 1 --prop 1 --no-bound \
    --load-weights "probes_r/S0/w_$s.bin" > "probes_r/ceiling/seed_$s.txt" 2>&1 &
done
wait
grep -h '^DFS' probes_r/ceiling/seed_*.txt | sed 's/^/CEILING /' | tee out/ceiling0270.txt