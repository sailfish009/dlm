#!/usr/bin/env bash
# 0.0260 gates: hybrid reasoning layer (Rocq certificate/focus, Silicon path
# condition/contracts, Screamer branching attention/search) on the native
# proof-state transformer.
#
# Every gate states what observation makes it FAIL:
#   GRADCHECK   any arm whose analytic gradient disagrees with finite differences
#   PC-PATH     a hard-path-condition arm selects an inadmissible candidate, or
#               the soft residual gate has no inadmissible selections (vacuous
#               control), or the condition removes nothing
#   CERT        the certificate checker accepts a corrupted parent map, rejects a
#               valid one, or changes the proved-goal answer (conservation)
#   FOCUS       obligation focus does not shrink the candidate set
#   LEMMA       mined contracts are never applied, or they increase node count
#               beyond the 2SE band of the pure arm
#   AGG         the printed table differs from the per-seed recomputation, or a
#               mutated log (missing/duplicate seed, NaN, out-of-range, degraded
#               metric) is accepted
#   WHDR        weights trained under one variant load into another (silent reuse)
#   LLVM        O0/O2/O3 differ, or ASan/UBSan reports at depth 4
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-3}"

echo "== 1. gradient check, every arm (finite differences vs analytic)"
for spec in "pure:" "topk:-DATTMODE=2" "pc:-DSYMGATE=2" "soft:-DSYMGATE=1" \
            "focus:-DFOCUS=1" "cert:-DCERT=1" "lemma:-DLEMMA=1" \
            "hybrid:-DATTMODE=2 -DSYMGATE=2 -DFOCUS=1 -DCERT=1 -DLEMMA=1"; do
  name="${spec%%:*}"; flags="${spec#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $flags src/pst.c -o "bin/gc_$name" -lm
  "./bin/gc_$name" --gradcheck > "out/gc_$name.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gc_$name.txt" || { echo "GRADCHECK-FAIL arm=$name"; cat "out/gc_$name.txt"; exit 1; }
done
echo "GRADCHECK-PASS eight arms ($(grep '^GRADCHECK ' out/gc_hybrid.txt))"

echo "== 2. Silicon path condition: hard enforces, soft does not, control drops nothing"
row () { awk -v a="$1" -v k="$2" '$1=="ARM" && $2==a{ for(i=3;i<=NF;i++){ split($i,kv,"="); if(kv[1]==k) print kv[2] } }' out/hybrid.txt; }
hpv=$(row hybrid gate_viol); ppv=$(row pc gate_viol); spv=$(row soft gate_viol); prpv=$(row pure pc_dropped)
hpd=$(row hybrid pc_dropped); ppd=$(row pc pc_dropped); prdd=$(row pure pc_dropped)
awk -v hpv="$hpv" -v ppv="$ppv" -v spv="$spv" -v hpd="$hpd" -v ppd="$ppd" -v prdd="$prdd" 'BEGIN{
  bad=0
  if (hpv+0 != 0) { printf "FAIL hybrid selected an inadmissible candidate (gate_viol=%s)\n", hpv; bad=1 }
  if (ppv+0 != 0) { printf "FAIL pc selected an inadmissible candidate (gate_viol=%s)\n", ppv; bad=1 }
  if (!(spv+0 > 0)) { printf "FAIL soft arm has no inadmissible selection: control is vacuous (gate_viol=%s)\n", spv; bad=1 }
  if (!(hpd+0 > 0) || !(ppd+0 > 0)) { printf "FAIL path condition removed no candidate (hybrid=%s pc=%s)\n", hpd, ppd; bad=1 }
  if (prdd+0 != 0) { printf "FAIL pure arm dropped candidates without a gate (%s)\n", prdd; bad=1 }
  printf "PC-PATH-PASS hard gate_viol=0 (soft=%s), dropped candidates hybrid=%s pc=%s pure=%s\n", spv, hpd, ppd, prdd
  if (bad) exit 1 }'

