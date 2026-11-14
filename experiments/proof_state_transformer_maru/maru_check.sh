#!/usr/bin/env bash
# Maru Q16 inference parity on the MAIN performance protocol (0.0245 review F5):
# hard fixture + relation features + full-budget teacher states, 180/60/100, seed 11, 40 epochs. The exported artifact
# records its config and weights checksum; 100 initial states are reproduced.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
mkdir -p out bin
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc src/pst.c -o bin/pst_hard_relob -lm
./bin/pst_hard_relob --export-maru out/pst_data.l --cases 100 --seeds 1 --epochs 40 \
  --train-n 180 --val-n 60 --test-n 100 --collect full --sample sub | tee out/export.txt
"$ROOT/maru-compiler" "$ROOT/src/maru/boot.l" "$ROOT/src/dlm/logic.l" \
  "$ROOT/src/dlm/infer.l" "$ROOT/src/dlm/deduce.l" "$ROOT/src/dlm/proof.l" \
  maru/exp_table.l maru/fx.l out/pst_data.l maru/pst_infer.l maru/pst_run.l \
  | tee out/maru_pst.txt
grep -q '^MARU-PST-PARITY-PASS$' out/maru_pst.txt
