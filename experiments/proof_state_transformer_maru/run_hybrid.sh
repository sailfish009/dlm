#!/usr/bin/env bash
# 0.0260 hybrid reasoning layer: Rocq + Silicon + Screamer elements inside the
# native (C/LLVM IR + Maru) proof-state transformer.
#
# Elements (all compile-time, all ablatable, same parameter count 19939):
#   rocq/cert   independent proof-certificate checker (parent-map re-derivation)
#   rocq/focus  obligation-directed candidate focus (only unproved goal heads)
#   silicon/pc  kernel path condition: inadmissible candidates leave the action set
#   silicon/lemma verified 2-rule contracts applied as one action slot
#   screamer/topk sparse top-k attention layer (branch-preserving readout)
#   screamer/dfs  branch + backtrack + propagation + subsumption (baseline search)
#
# One training protocol, one evaluation protocol; every arm writes per-seed rows.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_h
SEEDS="${SEEDS:-3}"; EPOCHS="${EPOCHS:-40}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 3 --subsume 1 --prop 1 --no-bound"

# arm:flags  (flags are compile-time; the header records them)
ARMS=(
  "pure:"
  "topk:-DATTMODE=2"
  "pc:-DSYMGATE=2"
  "soft:-DSYMGATE=1"
  "focus:-DFOCUS=1"
  "cert:-DCERT=1"
  "lemma:-DLEMMA=1"
  "hybrid:-DATTMODE=2 -DSYMGATE=2 -DFOCUS=1 -DCERT=1 -DLEMMA=1"
)

for spec in "${ARMS[@]}"; do
  name="${spec%%:*}"; flags="${spec#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $flags src/pst.c -o "bin/hb_$name" -lm
  mkdir -p "probes_h/$name"
  # train once per seed at d=2/b=4 on the hard fixture
  for i in $(seq 0 $((SEEDS-1))); do
    s=$((11+i))
    "bin/hb_$name" --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" $CFG --goaldepth 2 \
      --save-weights "probes_h/$name/w_$s.bin" --no-bound > "probes_h/$name/train_$s.log" 2>&1
  done
  # one evaluation invocation per seed: greedy + beam + DFS + hybrid census in one file
  : > "probes_h/$name/cfg_4_4.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    s=$((11+i))
    "bin/hb_$name" --train --seeds 1 --seed-base "$s" $CFG $EVAL \
      --load-weights "probes_h/$name/w_$s.bin" >> "probes_h/$name/cfg_4_4.txt"
  done
done

# certificate negative control (mutated parent map must be rejected)
"bin/hb_cert" --train --seeds 1 --seed-base 11 $CFG --goaldepth 4 --eval-budget 4 --dfs --branch 3 \
  --cert-selftest --load-weights probes_h/cert/w_11.bin > out/hybrid_cert_mutation.txt 2>&1

bash tools/hybrid_stats.sh table "$SEEDS" | tee out/hybrid.txt