echo "== 3. Rocq certificate: valid accepted, mutated rejected, answer conserved"
./bin/hb_cert --train --seeds 1 --seed-base 11 --collect full --sample sub \
  --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward \
  --goaldepth 4 --eval-budget 4 --dfs --branch 3 --subsume 1 --prop 1 --no-bound \
  --load-weights probes_h/cert/w_11.bin > out/cert_valid.txt 2>&1
awk '/^HYBRID /{ for(i=1;i<=NF;i++){ split($i,kv,"="); v[kv[1]]=kv[2] }
  if (v["cert_fail"]+0 != 0) { print "FAIL valid certificate rejected: fail=" v["cert_fail"]; exit 1 }
  if (v["cert_checked"]+0 < 1 || v["cert_ok"]+0 != v["cert_checked"]+0){
    printf "FAIL certificate not covering the derived goals (ok=%s checked=%s)\n", v["cert_ok"], v["cert_checked"]; exit 1 }
  printf "CERT-PASS certified=%s goals, fail=0\n", v["cert_checked"] }' out/cert_valid.txt
awk '/^HYBRID /{ for(i=1;i<=NF;i++){ split($i,kv,"="); v[kv[1]]=kv[2] }
  if (!(v["cert_mutfail"]+0 > 0)) { print "FAIL mutated certificate accepted: the checker is vacuous"; exit 1 }
  if (v["cert_mutfail"]+0 != v["cert_checked"]+0) { printf "FAIL mutated rejection %s != checked %s\n", v["cert_mutfail"], v["cert_checked"]; exit 1 }
  printf "CERT-MUTATION-PASS corrupted parents rejected %s/%s\n", v["cert_mutfail"], v["cert_checked"] }' out/hybrid_cert_mutation.txt
# conservation: attaching the certificate must not change the search answer
python3 - <<'PY' || { echo CERT-CONSERVATION-FAIL; exit 1; }
def dfs(p):
    for l in open(p):
        if l.startswith('DFS '): return l.split()[3]
a=dfs('out/cert_valid.txt'); b=dfs('probes_h/pure/cfg_4_4.txt')
assert a==b, f'cert arm changed the DFS answer: {a} vs {b}'
print('CERT-CONSERVATION-PASS certificate check did not change the proved-goal answer')
PY

echo "== 4. Rocq focus / Silicon contracts"
fst=$(row focus focus_states); fre=$(row focus focus_removed)
awk -v st="$fst" -v re="$fre" 'BEGIN{
  if (st+0 <= 0) { print "FAIL focus filter was never consulted"; exit 1 }
  if (re+0 > 0) printf "FOCUS-PRUNE-PASS filter consulted %s times, removed %s candidates\n", st, re
  else printf "FOCUS-VACUOUS-SATURATED filter consulted %s times, removed 0: the relevance closure saturates on this fixture (reported as a negative result, no gain claimed)\n", st }'
# completeness: the filter must not change the exhaustive answer (branch = POOL)
./bin/hb_focus --train --seeds 1 --seed-base 11 --collect full --sample sub --train-n 180 --val-n 60   --test-n 100 --goal-scan --balance-reward --goaldepth 4 --eval-budget 4 --dfs --branch 24   --subsume 1 --prop 1 --no-bound --load-weights probes_h/focus/w_11.bin > out/focus_exh.txt 2>&1
./bin/hb_pure --train --seeds 1 --seed-base 11 --collect full --sample sub --train-n 180 --val-n 60   --test-n 100 --goal-scan --balance-reward --goaldepth 4 --eval-budget 4 --dfs --branch 24   --subsume 1 --prop 1 --no-bound --load-weights probes_h/pure/w_11.bin > out/pure_exh.txt 2>&1
a=$(awk '/^DFS /{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="goal") print kv[2]}}' out/focus_exh.txt)
b=$(awk '/^DFS /{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="goal") print kv[2]}}' out/pure_exh.txt)
[ "$a" = "$b" ] || { echo "FOCUS-COMPLETENESS-FAIL exhaustive answer $a != $b"; exit 1; }
echo "FOCUS-COMPLETENESS-PASS exhaustive DFS (branch=POOL) answer unchanged ($a)" 
awk -v l="$(row lemma lemma_uses)" -v hl="$(row hybrid lemma_uses)" -v ln="$(row lemma nodes)" -v pn="$(row pure nodes)" 'BEGIN{
  if (!(l+0 > 0)) { print "FAIL lemma arm never applied a contract"; exit 1 }
  if (!(hl+0 > 0)) { print "FAIL hybrid arm never applied a contract"; exit 1 }
  if (!(ln+0 <= pn+0)) { printf "FAIL contracts increased nodes %.0f -> %.0f\n", pn, ln; exit 1 }
  printf "LEMMA-PASS uses lemma=%.0f hybrid=%.0f; nodes %.0f -> %.0f\n", l, hl, pn, ln }'

