#!/usr/bin/env bash
# 0.0267 gates: recombination matrix + label-DP budget fix.
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"
export PROBES=probes_x
export ARMS="A_nocost B_pair16 C_pair64 D_pair16_b5 E_pair16_e6 F_pair16_intg G_pair16_lift H_pair16_focus"
row () { awk -v a="$1" -v k="$2" '$1=="ARM" && $2==a{ for(i=3;i<=NF;i++){ split($i,kv,"="); if(kv[1]==k) print kv[2] } }' out/recomb.txt; }

echo "== 1. gradient check, eight arms"
for f in "A_nocost:-DVALMODE=1 -DLABEL_NCOST=1" \
         "B_pair16:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1" \
         "D_pair16_b5:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1" \
         "E_pair16_e6:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1" \
         "F_pair16_intg:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -DINTEGRAL=1" \
         "G_pair16_lift:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -DLIFTED=1 -DLIFT_RHO=0.25" \
         "H_pair16_focus:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -DFOCUS=1" \
         "C_pair64:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1"; do
  n="${f%%:*}"; fl="${f#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $fl src/pst.c -o "bin/gcx_$n" -lm
  "./bin/gcx_$n" --gradcheck > "out/gcx_$n.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gcx_$n.txt" || { echo "RECOMB-GRADCHECK-FAIL $n"; exit 1; }
done
echo "RECOMB-GRADCHECK-PASS (8 arms)"

echo "== 2. labels independent of the search budget; memo healthy"
for s in 71 72; do
  for b in 4 6; do
    ./bin/x_B_pair16 --train --seeds 1 --seed-base $s --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
      --goal-scan --balance-reward --goaldepth 2 --eval-budget $b --no-bound > "out/lb_${s}_${b}.txt" 2>&1
    fail=$(grep -o 'store_fail=[0-9]*' "out/lb_${s}_${b}.txt" | head -1 | cut -d= -f2)
    [ "$fail" = "0" ] || { echo "LABEL-BUDGET-FAIL store_fail=$fail at budget $b"; exit 1; }
    rem=$(grep -o 'label_rem_max=[0-9]*' "out/lb_${s}_${b}.txt" | head -1 | cut -d= -f2)
    [ "$rem" = "4" ] || { echo "LABEL-BUDGET-FAIL label_rem_max=$rem"; exit 1; }
  done
done
echo "LABEL-BUDGET-PASS (label_rem_max=4 for budgets 4 and 6, store_fail=0)"

echo "== 3. budget ladder (the overflow regression)"
CFG="--collect full --sample sub --train-n 8 --val-n 4 --test-n 4 --goal-scan --balance-reward"
for b in 4 5 6; do
  t0=$(date +%s%N)
  ./bin/x_A_nocost --train --seeds 1 --seed-base 71 --epochs 1 $CFG --goaldepth 4 \
    --eval-budget $b --dfs --branch 3 --subsume 1 --prop 1 --no-bound > "out/ladder_$b.txt" 2>&1
  t1=$(date +%s%N); ms=$(( (t1-t0)/1000000 ))
  [ "$ms" -lt 30000 ] || { echo "BUDGET-LADDER-FAIL budget $b took ${ms}ms"; exit 1; }
  printf "  budget %s: %s ms\n" "$b" "$ms"
done
echo "BUDGET-LADDER-PASS (all budgets under 30 s)"

echo "== 4. eval budget above MAXBUDGET fails loudly"
set +e
./bin/x_A_nocost --train --seeds 1 --train-n 4 --goal-scan --eval-budget 9 > out/guard.txt 2>&1; ge=$?
set -e
grep -q 'EVAL-BUDGET-FAIL' out/guard.txt || { echo "BUDGET-GUARD-FAIL (exit $ge)"; exit 1; }
echo "BUDGET-GUARD-PASS"

echo "== 5. claims and ceilings"
bash tools/hybrid_stats.sh contrast B_pair16 A_nocost goal | tee out/recomb_contrast.txt
bash tools/hybrid_stats.sh contrast D_pair16_b5 B_pair16 goal | tee -a out/recomb_contrast.txt
bash tools/hybrid_stats.sh contrast C_pair64 B_pair16 goal | tee -a out/recomb_contrast.txt
awk '
/B_pair16-A_nocost goal/ && /SIGNIFICANT/ { b=1 }
/D_pair16_b5-B_pair16 goal/ && /SIGNIFICANT/ { d=1 }
END{ if (b && d) print "RECOMB-CLAIM-PASS contracts and wider branching both significant"
     else { print "RECOMB-CLAIM-FAIL expected significant contrasts are missing"; exit 1 } }' out/recomb_contrast.txt
awk -v d="$(row D_pair16_b5 dfs)" -v b="$(row B_pair16 dfs)" -v e="$(row E_pair16_e6 dfs)" 'BEGIN{
  if (!(d+0 <= 0.9286)) { printf "CEILING-FAIL D %.4f exceeds the contract-action ceiling 0.9286\n", d; exit 1 }
  if (!(e+0 <= 1.0000)) { printf "CEILING-FAIL E %.4f exceeds the budget-6 bound\n", e; exit 1 }
  printf "CEILING-PASS D=%.4f <= 0.9286 (contract exhaustive), B=%.4f; E=%.4f <= 1.0000 (budget-6 bound)\n", d, b, e }'
grep -q '0.9286' ../../docs/release-0267.md || { echo "CEILING-FAIL note lacks the contract ceiling"; exit 1; }

echo "== documentation hygiene"
bash tools/doc_check.sh ../../docs/release-0267.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 6. aggregation + mutation regression"
bash tools/hybrid_stats.sh verify out/recomb.txt "$SEEDS"
bash gate_regression_hybrid.sh out/recomb.txt probes_x "$SEEDS"

echo "== 7. header tag: contract/branch configuration"
ra="--train --seeds 1 --seed-base 71 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/x_B_pair16 $ra --pair-keep 64 --load-weights probes_x/B_pair16/w_71.bin --no-bound > out/xh_a.txt 2>&1; ea=$?
./bin/x_B_pair16 $ra --load-weights probes_x/B_pair16/w_71.bin --no-bound > out/xh_b.txt 2>&1; eb=$?
set -e
[ "$ea" -eq 4 ] || { echo "WHDR-FAIL pair_keep change not detected (exit $ea)"; exit 1; }
[ "$eb" -eq 0 ] || { echo "WHDR-FAIL own weights rejected"; exit 1; }
echo "WHDR-PASS"

echo "== 8. LLVM identity + sanitizers (best arm)"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 \
    -Iinclude -Isrc src/pst.c -o bin/x_O$O -lm
  ./bin/x_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 3 > out/x_id_O$O.txt 2>&1
done
diff -q out/x_id_O0.txt out/x_id_O2.txt >/dev/null && diff -q out/x_id_O0.txt out/x_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -Iinclude -Isrc src/pst.c -o bin/x_asan -lm
./bin/x_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 5 > out/x_asan.txt 2> out/x_asan.err
grep -q 'Sanitizer' out/x_asan.err && { echo ASAN-FAIL; cat out/x_asan.err; exit 1; }
echo "LLVM-PASS"
echo "V0267-RECOMB-PASS"
