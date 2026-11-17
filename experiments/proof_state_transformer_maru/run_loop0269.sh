#!/usr/bin/env bash
# 0.0269: the loop cell — proof-state transition INSIDE the model.
# All arms share the episode-batched trainer (EPTRAIN=1) so contrasts are
# protocol-matched. Base label = exact DP value, no cost (the working label).
#   A_nocost     label only, branch 3
#   B_pair16     + contracts, branch 3
#   D_pair16_b5  + contracts, branch 5          (0268 best config, new protocol)
#   D_rem        + remaining-budget state feature (identifiability control)
#   D_cell       + loop cell (BPTT latent register)
#   D_cellpred   + loop cell + world-model auxiliary loss (PREDW 0.5)
#   D_detach     + static z0 token (no transition; cell params unused)
#   D_shuf       + cell fed a rotated action sequence (content control)
#   D_remcell    + rem feature + loop cell
#   D_wide       + one extra block (capacity-matched feedforward control)
# Plus per-seed contract-action ceilings at branch 64 (>= POOL + pair_keep).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_y probes_y/ceiling
SEEDS="${SEEDS:-5}"; EPOCHS="${EPOCHS:-40}"; SEED_BASE="${SEED_BASE:-71}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
LABEL="-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1"
PAIR="$LABEL -DLEMMA=1 -DPAIRMODE=1"
CELL="$PAIR -DLOOPCELL=1"
declare -A FLAGS=(
  [A_nocost]="$LABEL"
  [B_pair16]="$PAIR"
  [D_pair16_b5]="$PAIR"
  [D_rem]="$PAIR -DREMFEAT=1"
  [D_cell]="$CELL"
  [D_cellpred]="$CELL -DPREDW=0.5"
  [D_detach]="$CELL -DCELLDETACH=1"
  [D_shuf]="$CELL -DCELLSHUF=1"
  [D_remcell]="$CELL -DREMFEAT=1"
  [D_wide]="$PAIR -DMNL=3"
)
declare -A EXTRA=(
  [A_nocost]="--branch 3"
  [B_pair16]="--branch 3"
  [D_pair16_b5]="--branch 5"
  [D_rem]="--branch 5"
  [D_cell]="--branch 5"
  [D_cellpred]="--branch 5"
  [D_detach]="--branch 5"
  [D_shuf]="--branch 5"
  [D_remcell]="--branch 5"
  [D_wide]="--branch 5"
)
ORDER="A_nocost B_pair16 D_pair16_b5 D_rem D_cell D_cellpred D_detach D_shuf D_remcell D_wide"
arm_run () {
  local a="$1"; mkdir -p "probes_y/$a"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/y9_$a" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_y/$a/w_$s.bin" --no-bound > "probes_y/$a/train_$s.log" 2>&1
  done
  : > "probes_y/$a/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/y9_$a" --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --beam 3 --dfs --subsume 1 --prop 1 --no-bound ${EXTRA[$a]} \
      --load-weights "probes_y/$a/w_$s.bin" >> "probes_y/$a/cfg_4_4.txt"
  done
}
for a in $ORDER; do clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/y9_$a" -lm; done
for a in $ORDER; do arm_run "$a" & done
wait
PROBES=probes_y ARMS="$ORDER" bash tools/hybrid_stats.sh table "$SEEDS" | tee out/loop0269.txt

# per-seed contract-action ceiling: exhaustive DFS, branch 64 >= POOL(24)+keep(16)
# (0268 review G2: branch=POOL truncates the score-sorted candidate+pair list).
# Contracts are mined from each arm's OWN weights, so every arm gets its own
# ceiling; the B ceiling is kept for cross-version comparability.
for a in $ORDER; do
  case "$a" in A_nocost|B_pair16) continue ;; esac
  for i in $(seq 0 $((SEEDS-1))); do
    s=$((SEED_BASE+i))
    "bin/y9_$a" --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --eval-budget 4 \
      --dfs --branch 64 --subsume 1 --prop 1 --no-bound \
      --load-weights "probes_y/$a/w_$s.bin" > "probes_y/ceiling/${a}_seed_$s.txt" 2>&1 &
  done
done
for i in $(seq 0 $((SEEDS-1))); do
  s=$((SEED_BASE+i))
  "bin/y9_B_pair16" --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --eval-budget 4 \
    --dfs --branch 64 --subsume 1 --prop 1 --no-bound \
    --load-weights "probes_y/B_pair16/w_$s.bin" > "probes_y/ceiling/seed_$s.txt" 2>&1 &
done
wait
grep -h '^DFS' probes_y/ceiling/seed_*.txt | sed 's/^/CEILING /' | tee out/ceiling0269.txt