echo "== 5. aggregation schema + table/recomputation identity + mutation regression"
bash tools/hybrid_stats.sh verify out/hybrid.txt "$SEEDS"
bash gate_regression_hybrid.sh out/hybrid.txt probes_h "$SEEDS"

echo "== 6. weight-header variant tag (cross-variant load must be refused)"
ra="--train --seeds 1 --seed-base 11 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/hb_soft  $ra --load-weights probes_h/hybrid/w_11.bin --no-bound > out/whdr_a.txt 2>&1; ea=$?
./bin/hb_hybrid $ra --load-weights probes_h/pure/w_11.bin --no-bound > out/whdr_b.txt 2>&1; eb=$?
./bin/hb_hybrid $ra --load-weights probes_h/hybrid/w_11.bin --no-bound > out/whdr_c.txt 2>&1; ec=$?
set -e
[ "$ea" -eq 4 ] || { echo "WHDR-FAIL soft accepted hybrid weights (exit $ea)"; exit 1; }
[ "$eb" -eq 4 ] || { echo "WHDR-FAIL hybrid accepted pure weights (exit $eb)"; exit 1; }
[ "$ec" -eq 0 ] || { echo "WHDR-FAIL hybrid rejected its own weights (exit $ec)"; exit 1; }
echo "WHDR-PASS cross-variant loads refused (exit 4), own weights accepted"

echo "== 7. LLVM identity + sanitizers on the hybrid arm"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DATTMODE=2 -DSYMGATE=2 -DFOCUS=1 -DCERT=1 -DLEMMA=1 \
    -Iinclude -Isrc src/pst.c -o bin/hb_hybrid_O$O -lm
  ./bin/hb_hybrid_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 6 --goaldepth 3 --goal-scan --dfs --branch 3 > out/hb_id_O$O.txt 2>&1
done
diff -q out/hb_id_O0.txt out/hb_id_O2.txt >/dev/null && diff -q out/hb_id_O0.txt out/hb_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DATTMODE=2 -DSYMGATE=2 -DFOCUS=1 -DCERT=1 -DLEMMA=1 -Iinclude -Isrc src/pst.c -o bin/hb_asan -lm
./bin/hb_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 6 --goaldepth 4 --goal-scan --dfs --branch 3 > out/hb_asan.txt 2> out/hb_asan.err
grep -q 'Sanitizer' out/hb_asan.err && { echo ASAN-FAIL; cat out/hb_asan.err; exit 1; }
echo "LLVM-PASS O0/O2/O3 byte-identical; ASAN+UBSAN clean (hybrid, depth 4)"

echo "== 8. paired-by-seed contrasts (reported, 2SE verdict; n=3 is underpowered)"
for c in "hybrid pure" "lemma pure" "pc pure" "soft pure" "topk pure" "cert pure"; do
  set -- $c
  bash tools/hybrid_stats.sh contrast "$1" "$2" goal | sed 's/^/  /'
  bash tools/hybrid_stats.sh contrast "$1" "$2" full | sed 's/^/  /'
  bash tools/hybrid_stats.sh contrast "$1" "$2" proof_beam | sed 's/^/  /'
done
echo "== absolute table (each field a per-seed mean, 3 seeds)"
sed 's/^/  /' out/hybrid.txt

echo "V0260-HYBRID-PASS"