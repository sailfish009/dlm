#!/usr/bin/env bash
# 0.0266 gates: label decomposition (review N1-N4).
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-15}"
export PROBES=probes_q
export ARMS="dp dp_steps dp_nocost onpath onpathshuf"

echo "== 1. gradient check across the five label regimes"
for f in "dp:-DVALMODE=1" "dp_steps:-DVALMODE=1 -DLABEL_STEPS=1" \
         "dp_nocost:-DVALMODE=1 -DLABEL_NCOST=1" "onpath:-DVALMODE=3" "onpathshuf:-DVALMODE=4"; do
  n="${f%%:*}"; fl="${f#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $fl src/pst.c -o "bin/gcq_$n" -lm
  "./bin/gcq_$n" --gradcheck > "out/gcq_$n.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gcq_$n.txt" || { echo "DECOMP-GRADCHECK-FAIL $n"; exit 1; }
  printf "  %-11s %s\n" "$n" "$(grep '^GRADCHECK ' out/gcq_$n.txt)"
done
echo "DECOMP-GRADCHECK-PASS"

echo "== 2. census is read from the TRAINING log, per split (review N1)"
for a in dp dp_steps dp_nocost onpath onpathshuf; do
  line=$(grep -h 'split=train' "probes_q/$a/train_51.log" | head -1)
  [ -n "$line" ] || { echo "CENSUS-TRAIN-FAIL missing census in train log of $a"; exit 1; }
  printf "  %-11s %s\n" "$a" "$(echo "$line" | sed 's/^LABELCENSUS //')"
done
# the eval-run census must NOT be used for the mechanism claim
if grep -q 'top_share=0.180' out/decomp0266.txt 2>/dev/null; then
  echo "CENSUS-TRAIN-FAIL the eval-run census leaked into the table"; exit 1
fi
echo "CENSUS-TRAIN-PASS"

echo "== 3. shuffle control: the correspondence is used"
bash tools/hybrid_stats.sh contrast onpath onpathshuf goal | tee out/decomp_contrast.txt
bash tools/hybrid_stats.sh contrast dp_nocost dp goal | tee -a out/decomp_contrast.txt
bash tools/hybrid_stats.sh contrast dp_nocost dp full | tee -a out/decomp_contrast.txt
bash tools/hybrid_stats.sh contrast dp_nocost dp proof_model | tee -a out/decomp_contrast.txt
bash tools/hybrid_stats.sh contrast dp_steps dp goal | tee -a out/decomp_contrast.txt
bash tools/hybrid_stats.sh contrast onpath dp_nocost goal | tee -a out/decomp_contrast.txt
awk '
/onpath-onpathshuf goal/ && /SIGNIFICANT/ { s=1 }
END{ if (!s){ print "SHUFFLE-CONTROL-FAIL the shuffled label is not worse at 2 SE"; exit 1 }
     print "SHUFFLE-CONTROL-PASS" }' out/decomp_contrast.txt

echo "== 4. localisation: cost term carries the gain, length term is inert"
awk '
/dp_nocost-dp goal/ && /SIGNIFICANT/ { c=1 }
/dp_steps-dp goal/ && /INCONCLUSIVE/ { l=1 }
END{ if (!c){ print "COST-LOCALISATION-FAIL cost removal not significant"; exit 1 }
     if (!l){ print "COST-LOCALISATION-FAIL length term is not inert (revisit the claim)"; exit 1 }
     print "COST-LOCALISATION-PASS cost removal significant, length term inert" }' out/decomp_contrast.txt
grep -q 'dropping the rule-cost penalty' ../../docs/release-0266.md \
  || { echo "COST-LOCALISATION-FAIL release note does not state the mechanism"; exit 1; }

echo "== 5. ceiling at this protocol (review N4)"
grep -q 'bound_goal = 0.8492' ../../docs/release-0266.md || { echo "CEILING-FAIL note lacks the measured bound"; exit 1; }
awk -v g="$(awk '$1=="ARM" && $2=="onpath"{for(i=3;i<=NF;i++){split($i,kv,"="); if(kv[1]=="dfs") print kv[2]}}' out/decomp0266.txt)" \
    -v b="0.8492" 'BEGIN{
  if (!(g+0 > 0 && g+0 <= b+0)) { printf "CEILING-FAIL best arm %s exceeds the bound %s\n", g, b; exit 1 }
  printf "CEILING-PASS best label arm %.4f <= bound %.4f (headroom %.4f)\n", g, b, b-g }'

echo "== documentation hygiene"
bash tools/doc_check.sh ../../docs/release-0266.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 6. aggregation + mutation regression"
bash tools/hybrid_stats.sh verify out/decomp0266.txt "$SEEDS"
bash gate_regression_hybrid.sh out/decomp0266.txt probes_q "$SEEDS"

echo "== 7. weight header carries the label flags"
ra="--train --seeds 1 --seed-base 51 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/q_onpathshuf $ra --load-weights probes_q/onpath/w_51.bin --no-bound > out/qh_a.txt 2>&1; ea=$?
./bin/q_onpath $ra --load-weights probes_q/onpath/w_51.bin --no-bound > out/qh_b.txt 2>&1; eb=$?
set -e
[ "$ea" -eq 4 ] || { echo "WHDR-FAIL shuffled arm accepted unshuffled weights"; exit 1; }
[ "$eb" -eq 0 ] || { echo "WHDR-FAIL onpath rejected its own weights"; exit 1; }
echo "WHDR-PASS"

echo "== 8. LLVM identity + sanitizers"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -DLABEL_NCOST=1 -Iinclude -Isrc src/pst.c -o bin/q_O$O -lm
  ./bin/q_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3 > out/q_id_O$O.txt 2>&1
done
diff -q out/q_id_O0.txt out/q_id_O2.txt >/dev/null && diff -q out/q_id_O0.txt out/q_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -Iinclude -Isrc src/pst.c -o bin/q_asan -lm
./bin/q_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 3 > out/q_asan.txt 2> out/q_asan.err
grep -q 'Sanitizer' out/q_asan.err && { echo ASAN-FAIL; exit 1; }
echo "LLVM-PASS"
echo "V0266-LABELDECOMP-PASS"
