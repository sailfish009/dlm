#!/usr/bin/env bash
# 0.0267: recombination on top of the working label (dp value, no cost term).
# All components already exist; only the configuration changes.
#   A nocost              label only (0.0266 baseline)
#   B pair16              + verified 2-rule contracts (keep 16)
#   C pair64              + contracts, wider coverage
#   D pair16_b5           + contracts, branch 5
#   E pair16_e6           + contracts, 6-slot eval budget
#   F pair16_intg         + path-integral features
#   G pair16_lift         + predicate-id residual (rho .25)
#   H pair16_focus        + obligation focus
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_x
SEEDS="${SEEDS:-5}"; EPOCHS="${EPOCHS:-40}"; SEED_BASE="${SEED_BASE:-71}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
BASE_EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --subsume 1 --prop 1 --no-bound"
LABEL="-DVALMODE=1 -DLABEL_NCOST=1"
declare -A FLAGS=(
  [A_nocost]="$LABEL"
  [B_pair16]="$LABEL -DLEMMA=1 -DPAIRMODE=1"
  [C_pair64]="$LABEL -DLEMMA=1 -DPAIRMODE=1"
  [D_pair16_b5]="$LABEL -DLEMMA=1 -DPAIRMODE=1"
  [E_pair16_e6]="$LABEL -DLEMMA=1 -DPAIRMODE=1"
  [F_pair16_intg]="$LABEL -DLEMMA=1 -DPAIRMODE=1 -DINTEGRAL=1"
  [G_pair16_lift]="$LABEL -DLEMMA=1 -DPAIRMODE=1 -DLIFTED=1 -DLIFT_RHO=0.25"
  [H_pair16_focus]="$LABEL -DLEMMA=1 -DPAIRMODE=1 -DFOCUS=1"
)
declare -A TRAIN_EXTRA=(
  [A_nocost]=""
  [B_pair16]=""
  [C_pair64]="--pair-keep 64"
  [D_pair16_b5]=""
  [E_pair16_e6]=""
  [F_pair16_intg]=""
  [G_pair16_lift]=""
  [H_pair16_focus]=""
)
declare -A EXTRA=(
  [A_nocost]="--branch 3"
  [B_pair16]="--branch 3"
  [C_pair64]="--branch 3 --pair-keep 64"
  [D_pair16_b5]="--branch 5"
  [E_pair16_e6]="--branch 3 --eval-budget 6"
  [F_pair16_intg]="--branch 3"
  [G_pair16_lift]="--branch 3"
  [H_pair16_focus]="--branch 3"
)
ORDER="A_nocost B_pair16 C_pair64 D_pair16_b5 E_pair16_e6 F_pair16_intg G_pair16_lift H_pair16_focus"
arm_run () {
  local a="$1"; mkdir -p "probes_x/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/x_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      ${TRAIN_EXTRA[$a]} --save-weights "probes_x/$a/w_$s.bin" --no-bound > "probes_x/$a/train_$s.log" 2>&1
  done
  : > "probes_x/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/x_$a" --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --beam 3 --dfs --subsume 1 --prop 1 --no-bound ${EXTRA[$a]} \
      --load-weights "probes_x/$a/w_$s.bin" >> "probes_x/$a/cfg_4_4.txt"
  done
}
for a in $ORDER; do clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/x_$a" -lm; done
for a in $ORDER; do arm_run "$a" & done
wait
PROBES=probes_x ARMS="$ORDER" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/recomb.txt
