#!/usr/bin/env bash
# 0.0268: recombination matrix with the controls the 0267 audit asked for.
#   A_nocost    label only, branch 3
#   A_b5        label only, branch 5            (branch-width control)
#   A_b6        label only, budget 6, branch 3   (budget control at b6)
#   B_pair16    + contracts, branch 3
#   C_pair64    + contracts, keep 64
#   D_pair16_b5 + contracts, branch 5
#   E_pair16_e6 + contracts, budget 6
#   F/G/H       + integral / lifted / focus
# Plus per-seed contract-action ceilings (exhaustive DFS) and the budget-6 bound.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_x probes_x/ceiling
SEEDS="${SEEDS:-5}"; EPOCHS="${EPOCHS:-40}"; SEED_BASE="${SEED_BASE:-71}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
LABEL="-DVALMODE=1 -DLABEL_NCOST=1"
PAIR="$LABEL -DLEMMA=1 -DPAIRMODE=1"
declare -A FLAGS=(
  [A_nocost]="$LABEL"
  [A_b5]="$LABEL"
  [A_b6]="$LABEL"
  [B_pair16]="$PAIR"
  [C_pair64]="$PAIR"
  [D_pair16_b5]="$PAIR"
  [E_pair16_e6]="$PAIR"
  [F_pair16_intg]="$PAIR -DINTEGRAL=1"
  [G_pair16_lift]="$PAIR -DLIFTED=1 -DLIFT_RHO=0.25"
  [H_pair16_focus]="$PAIR -DFOCUS=1"
)
declare -A TRAIN_EXTRA=(
  [A_nocost]="" [A_b5]="" [A_b6]="" [B_pair16]="" [C_pair64]="--pair-keep 64"
  [D_pair16_b5]="" [E_pair16_e6]="" [F_pair16_intg]="" [G_pair16_lift]="" [H_pair16_focus]=""
)
declare -A EXTRA=(
  [A_nocost]="--branch 3"
  [A_b5]="--branch 5"
  [A_b6]="--branch 3 --eval-budget 6"
  [B_pair16]="--branch 3"
  [C_pair64]="--branch 3 --pair-keep 64"
  [D_pair16_b5]="--branch 5"
  [E_pair16_e6]="--branch 3 --eval-budget 6"
  [F_pair16_intg]="--branch 3"
  [G_pair16_lift]="--branch 3"
  [H_pair16_focus]="--branch 3"
)
ORDER="A_nocost A_b5 A_b6 B_pair16 C_pair64 D_pair16_b5 E_pair16_e6 F_pair16_intg G_pair16_lift H_pair16_focus"
arm_run () {
  local a="$1"; mkdir -p "probes_x/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/y_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      ${TRAIN_EXTRA[$a]} --save-weights "probes_x/$a/w_$s.bin" --no-bound > "probes_x/$a/train_$s.log" 2>&1
  done
  : > "probes_x/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/y_$a" --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --beam 3 --dfs --subsume 1 --prop 1 --no-bound ${EXTRA[$a]} \
      --load-weights "probes_x/$a/w_$s.bin" >> "probes_x/$a/cfg_4_4.txt"
  done
}
for a in $ORDER; do clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/y_$a" -lm; done
for a in $ORDER; do arm_run "$a" & done
wait
PROBES=probes_x ARMS="$ORDER" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/recomb0268.txt

# per-seed contract-action ceiling: exhaustive DFS (branch 64 >= POOL+keep, 0268 review G2)
for i in $(seq 0 $((SEEDS-1))); do
  s=$((SEED_BASE+i))
  "bin/y_B_pair16" --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --eval-budget 4 \
    --dfs --branch 64 --subsume 1 --prop 1 --no-bound \
    --load-weights "probes_x/B_pair16/w_$s.bin" > "probes_x/ceiling/seed_$s.txt" 2>&1 &
done
wait
# budget-6 bound (fixture level, seed independent)
"bin/y_A_nocost" --train --seeds 1 --seed-base 71 $CFG --goaldepth 4 --eval-budget 6 \
  --dfs --branch 3 --subsume 1 --prop 1 --load-weights probes_x/A_nocost/w_71.bin \
  > probes_x/ceiling/bound6.txt 2>&1
grep -h '^DFS' probes_x/ceiling/seed_*.txt | sed 's/^/CEILING /' | tee out/ceiling0268.txt
grep -o 'bound_goal=[0-9.]* bound_full=[0-9.]*' probes_x/ceiling/bound6.txt | head -1 | sed 's/^/BOUND6 /' | tee -a out/ceiling0268.txt
