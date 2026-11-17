#!/usr/bin/env bash
# Search-vs-scorer decomposition: beam width sweep with the model scorer, plus the
# step-indexed optimality profile on the model's own greedy trajectory.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes
SEEDS="${SEEDS:-3}"; EPOCHS="${EPOCHS:-40}"
BIN=bin/pst_hard_relob
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc src/pst.c -o $BIN -lm
for i in $(seq 0 $((SEEDS-1))); do
  s=$((11+i))
  [ -f probes/w_$s.bin ] || $BIN --train --seeds 1 --seed-base $s --epochs $EPOCHS $CFG \
      --goaldepth 2 --save-weights probes/w_$s.bin --no-bound > probes/train_$s.log 2>&1
done
out=out/decomp.txt; : > $out
for d in 2 4; do
  for W in 1 3 10 25; do
    : > probes/cfg_d${d}_w${W}.txt
    for i in $(seq 0 $((SEEDS-1))); do
      s=$((11+i))
      $BIN --train --seeds 1 --seed-base $s $CFG --goaldepth $d --goal-scan --eval-budget 4 \
        --beam $W --load-weights probes/w_$s.bin --no-bound >> probes/cfg_d${d}_w${W}.txt
    done
    awk -v d=$d -v W=$W '/^MEAN /{n++; for(i=1;i<=NF;i++){split($i,kv,"="); m[kv[1]]+=kv[2]}}
      END{ printf "DECOMP d=%d W=%d goal=%.4f full=%.4f beam=%.4f\n", d, W, m["proof_model"]/n, m["full_model"]/n, m["proof_beam"]/n }' \
      probes/cfg_d${d}_w${W}.txt | tee -a $out
  done
done
for d in 2 4; do
  : > probes/cfg_traj${d}.txt
  for i in $(seq 0 $((SEEDS-1))); do
    s=$((11+i))
    $BIN --train --seeds 1 --seed-base $s $CFG --goaldepth $d --goal-scan --eval-budget 4 \
      --beam 1 --regret --load-weights probes/w_$s.bin --no-bound >> probes/cfg_traj${d}.txt
  done
  awk -v d=$d '/^TRAJ /{n[$4]++; for(i=1;i<=NF;i++){split($i,kv,"="); v[kv[1]]=kv[2]} o[$4]+=v["opt"]; os[$4]+=v["optset"]; r[$4]+=v["regret"]}
    END{ for (k in n) printf "TRAJ-MEAN d=%d step=%s opt=%.4f optset=%.2f regret=%.4f\n", d, substr(k,6), o[k]/n[k], os[k]/n[k], r[k]/n[k] }' \
    probes/cfg_traj${d}.txt | sort -t= -k2,2n | tee -a $out
done
