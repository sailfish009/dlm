#!/usr/bin/env bash
# 0.0252 integration + lifted-token arms.
# Ladder arms (train d2/b4, --balance-reward, evaluate same weights on the
# depth/budget ladder + exact first-step regret):
#   bal       relation baseline (0251 arm)
#   integral  + path-integral support (avg/growth) + per-rule prior
#   lifted    + predicate-id residual rho=0.25
#   both      integral + lifted
#   priorshuf integral with deranged prior (identity control)
#   lifted0   lifted rho=0 (type-only control)
# Held-out rung: train d2 with predicates {4,5} excluded from goals, evaluate on
# worlds whose goals are ALL in {4,5} (predicate-identity transfer).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes
SEEDS="${SEEDS:-5}"
EPOCHS="${EPOCHS:-40}"

declare -A BIN=(
  [bal]=bin/pst_hard_relob
  [integral]=bin/pst_integral
  [lifted]=bin/pst_lifted
  [both]=bin/pst_both
  [priorshuf]=bin/pst_priorshuf
  [lifted0]=bin/pst_lifted0
)
ORDER="bal integral lifted both priorshuf lifted0"

for arm in $ORDER; do
  rm -rf "probes/$arm"; mkdir -p "probes/$arm"
  SEEDS="$SEEDS" EPOCHS="$EPOCHS" PREFIX="probes/$arm" BIN="${BIN[$arm]}" \
    TRAIN_EXTRA="--balance-reward" ./run_probes.sh > "out/probes_$arm.txt" 2>&1
  echo "ARM-$arm done"
done

# ---- held-out predicate transfer rung (train d2 ho{4,5} -> test d2 ho{4,5}) ----
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --holdout 45"
for arm in bal integral lifted both lifted0; do
  P="probes/ho_$arm"; rm -rf "$P"; mkdir -p "$P"
  for i in $(seq 0 $((SEEDS-1))); do
    seed=$((11+i))
    "${BIN[$arm]}" --train --seeds 1 --seed-base "$seed" --epochs "$EPOCHS" $CFG \
      --goaldepth 2 --goal-scan --balance-reward --save-weights "$P/w_$seed.bin" --no-bound \
      > "$P/train_$seed.log" 2>&1
  done
  for cfg in "2 4" "2 6"; do
    set -- $cfg; d=$1; b=$2
    : > "$P/cfg_${d}_${b}.txt"
    for i in $(seq 0 $((SEEDS-1))); do
      seed=$((11+i))
      "${BIN[$arm]}" --train --seeds 1 --seed-base "$seed" $CFG --goaldepth "$d" --goal-scan \
        --eval-budget "$b" --regret --load-weights "$P/w_$seed.bin" --no-bound >> "$P/cfg_${d}_${b}.txt"
    done
  done
  echo "ARM-ho_$arm done"
done

# ---- summary ----
{
  for arm in $ORDER; do echo "== $arm"; grep -E '^ladder|^regret' "out/probes_$arm.txt"; done
  echo "== held-out (train d2 ho{4,5}, test goals all in {4,5})"
  for arm in bal integral lifted both lifted0; do
    P="probes/ho_$arm"
    for cfg in 2_4 2_6; do
      awk -v tag="ho_$arm $cfg" '
        /^MEAN /{n++; for(i=1;i<=NF;i++){split($i,kv,"="); m[kv[1]]+=kv[2]}}
        END{ if(n) printf "holadder %s goal=%.4f full=%.4f beam=%.4f support_beam=%.4f\n",
             tag, m["proof_model"]/n, m["full_model"]/n, m["proof_beam"]/n, m["beam_support"]/n }
      ' "$P/cfg_$cfg.txt"
    done
  done
} | tee out/integral_summary.txt
echo "INTEGRAL-RUN-DONE"