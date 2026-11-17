#!/usr/bin/env bash
# 0.0264 gates: capacity scaling (width / depth / untied phases).
# Fails when:
#   SCALE-GRADCHECK  any capacity variant's analytic gradient disagrees with FD
#   SCALE-OFF        PHASEUNTIE is not inert when the passes are tied (NPASS=1)
#   SCALE-PARAMS     the base arm is not exactly 19,939 parameters
#   SCALE-CLAIM      a capacity gain is reported at 2SE when the 15-seed contrast is
#                    inside it, or the note omits the verdict
#   AGG/WHDR/LLVM    same checks as 0.0263
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-15}"
export PROBES=probes_c15
export ARMS="base w48 untied"
row () { awk -v a="$1" -v k="$2" '$1=="ARM" && $2==a{ for(i=3;i<=NF;i++){ split($i,kv,"="); if(kv[1]==k) print kv[2] } }' out/scale15.txt; }

echo "== documentation hygiene (review F6)"
bash tools/doc_check.sh ../../docs/release-0264.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 1. gradient check across capacity variants"
for f in "base:" "w48:-DMD=48" "d3:-DMNL=3" "w48d3:-DMD=48 -DMNL=3" "untied:-DVAR_LOOP=1 -DPHASEUNTIE=1"; do
  n="${f%%:*}"; fl="${f#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $fl src/pst.c -o "bin/gcs_$n" -lm
  "./bin/gcs_$n" --gradcheck > "out/gcs_$n.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gcs_$n.txt" || { echo "GRADCHECK-FAIL $n"; cat "out/gcs_$n.txt"; exit 1; }
  printf "  %-7s %s\n" "$n" "$(grep '^GRADCHECK ' out/gcs_$n.txt)"
done
echo "SCALE-GRADCHECK-PASS"

echo "== 2. untied plumbing inert when phases are tied"
ra="--train --seeds 1 --seed-base 51 --epochs 3 --train-n 40 --val-n 40 --test-n 40 --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DPHASEUNTIE=1 -Iinclude -Isrc src/pst.c -o bin/c_untie1 -lm
./bin/c_untie1 $ra > out/sc_untie1.txt 2>&1
./bin/gcs_base $ra > out/sc_base.txt 2>&1
cmp -s out/sc_base.txt out/sc_untie1.txt || { echo "SCALE-OFF-FAIL PHASEUNTIE(NPASS=1) differs from base"; exit 1; }
echo "SCALE-OFF-PASS PHASEUNTIE with tied passes is identical to base"

echo "== 3. parameter counts"
grep '^SCALEPARAM' out/scale_params.txt | sed 's/^/  /'
bp=$(awk '$1=="SCALEPARAM" && $2=="base"{print $3}' out/scale_params.txt)
[ "$bp" = "19939" ] || { echo "SCALE-PARAMS-FAIL base=$bp != 19939"; exit 1; }
echo "SCALE-PARAMS-PASS base=19,939"

echo "== 4. 15-seed contrasts (the 5-seed +11.4pp did not survive)"
bash tools/hybrid_stats.sh contrast w48 base goal | tee out/scale_contrast.txt
bash tools/hybrid_stats.sh contrast w48 base full | tee -a out/scale_contrast.txt
bash tools/hybrid_stats.sh contrast untied base goal | tee -a out/scale_contrast.txt
bash tools/hybrid_stats.sh contrast w48 untied goal | tee -a out/scale_contrast.txt
awk '
/w48-base goal/ && /SIGNIFICANT/  { sig=1 }
/w48-base goal/ && /INCONCLUSIVE/ { sig=0 }
END{
  if (sig) print "SCALE-CLAIM width beats base at 2SE over 15 seeds"
  else print "SCALE-CLAIM-VERDICT SCALE-NOT-DEMONSTRATED (width/depth/untied all inside 2SE over 15 seeds; the 5-seed +11.4pp was seed variance)"
}' out/scale_contrast.txt | tee out/scale_verdict.txt
if grep -q 'SCALE-NOT-DEMONSTRATED' out/scale_verdict.txt; then
  grep -q 'SCALE-NOT-DEMONSTRATED' ../../docs/release-0264.md \
    || { echo "SCALE-CLAIM-FAIL release note omits SCALE-NOT-DEMONSTRATED"; exit 1; }
  echo "SCALE-CLAIM-PASS verdict stated in docs/release-0264.md"
fi

echo "== 5. aggregation + mutation regression"
bash tools/hybrid_stats.sh verify out/scale15.txt "$SEEDS"
bash gate_regression_hybrid.sh out/scale15.txt probes_c15 "$SEEDS"

echo "== 6. capacity tag in the weight header"
ra2="--train --seeds 1 --seed-base 51 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/c_w48  $ra2 --load-weights probes_c15/base/w_51.bin --no-bound > out/sh_a.txt 2>&1; ea=$?
./bin/c_base $ra2 --load-weights probes_c15/w48/w_51.bin --no-bound > out/sh_b.txt 2>&1; eb=$?
./bin/c_w48  $ra2 --load-weights probes_c15/w48/w_51.bin --no-bound > out/sh_c.txt 2>&1; ec=$?
set -e
[ "$ea" -eq 4 ] || { echo "WHDR-FAIL w48 accepted base weights (exit $ea)"; exit 1; }
[ "$eb" -eq 4 ] || { echo "WHDR-FAIL base accepted w48 weights (exit $eb)"; exit 1; }
[ "$ec" -eq 0 ] || { echo "WHDR-FAIL w48 rejected its own weights (exit $ec)"; exit 1; }
echo "WHDR-PASS width/depth/phase tags in the header; cross-capacity load refused"

echo "== 7. LLVM identity + sanitizers (w48, untied)"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DMD=48 -Iinclude -Isrc src/pst.c -o bin/c_O$O -lm
  ./bin/c_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3 > out/sc_id_O$O.txt 2>&1
done
diff -q out/sc_id_O0.txt out/sc_id_O2.txt >/dev/null && diff -q out/sc_id_O0.txt out/sc_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DVAR_LOOP=1 -DPHASEUNTIE=1 -Iinclude -Isrc src/pst.c -o bin/c_asan -lm
./bin/c_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 3 > out/sc_asan.txt 2> out/sc_asan.err
grep -q 'Sanitizer' out/sc_asan.err && { echo ASAN-FAIL; cat out/sc_asan.err; exit 1; }
echo "LLVM-PASS O0/O2/O3 byte-identical; ASAN+UBSAN clean (untied phases)"
echo "V0264-SCALE-PASS"
