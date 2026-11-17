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
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DBINDTOK=2 -Iinclude -Isrc src/pst.c -o bin/pst_hard_bindshuf -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc src/pst.c -o bin/pst_hard_relob -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DBINDTOK=2 -Iinclude -Isrc src/pst.c -o bin/pst_hard_bindshuf -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DBINDTOK=1 -Iinclude -Isrc src/pst.c -o bin/pst_hard_bindtok -lm
clang -O2 tools/world_audit.c -o bin/world_audit -lm
clang -O2 tools/gate_check.c -o bin/gate_check -lm
clang -O2 tools/alias_audit.c -o bin/alias_audit -lm
# 0.0252 integration/lifted arms used by run_integral.sh (must be built here so the
# release is self-contained from a clean bin/).
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DINTEGRAL=1 -Iinclude -Isrc src/pst.c -o bin/pst_integral -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DLIFTED=1 -DLIFT_RHO=0.25 -Iinclude -Isrc src/pst.c -o bin/pst_lifted -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DINTEGRAL=1 -DLIFTED=1 -DLIFT_RHO=0.25 -Iinclude -Isrc src/pst.c -o bin/pst_both -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DINTEGRAL=1 -DPRIOR_SHUF=1 -Iinclude -Isrc src/pst.c -o bin/pst_priorshuf -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DLIFTED=1 -DLIFT_RHO=0.0 -Iinclude -Isrc src/pst.c -o bin/pst_lifted0 -lm

./bin/pst --dump out/worlds.txt --worlds 8 | tee out/gen.txt
/usr/bin/python3 tools/check_parity.py out/worlds.txt | tee out/parity.txt

for O in 0 2 3; do
  clang -O$O -Iinclude -Isrc src/pst.c -o bin/pst_O$O -lm
  ./bin/pst_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 6 --goaldepth 3 --goal-scan > out/id_O$O.txt
done
diff -q out/id_O0.txt out/id_O2.txt
diff -q out/id_O0.txt out/id_O3.txt
echo "LLVM-MATRIX PASS O0/O2/O3"

./bin/pst --train --seeds "$SEEDS" --epochs "$EPOCHS" --train-n 180 --val-n 60 --test-n 100 \
  --collect root --sample root > out/ref_base.txt
./bin/pst --dump-test out/ref_worlds.txt --test-n 100 --seed 11 > out/dump_ref.txt
./bin/world_audit out/ref_worlds.txt | tee out/audit_ref.txt

./bin/pst_hard_relob --dataset-stats --goal-scan --collect root --train-n 180 --val-n 60 --test-n 100 | tee out/dataset_root.txt
./bin/pst_hard_relob --dataset-stats --goal-scan --collect full --train-n 180 --val-n 60 --test-n 100 | tee out/dataset_full.txt
./bin/pst_hard_relob --dump-test out/hard_worlds.txt --test-n 100 --seed 11 --goal-scan > out/dump_hard.txt
./bin/world_audit out/hard_worlds.txt | tee out/audit_hard.txt
./bin/alias_audit out/hard_worlds.txt 100 | tee out/alias.txt

./run_2x2.sh | tee out/twoby2_summary.txt

# structure-probe ladder: exposure control (unbal/bal) and the matched-width
# binding-token control (aligned vs entity-shifted, same width/params)
rm -rf probes/unbal probes/bal probes/bindtok probes/bindshuf
mkdir -p probes/unbal probes/bal probes/bindtok probes/bindshuf
SEEDS="$SEEDS" PREFIX=probes/unbal ./run_probes.sh > out/probes_unbal.txt
SEEDS="$SEEDS" PREFIX=probes/bal   TRAIN_EXTRA="--balance-reward" ./run_probes.sh > out/probes_bal.txt
SEEDS="$SEEDS" PREFIX=probes/bindtok  BIN=./bin/pst_hard_bindtok  TRAIN_EXTRA="--balance-reward" ./run_probes.sh > out/probes_bindtok.txt
SEEDS="$SEEDS" PREFIX=probes/bindshuf BIN=./bin/pst_hard_bindshuf TRAIN_EXTRA="--balance-reward" ./run_probes.sh > out/probes_bindshuf.txt
for f in unbal bal bindtok bindshuf; do echo "PROBE-$f"; grep -E '^ladder|^regret' out/probes_$f.txt; done
grep '^MEAN' out/2x2_A_root_agg.txt
grep '^MEAN' out/2x2_D_full_relob.txt

# 0.0252 integration + lifted-token arms and the predicate-held-out rung
SEEDS="$SEEDS" EPOCHS="$EPOCHS" ./run_integral.sh > out/integral_run.log 2>&1
tail -1 out/integral_run.log
echo "RUN-DONE"
