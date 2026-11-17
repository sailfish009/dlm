#!/usr/bin/env bash
# Port of Screamer (choice+backtracking+propagation) and Silicon (subsumption)
# into the native search. Measures goal coverage vs candidate evaluations on the
# genuine depth-4 fixture, comparing DFS(branch) with the C beam.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes
SEEDS="${SEEDS:-3}"; EPOCHS="${EPOCHS:-40}"
BIN=bin/pst_hard_relob; CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc src/pst.c -o $BIN -lm
for i in $(seq 0 $((SEEDS-1))); do s=$((11+i)); [ -f probes/w_${s}_v$(cat ../../VERSION).bin ] || \
  $BIN --train --seeds 1 --seed-base $s --epochs $EPOCHS $CFG --goaldepth 2 --save-weights probes/w_${s}_v$(cat ../../VERSION).bin --no-bound >probes/train_$s.log 2>&1; done
out=out/port.txt; : > $out
run () { # label, extra args
  local label="$1"; shift
  : > probes/cfg_$label.txt
  for i in $(seq 0 $((SEEDS-1))); do s=$((11+i)); \
    $BIN --train --seeds 1 --seed-base $s $CFG --goaldepth 4 --eval-budget 4 --dfs "$@" \
      --load-weights probes/w_${s}_v$(cat ../../VERSION).bin --no-bound >> probes/cfg_$label.txt; done
  awk -v L="$label" '/^DFS /{n++; for(i=1;i<=NF;i++){split($i,kv,"="); v[kv[1]]=kv[2]}
      g+=v["goal"]; f+=v["full"]; c+=v["cands"]; no+=v["nodes"]; l+=v["leafs"]; p+=v["pruned"]}
    END{printf "PORT %-18s goal=%.4f full=%.4f nodes=%.0f cands=%.0f leafs=%.0f pruned=%.0f n=%d\n",
        L, g/n, f/n, no/n, c/n, l/n, p/n, n}' probes/cfg_$label.txt | tee -a $out
}
for b in 1 2 3 5; do
  run "dfs_b${b}_sub0" --branch $b --subsume 0
  run "dfs_b${b}_sub1" --branch $b --subsume 1
done
run "dfs_b3_noprop" --branch 3 --subsume 1 --prop 0
for W in 1 3 10 25; do
  : > probes/cfg_beam$W.txt
  for i in $(seq 0 $((SEEDS-1))); do s=$((11+i)); \
    $BIN --train --seeds 1 --seed-base $s $CFG --goaldepth 4 --eval-budget 4 --beam $W \
      --load-weights probes/w_${s}_v$(cat ../../VERSION).bin --no-bound >> probes/cfg_beam$W.txt; done
  awk -v L="beam_W$W" '/^MEAN /{n++; for(i=1;i<=NF;i++){split($i,kv,"="); v[kv[1]]=kv[2]}}
    END{printf "PORT %-18s goal=%.4f full=%.4f nodes=- cands=%.0f leafs=- pruned=- greedy=%.4f\n",
        L, v["proof_beam"], v["full_beam"], v["search_cands"], v["proof_model"]}' probes/cfg_beam$W.txt | tee -a $out
done
# R255-3 soundness oracle: exhaustive DFS (branch=POOL) with postorder subsumption
# and propagation must reach the budget-exact bound on every seed. Bound enabled.
CFGNB="${CFG/--no-bound/}"
: > probes/cfg_exh.txt
for i in $(seq 0 $((SEEDS-1))); do s=$((11+i)); \
  $BIN --train --seeds 1 --seed-base $s $CFGNB --goaldepth 4 --eval-budget 4 --dfs --branch 24 --subsume 1 --prop 1 \
    --load-weights probes/w_${s}_v$(cat ../../VERSION).bin >> probes/cfg_exh.txt; done
awk '/^DFS /{for(i=1;i<=NF;i++){split($i,kv,"="); v[kv[1]]=kv[2]} dg=v["goal"]; df=v["full"]; sd=v["seed"]}
     /^MEAN /{for(i=1;i<=NF;i++){split($i,kv,"="); v[kv[1]]=kv[2]}
       ok=(dg==v["bound_goal"] && df==v["bound_full"]) ? 1 : 0;
       printf "EXH-ORACLE seed=%s dfs_goal=%.4f bound_goal=%.4f dfs_full=%.4f bound_full=%.4f ok=%d\n",
         sd, dg, v["bound_goal"], df, v["bound_full"], ok}' probes/cfg_exh.txt | tee -a $out
