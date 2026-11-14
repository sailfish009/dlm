#!/usr/bin/env bash
# 0.0246: build, reference parity, LLVM identity, audits, dataset exposure and
# the state-collection x representation 2x2. Every arm trains on the same number
# of samples per epoch (matched optimizer updates).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out bin
SEEDS="${SEEDS:-5}"
EPOCHS="${EPOCHS:-40}"

clang -O2 -Iinclude -Isrc src/pst.c -o bin/pst -lm
clang -O2 -DHARD_GOALS=1 -Iinclude -Isrc src/pst.c -o bin/pst_hard_agg -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc src/pst.c -o bin/pst_hard_relob -lm
clang -O2 tools/world_audit.c -o bin/world_audit -lm
clang -O2 tools/gate_check.c -o bin/gate_check -lm
clang -O2 tools/alias_audit.c -o bin/alias_audit -lm

./bin/pst --dump out/worlds.txt --worlds 8 | tee out/gen.txt
/usr/bin/python3 tools/check_parity.py out/worlds.txt | tee out/parity.txt

for O in 0 2 3; do
  clang -O$O -Iinclude -Isrc src/pst.c -o bin/pst_O$O -lm
  ./bin/pst_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 > out/id_O$O.txt
done
diff -q out/id_O0.txt out/id_O2.txt
diff -q out/id_O0.txt out/id_O3.txt
echo "LLVM-MATRIX PASS O0/O2/O3"

./bin/pst --train --seeds "$SEEDS" --epochs "$EPOCHS" --train-n 180 --val-n 60 --test-n 100 \
  --collect root --sample root > out/ref_base.txt
./bin/pst --dump-test out/ref_worlds.txt --test-n 100 --seed 11 > out/dump_ref.txt
./bin/world_audit out/ref_worlds.txt | tee out/audit_ref.txt

./bin/pst_hard_agg --dataset-stats --collect root --train-n 180 --val-n 60 --test-n 100 | tee out/dataset_root.txt
./bin/pst_hard_agg --dataset-stats --collect full --train-n 180 --val-n 60 --test-n 100 | tee out/dataset_full.txt
./bin/pst_hard_agg --dump-test out/hard_worlds.txt --test-n 100 --seed 11 > out/dump_hard.txt
./bin/world_audit out/hard_worlds.txt | tee out/audit_hard.txt
./bin/alias_audit out/hard_worlds.txt 100 | tee out/alias.txt

./run_2x2.sh | tee out/twoby2_summary.txt
grep '^MEAN' out/2x2_A_root_agg.txt
grep '^MEAN' out/2x2_D_full_relob.txt
echo "RUN-DONE"
