#!/usr/bin/env bash
# Layer-substitution experiment: replace parts of the transformer block with
# Screamer-style branching attention (top-k) and Silicon-style symbolic path
# gating, keeping the same parameter count and training protocol.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes
SEEDS="${SEEDS:-3}"; EPOCHS="${EPOCHS:-40}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
build () { local name="$1"; shift; clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc "$@" -DVNAME="\"$name\"" src/pst.c -o "bin/pst_$name" -lm; }
build soft
build topk2 -DATTMODE=2
build topk3 -DATTMODE=3
build symgate -DSYMGATE=1
build topk2sym -DATTMODE=2 -DSYMGATE=1
out=out/layer.txt; : > $out
for name in soft topk2 topk3 symgate topk2sym; do
  mkdir -p probes/$name
  for i in $(seq 0 $((SEEDS-1))); do s=$((11+i)); \
    bin/pst_$name --train --seeds 1 --seed-base $s --epochs $EPOCHS $CFG --goaldepth 2 \
      --save-weights probes/$name/w_$s.bin --no-bound > probes/$name/train_$s.log 2>&1; done
  : > probes/$name/eval.txt
  for i in $(seq 0 $((SEEDS-1))); do s=$((11+i)); \
    bin/pst_$name --train --seeds 1 --seed-base $s $CFG --goaldepth 4 --eval-budget 4 --beam 3 \
      --load-weights probes/$name/w_$s.bin --no-bound >> probes/$name/eval.txt; \
    bin/pst_$name --train --seeds 1 --seed-base $s $CFG --goaldepth 4 --eval-budget 4 --dfs \
      --branch 3 --subsume 1 --load-weights probes/$name/w_$s.bin --no-bound >> probes/$name/eval.txt; done
  # Aggregate over SEED rows only. 0.0259 printed the LAST MEAN row (the seed-13
  # evaluation) as if it were the 3-seed average; each seed writes two MEAN rows
  # (greedy/beam run and DFS run), so MEAN-based aggregation is ambiguous.
  awk -v L="$name" '
    function num(line,key,  i,f2,kv){ split(line,f2," "); for(i=1;i<=NF;i++){ split(f2[i],kv,"="); if(kv[1]==key) return kv[2]+"" } return "" }
    /^SEED /{ s=$2+0; if (s in seen){ printf "LAYER-FAIL %s duplicate SEED %d\n", L, s; bad=1 }
      seen[s]=1; g[s]=num($0,"proof_model")+0; b[s]=num($0,"proof_beam")+0; ns++ }
    /^DFS seed=/{ s=num($0,"seed")+0; dg[s]=num($0,"goal")+0; dc[s]=num($0,"cands")+0; nd++ }
    END{
      d=0; for (k in seen) d++
      for (k in seen){ sg+=g[k]; sb+=b[k]; sd+=dg[k]; sc+=dc[k] }
      printf "LAYER %-9s d4_greedy=%.4f d4_beam3=%.4f dfs_goal=%.4f dfs_cands=%.0f seeds=%d rows=%d\n",
           L, sg/d, sb/d, sd/d, sc/d, d, nd
      if (bad) exit 1 }' probes/$name/eval.txt | tee -a $out || exit 1
done
