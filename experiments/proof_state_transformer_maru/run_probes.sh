#!/usr/bin/env bash
# Structure-probe ladder (0.0247/0.0248). Train once on d=2/b=4 (optionally with
# reward-balanced exposure), then evaluate the SAME weights on structural shifts
# with exact first-step regret:
#   ID d=2 b=4 | depth d=3 b=4, d=4 b=4 | budget d=2 b=6, d=4 b=6
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes
SEEDS="${SEEDS:-3}"
EPOCHS="${EPOCHS:-40}"
BIN="${BIN:-bin/pst_hard_relob}"
PREFIX="${PREFIX:-probes}"
TRAIN_EXTRA="${TRAIN_EXTRA:-}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100"

for i in $(seq 0 $((SEEDS-1))); do
  seed=$((11+i))
  [ -f "$PREFIX/w_$seed.bin" ] || "$BIN" --train --seeds 1 --seed-base "$seed" --epochs "$EPOCHS" \
      $CFG --goaldepth 2 --goal-scan $TRAIN_EXTRA --save-weights "$PREFIX/w_$seed.bin" --no-bound > "$PREFIX/train_$seed.log" 2>&1
done

out="out/probes_${PREFIX#probes/}.txt"
echo "# ladder: trained d=2,b=4 bin=$BIN extra='$TRAIN_EXTRA'; rows are evaluation configs" | tee "$out"
for cfg in "2 4" "3 4" "4 4" "2 6" "4 6"; do
  set -- $cfg; d=$1; b=$2
  : > "$PREFIX/cfg_${d}_${b}.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    seed=$((11+i))
    "$BIN" --train --seeds 1 --seed-base "$seed" $CFG --goaldepth "$d" --goal-scan --eval-budget "$b" --regret \
      --load-weights "$PREFIX/w_$seed.bin" --no-bound >> "$PREFIX/cfg_${d}_${b}.txt"
  done

done
./summarize_probes.sh "$PREFIX"
