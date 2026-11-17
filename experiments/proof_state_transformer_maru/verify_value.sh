#!/usr/bin/env bash
# 0.0262 gates: budget-exact DP value labels.
#
# Fails when:
#   DP-EXACT     the memoised DP disagrees with an independent brute-force
#                enumeration on sampled (state, remaining budget) pairs
#   VAL-LEARNED  shuffled DP labels (matched multiset) are not clearly worse, i.e.
#                the label correspondence is not what the model uses
#   VAL-TARGET   the DP label's own contrast over utility is reported as a gain
#                when it is inside 2 SE, or the release note does not state it
#   CONSERVATION VALMODE=0 is bit-identical to a re-run (label path inert)
#   AGG/WHDR/LLVM  same checks as 0.0261
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"
export PROBES=probes_v
export ARMS="util dp dpshuf dplem"
row () { awk -v a="$1" -v k="$2" '$1=="ARM" && $2==a{ for(i=3;i<=NF;i++){ split($i,kv,"="); if(kv[1]==k) print kv[2] } }' out/value.txt; }

echo "== 1. DP label equals an independent brute-force enumeration"
grep -q '^DP-AUDIT-SUMMARY checks=[1-9][0-9]* mismatches=0$' out/dp_audit.txt \
  || { echo "DP-EXACT-FAIL"; cat out/dp_audit.txt; exit 1; }
echo "DP-EXACT-PASS $(grep '^DP-AUDIT-SUMMARY' out/dp_audit.txt) (memoised recursion vs no-memo enumeration)"

echo "== 2. labels are actually used: shuffled control collapses"
bash tools/hybrid_stats.sh contrast dp dpshuf goal | tee out/value_contrast.txt
bash tools/hybrid_stats.sh contrast dp util goal     | tee -a out/value_contrast.txt
bash tools/hybrid_stats.sh contrast dp util full     | tee -a out/value_contrast.txt
bash tools/hybrid_stats.sh contrast dplem util goal  | tee -a out/value_contrast.txt
bash tools/hybrid_stats.sh contrast dplem dp   goal  | tee -a out/value_contrast.txt
bash tools/hybrid_stats.sh contrast dplem dp   full  | tee -a out/value_contrast.txt
awk '
/dp-dpshuf goal/ && /SIGNIFICANT/ { ok=1 }
END{ if (!ok){ print "VAL-LEARNED-FAIL shuffled DP labels are not worse: the correspondence is unused"; exit 1 }
     print "VAL-LEARNED-PASS shuffled DP labels collapse (same multiset, no correspondence)" }' out/value_contrast.txt

echo "== 3. the central contrast: exact DP value vs single-step utility"
awk '
/dp-util goal/ && /INCONCLUSIVE/ { inc=1 }
/dp-util goal/ && /SIGNIFICANT/  { sig=1 }
END{
  if (sig) print "VAL-CLAIM exact DP value beats utility at 2SE: report as a positive learning result"
  else print "VAL-TARGET-VERDICT DP-VALUE-NOT-DEMONSTRATED (dp-util goal inside 2SE; composition still carried by the symbolic action space)"
}' out/value_contrast.txt | tee out/value_verdict.txt
if grep -q 'DP-VALUE-NOT-DEMONSTRATED' out/value_verdict.txt; then
  grep -q 'DP-VALUE-NOT-DEMONSTRATED' ../../docs/release-0262.md \
    || { echo "VAL-TARGET-FAIL release note does not state DP-VALUE-NOT-DEMONSTRATED"; exit 1; }
  echo "VAL-TARGET-PASS verdict stated in docs/release-0262.md"
fi

echo "== 4. VALMODE=0 path is inert (conservation)"
ra="--train --seeds 1 --seed-base 31 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 6 --goaldepth 3 --goal-scan --dfs --branch 3"
./bin/v_util $ra > out/val_cons_a.txt 2>&1
./bin/v_util $ra > out/val_cons_b.txt 2>&1
cmp -s out/val_cons_a.txt out/val_cons_b.txt || { echo "CONSERVATION-FAIL VALMODE=0 is not deterministic"; exit 1; }
grep -q 'DP-AUDIT' out/val_cons_a.txt && { echo "CONSERVATION-FAIL label audit ran without --dp-bruteforce-check"; exit 1; }
echo "CONSERVATION-PASS VALMODE=0 deterministic and free of DP label work"

echo "== 5. aggregation schema, table identity, mutation regression"
bash tools/hybrid_stats.sh verify out/value.txt "$SEEDS"
bash gate_regression_hybrid.sh out/value.txt probes_v "$SEEDS"

echo "== 6. weight header carries the value-label mode"
ra2="--train --seeds 1 --seed-base 31 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/v_dp $ra2 --load-weights probes_v/util/w_31.bin --no-bound > out/vh_a.txt 2>&1; ea=$?
./bin/v_dp $ra2 --load-weights probes_v/dp/w_31.bin --no-bound > out/vh_b.txt 2>&1; eb=$?
set -e
[ "$ea" -eq 4 ] || { echo "WHDR-FAIL dp accepted utility-label weights (exit $ea)"; exit 1; }
[ "$eb" -eq 0 ] || { echo "WHDR-FAIL dp rejected its own weights (exit $eb)"; exit 1; }
echo "WHDR-PASS value-label mode in the header; cross-label load refused"

echo "== 7. LLVM identity + sanitizers on the DP-label arm"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -Iinclude -Isrc src/pst.c -o bin/v_dp_O$O -lm
  ./bin/v_dp_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3 > out/val_id_O$O.txt 2>&1
done
diff -q out/val_id_O0.txt out/val_id_O2.txt >/dev/null && diff -q out/val_id_O0.txt out/val_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DVALMODE=1 -Iinclude -Isrc src/pst.c -o bin/v_dp_asan -lm
./bin/v_dp_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 3 > out/val_asan.txt 2> out/val_asan.err
grep -q 'Sanitizer' out/val_asan.err && { echo ASAN-FAIL; cat out/val_asan.err; exit 1; }
echo "LLVM-PASS O0/O2/O3 byte-identical; ASAN+UBSAN clean (DP labels, budget 4, depth 4; the label has cost C(n,<=budget) so the identity gate runs at the evaluation budget)"
echo "V0262-DPVALUE-PASS"