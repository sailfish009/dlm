#!/usr/bin/env bash
# 0.0263 gates: multi-register transformer (Screamer state branching in the model).
#
# Fails when:
#   REG-GRADCHECK  any arm's analytic gradient disagrees with finite differences
#                  (the max readout and the register bias are new backward paths)
#   REG-OFF        the register plumbing is not inert when disabled
#                  (BRANCHTOK=1 must be bit-identical to base)
#   REG-PARAMS     the base arm's parameter count drifted from 19,939
#   REG-CLAIM      the multi-register contrast is reported as a gain when it is
#                  inside 2 SE, or the release note omits the verdict
#   AGG/WHDR/LLVM  same checks as 0.0262
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"
export PROBES=probes_r
export ARMS="base b2 b2max b3max b2shuf"
row () { awk -v a="$1" -v k="$2" '$1=="ARM" && $2==a{ for(i=3;i<=NF;i++){ split($i,kv,"="); if(kv[1]==k) print kv[2] } }' out/register.txt; }

echo "== 1. gradient check, five register configurations"
for f in "base:" "b2:-DBRANCHTOK=2" "b2max:-DBRANCHTOK=2 -DREADMAX=1" \
         "b3max:-DBRANCHTOK=3 -DREADMAX=1" "b2shuf:-DBRANCHTOK=2 -DREADMAX=1 -DREGSHUF=1"; do
  n="${f%%:*}"; fl="${f#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $fl src/pst.c -o "bin/gc_$n" -lm
  "./bin/gc_$n" --gradcheck > "out/gc_$n.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gc_$n.txt" || { echo "GRADCHECK-FAIL arm=$n"; cat "out/gc_$n.txt"; exit 1; }
  printf "  %-7s %s\n" "$n" "$(grep '^GRADCHECK ' out/gc_$n.txt)"
done
echo "REG-GRADCHECK-PASS (register bias and max readout are differentiable)"

echo "== 2. the register plumbing is inert when disabled"
ra="--train --seeds 1 --seed-base 41 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DBRANCHTOK=1 -Iinclude -Isrc src/pst.c -o bin/r_off1 -lm
./bin/r_off1 $ra > out/reg_off1.txt 2>&1
./bin/gc_base $ra > out/reg_off0.txt 2>&1
cmp -s out/reg_off0.txt out/reg_off1.txt || { echo "REG-OFF-FAIL BRANCHTOK=1 differs from base"; diff <(cut -c1-100 out/reg_off0.txt) <(cut -c1-100 out/reg_off1.txt) | head -5; exit 1; }
echo "REG-OFF-PASS BRANCHTOK=1 identical to base"

echo "== 3. parameter counts (capacity is stated, not assumed equal)"
basep=$(row base candidate_labels 2>/dev/null || true)
grep -E '^PARAMS' out/register_params.txt | sed 's/^/  /'
bp=$(awk '$1=="PARAMS" && $2=="base"{print $3}' out/register_params.txt)
[ "$bp" = "19939" ] || { echo "REG-PARAMS-FAIL base parameter count $bp != 19939"; exit 1; }
echo "REG-PARAMS-PASS base=19,939 (register block excluded when the structure is off)"

echo "== 4. contrasts (2 SE, reported; claim gated on the verdict)"
bash tools/hybrid_stats.sh contrast b2max base goal | tee out/reg_contrast.txt
bash tools/hybrid_stats.sh contrast b2max base full | tee -a out/reg_contrast.txt
bash tools/hybrid_stats.sh contrast b3max base goal | tee -a out/reg_contrast.txt
bash tools/hybrid_stats.sh contrast b2 base goal     | tee -a out/reg_contrast.txt
bash tools/hybrid_stats.sh contrast b2max b2 goal    | tee -a out/reg_contrast.txt
bash tools/hybrid_stats.sh contrast b2shuf b2 goal   | tee -a out/reg_contrast.txt
bash tools/hybrid_stats.sh contrast b2max base proof_beam | tee -a out/reg_contrast.txt
awk '
/b2max-base goal/ && /SIGNIFICANT/  { sig=1 }
/b2max-base goal/ && /INCONCLUSIVE/ { sig=0 }
END{
  if (sig) print "REG-CLAIM multi-register beats base at 2SE: report as a positive architectural result"
  else print "REG-CLAIM-VERDICT MULTIREG-NOT-DEMONSTRATED (b2max-base goal inside 2SE)"
}' out/reg_contrast.txt | tee out/reg_verdict.txt
if grep -q 'MULTIREG-NOT-DEMONSTRATED' out/reg_verdict.txt; then
  grep -q 'MULTIREG-NOT-DEMONSTRATED' ../../docs/release-0263.md \
    || { echo "REG-CLAIM-FAIL release note does not state MULTIREG-NOT-DEMONSTRATED"; exit 1; }
  echo "REG-CLAIM-PASS verdict stated in docs/release-0263.md"
fi

echo "== documentation hygiene (review F6)"
bash tools/doc_check.sh ../../docs/release-0263.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 5. aggregation schema, table identity, mutation regression"
bash tools/hybrid_stats.sh verify out/register.txt "$SEEDS"
bash gate_regression_hybrid.sh out/register.txt probes_r "$SEEDS"

echo "== 6. weight header carries the register configuration"
ra2="--train --seeds 1 --seed-base 41 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/r_b2max $ra2 --load-weights probes_r/base/w_41.bin --no-bound > out/rh_a.txt 2>&1; ea=$?
./bin/r_base  $ra2 --load-weights probes_r/b2max/w_41.bin --no-bound > out/rh_b.txt 2>&1; eb=$?
./bin/r_b2max $ra2 --load-weights probes_r/b2max/w_41.bin --no-bound > out/rh_c.txt 2>&1; ec=$?
set -e
[ "$ea" -eq 4 ] || { echo "WHDR-FAIL b2max accepted base weights (exit $ea)"; exit 1; }
[ "$eb" -eq 4 ] || { echo "WHDR-FAIL base accepted b2max weights (exit $eb)"; exit 1; }
[ "$ec" -eq 0 ] || { echo "WHDR-FAIL b2max rejected its own weights (exit $ec)"; exit 1; }
echo "WHDR-PASS register configuration in the header; cross-configuration load refused"

echo "== 7. LLVM identity + sanitizers on the max-readout arm"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DBRANCHTOK=2 -DREADMAX=1 -Iinclude -Isrc src/pst.c -o bin/r_O$O -lm
  ./bin/r_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3 > out/reg_id_O$O.txt 2>&1
done
diff -q out/reg_id_O0.txt out/reg_id_O2.txt >/dev/null && diff -q out/reg_id_O0.txt out/reg_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DBRANCHTOK=3 -DREADMAX=1 -Iinclude -Isrc src/pst.c -o bin/r_asan -lm
./bin/r_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 3 > out/reg_asan.txt 2> out/reg_asan.err
grep -q 'Sanitizer' out/reg_asan.err && { echo ASAN-FAIL; cat out/reg_asan.err; exit 1; }
echo "LLVM-PASS O0/O2/O3 byte-identical; ASAN+UBSAN clean (B=3 max readout)"
echo "V0263-MULTIREG-PASS"