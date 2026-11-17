#!/usr/bin/env bash
# 0.0265 gates: the deductive (proof-path membership) label.
# Fails when:
#   ONPATH-GRADCHECK  a label regime's gradient disagrees with finite differences
#   ONPATH-LABEL      the label census is degenerate (all/none at the top)
#   CONSERVATION      VALMODE=0 is not inert/deterministic
#   CONTRAST          onpath is not significant at 2 SE on goal AND greedy
#                     (a search-only gain would not support "the scorer learned")
#   AGG/WHDR/LLVM/DOC same checks as 0.0264
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-15}"
export PROBES=probes_o15
export ARMS="util dp onpath onpathlem"
row () { awk -v a="$1" -v k="$2" '$1=="ARM" && $2==a{ for(i=3;i<=NF;i++){ split($i,kv,"="); if(kv[1]==k) print kv[2] } }' out/onpath.txt; }

echo "== 1. gradient check across label regimes"
for f in "util:" "dp:-DVALMODE=1" "dpshuf:-DVALMODE=2" "onpath:-DVALMODE=3" "onpathlem:-DVALMODE=3 -DLEMMA=1 -DPAIRMODE=1"; do
  n="${f%%:*}"; fl="${f#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $fl src/pst.c -o "bin/gco_$n" -lm
  "./bin/gco_$n" --gradcheck > "out/gco_$n.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gco_$n.txt" || { echo "GRADCHECK-FAIL $n"; cat "out/gco_$n.txt"; exit 1; }
  printf "  %-10s %s\n" "$n" "$(grep '^GRADCHECK ' out/gco_$n.txt)"
done
echo "ONPATH-GRADCHECK-PASS"

echo "== 2. label census (sharpness of the justified-derivation target)"
grep -h '^ONPATH' probes_o15/onpath/cfg_4_4.txt | head -1 | tee out/onpath_census.txt | sed 's/^/  /'
awk '{ for(i=1;i<=NF;i++){ split($i,kv,"="); v[kv[1]]=kv[2]+0 }
  if (!(v["top_share"] > 0 && v["top_share"] < 1)) { printf "ONPATH-LABEL-FAIL top_share=%s is degenerate\n", v["top_share"]; exit 1 }
  if (!(v["states"] > 0)) { print "ONPATH-LABEL-FAIL no labelled states"; exit 1 }
  printf "ONPATH-LABEL-PASS %d states, top_share=%.3f (a usable but non-trivial target)\n", v["states"], v["top_share"] }' out/onpath_census.txt

echo "== 3. VALMODE=0 conservation"
ra="--train --seeds 1 --seed-base 51 --epochs 3 --train-n 40 --val-n 40 --test-n 40 --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3"
./bin/gco_util $ra > out/on_cons_a.txt 2>&1
./bin/gco_util $ra > out/on_cons_b.txt 2>&1
cmp -s out/on_cons_a.txt out/on_cons_b.txt || { echo "CONSERVATION-FAIL"; exit 1; }
grep -q '^ONPATH' out/on_cons_a.txt && { echo "CONSERVATION-FAIL census ran with VALMODE=0"; exit 1; }
echo "CONSERVATION-PASS"

echo "== 4. the decisive contrasts (goal and scorer-only greedy)"
bash tools/hybrid_stats.sh contrast onpath util goal | tee out/onpath_contrast.txt
bash tools/hybrid_stats.sh contrast onpath util full | tee -a out/onpath_contrast.txt
bash tools/hybrid_stats.sh contrast onpath util proof_model | tee -a out/onpath_contrast.txt
bash tools/hybrid_stats.sh contrast onpath dp goal | tee -a out/onpath_contrast.txt
bash tools/hybrid_stats.sh contrast onpathlem onpath goal | tee -a out/onpath_contrast.txt
bash tools/hybrid_stats.sh contrast onpathlem util goal | tee -a out/onpath_contrast.txt
awk '
/onpath-util goal/ && /SIGNIFICANT/ { g=1 }
/onpath-util proof_model/ && /SIGNIFICANT/ { s=1 }
END{
  if (g && s) print "ONPATH-CLAIM-PASS PROOF-PATH-LABEL-DEMONSTRATED (goal and greedy both beyond 2 SE)"
  else { print "ONPATH-CLAIM-FAIL the deductive label did not beat utility on goal and greedy at 2 SE"; exit 1 }
}' out/onpath_contrast.txt | tee out/onpath_verdict.txt
grep -q 'PROOF-PATH-LABEL-DEMONSTRATED' ../../docs/release-0265.md \
  || { echo "ONPATH-CLAIM-FAIL release note does not state the verdict"; exit 1; }

echo "== documentation hygiene"
bash tools/doc_check.sh ../../docs/release-0265.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 5. aggregation + mutation regression"
bash tools/hybrid_stats.sh verify out/onpath.txt "$SEEDS"
bash gate_regression_hybrid.sh out/onpath.txt probes_o15 "$SEEDS"

echo "== 6. weight header carries the label mode"
ra2="--train --seeds 1 --seed-base 51 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/o_onpath $ra2 --load-weights probes_o15/util/w_51.bin --no-bound > out/oh_a.txt 2>&1; ea=$?
./bin/o_onpath $ra2 --load-weights probes_o15/onpath/w_51.bin --no-bound > out/oh_b.txt 2>&1; eb=$?
set -e
[ "$ea" -eq 4 ] || { echo "WHDR-FAIL onpath accepted util weights (exit $ea)"; exit 1; }
[ "$eb" -eq 0 ] || { echo "WHDR-FAIL onpath rejected its own weights (exit $eb)"; exit 1; }
echo "WHDR-PASS label mode in the header"

echo "== 7. LLVM identity + sanitizers (onpath)"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=3 -Iinclude -Isrc src/pst.c -o bin/o_O$O -lm
  ./bin/o_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3 > out/on_id_O$O.txt 2>&1
done
diff -q out/on_id_O0.txt out/on_id_O2.txt >/dev/null && diff -q out/on_id_O0.txt out/on_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DVALMODE=3 -DLEMMA=1 -DPAIRMODE=1 -Iinclude -Isrc src/pst.c -o bin/o_asan -lm
./bin/o_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 3 > out/on_asan.txt 2> out/on_asan.err
grep -q 'Sanitizer' out/on_asan.err && { echo ASAN-FAIL; cat out/on_asan.err; exit 1; }
echo "LLVM-PASS O0/O2/O3 byte-identical; ASAN+UBSAN clean (onpath+contracts)"
echo "V0265-ONPATH-PASS"
