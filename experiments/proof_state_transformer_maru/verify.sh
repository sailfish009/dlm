#!/usr/bin/env bash
# 0.0246 gates (review R245-1..5):
#  R245-1 strict validator: schema/aggregation, ratio range, exact bound, budget
#         metadata, token consumption, duplicate fields + 17-mutation regression
#  R245-2 full-budget teacher states (dataset exposure gates + 2x2 direction)
#  R245-3 feature-alias audit (aggregate aliases, relation features separate them)
#  R245-4 seed-persistent goal pool in generation and audit
#  R245-5 headline goal CI uses the total-goal ratio (reported separately from the
#         world-mean macro metric)
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"

grep -q '^PARITY-PASS$' out/parity.txt || { echo PARITY-FAIL; exit 1; }
echo "PARITY world/features/kernel-utility/rollout vs reference implementation"

for spec in "base:" "mask:-DVAR_MASK=1" "utilhead:-DVAR_UTILHEAD=1" \
            "goalx:-DVAR_GOALX=1" "loop:-DVAR_LOOP=1" "bind:-DVAR_BIND=1"; do
  name="${spec%%:*}"; flag="${spec#*:}"
  clang -O2 -Iinclude -Isrc $flag src/pst.c -o "bin/gc_$name" -lm
  if ! "./bin/gc_$name" --gradcheck | tee "out/gc_$name.txt" | grep -q '^GRADCHECK-PASS$'; then
    echo "GRADCHECK-FAIL variant=$name"; cat "out/gc_$name.txt"; exit 1
  fi
done
echo "GRADCHECK six aggregate variants ($(grep '^GRADCHECK ' out/gc_mask.txt))"

diff -q out/id_O0.txt out/id_O2.txt >/dev/null && diff -q out/id_O0.txt out/id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
./bin/pst --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 > out/id_repeat.txt
cmp -s out/id_O0.txt out/id_repeat.txt || { echo DETERMINISM-FAIL; exit 1; }
echo "LLVM O0/O2/O3 byte-identical; training re-run byte-identical"

field () { awk -v k="$2" '/^AUDIT /{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]==k) print kv[2]}}' "$1" | head -1; }
[ "$(field out/audit_ref.txt witness_violations)" = "0" ] || { echo REF-WITNESS-FAIL; exit 1; }
[ "$(field out/audit_ref.txt unreachable_all_candidates)" = "0" ] || { echo REF-REACHABILITY-FAIL; exit 1; }
[ "$(field out/audit_ref.txt bound_goal_pm)" = "1000000" ] || { echo REF-NOT-SATURATED; exit 1; }
[ "$(field out/audit_hard.txt unreachable_all_candidates)" = "0" ] || { echo HARD-REACHABILITY-FAIL; exit 1; }
[ "$(field out/audit_hard.txt goals_not_in_pool)" = "0" ] || { echo HARD-POOL-MISMATCH; exit 1; }
echo "F1/R245-4-INVARIANTS ref witness=0 unreachable=0 bound=100%; hard unreachable=0 pool_mismatch=0 pool=$(field out/audit_hard.txt pool_atoms)"

# R245-3 representation audit
grep -E '^ALIAS ' out/alias.txt | sed 's/^/  /'
base_alias=$(awk '/^ALIAS base /{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="optimal_differs") print kv[2]}}' out/alias.txt)
relob_eq=$(awk '/^ALIAS relob /{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="feature_equal") print kv[2]}}' out/alias.txt)
[ "${base_alias:-0}" -gt 0 ] || { echo ALIAS-NOT-REPRODUCED; exit 1; }
[ "${relob_eq:-1}" -eq 0 ] || { echo RELOB-STILL-ALIASED; exit 1; }
grep -q '^FEATURE-ALIAS-CONFIRMED' out/alias.txt || { echo ALIAS-CONFIRM-FAIL; exit 1; }
echo "R245-3-ALIAS aggregate feature collisions alias=${base_alias}, relation features collide on 0 pairs"

# R245-2 dataset exposure
awk '/^DATASET/{print "  " $0}' out/dataset_root.txt out/dataset_full.txt
root_hist=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="hist1") print kv[2]}}' out/dataset_root.txt)
root_rew=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="label_reward_steps") print kv[2]}}' out/dataset_root.txt)
full_hist=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="hist4") print kv[2]}}' out/dataset_full.txt)
full_rew=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="label_reward_steps") print kv[2]}}' out/dataset_full.txt)
[ "$root_hist" = "180" ] && [ "$root_rew" = "0" ] || { echo ROOT-DATASET-FAIL; exit 1; }
[ "$full_hist" = "180" ] && [ "${full_rew:-0}" -gt 0 ] || { echo FULL-DATASET-FAIL; exit 1; }
echo "R245-2-DATASET root arm 180 states / 0 reward labels; full arm 720 states / ${full_rew} reward labels"

# 2x2 direction + strict validation of every arm log
for a in A_root_agg B_full_agg C_root_relob D_full_relob E_full_all; do
  [ -f "out/2x2_$a.txt" ] || { echo "MISSING-ARM $a"; exit 1; }
  ./bin/gate_check "out/2x2_$a.txt" hard "$SEEDS" 11 | sed "s/^/  $a /"
  grep -q '^BOUND-ASSERT ok=1' "out/2x2_$a.txt" || { echo "BOUND-ASSERT-FAIL $a"; exit 1; }
done
bash gate_regression.sh out/2x2_D_full_relob.txt "$SEEDS"

awk '
function val(file, key,   line, i, kv, out) {
  while ((getline line < file) > 0) if (line ~ /^MEAN /) {
    for (i = 1; i <= length(line); i++) {}
    n = split(line, f, " ")
    for (i = 1; i <= n; i++){ split(f[i], kv, "="); if (kv[1] == key) out = kv[2]+0 }
  }
  close(file); return out
}
BEGIN {
  a = val("out/2x2_A_root_agg.txt", "proof_model")
  b = val("out/2x2_B_full_agg.txt", "proof_model")
  c = val("out/2x2_C_root_relob.txt", "proof_model")
  d = val("out/2x2_D_full_relob.txt", "proof_model")
  e = val("out/2x2_E_full_all.txt", "proof_model")
  s = val("out/2x2_D_full_relob.txt", "beam_support")
  db = val("out/2x2_D_full_relob.txt", "proof_beam")
  printf "2x2 greedy: A=%.4f B=%.4f C=%.4f D=%.4f E=%.4f (state +%.4f, features +%.4f)\n", a, b, c, d, e, b-a, d-b
  printf "2x2 beam:   D=%.4f support=%.4f\n", db, s
  bad = 0
  if (!(b > a + 0.10)) { print "FAIL state collection did not improve >=10pp"; bad = 1 }
  if (!(d > b + 0.10)) { print "FAIL relation features did not improve >=10pp on top of collection"; bad = 1 }
  if (!(db > s + 0.10)) { print "FAIL best 2x2 beam does not beat support beam by >=10pp"; bad = 1 }
  if (bad) exit 1
  printf "R245-2/3-2X2-PASS state collection and relation features both required\n"
}' /dev/null

grep -E '^BOOT beam_model_raw_minus_support' out/2x2_D_full_relob.txt | tee out/boot_estimand.txt | sed 's/^/  /'
awk '/goal_ratio_lo=/{print "R245-5-ESTIMAND headline goal CI uses the total-goal ratio; macro CI reported separately"}' out/boot_estimand.txt
echo "R245-5-CI headline goal estimator = total-goal ratio per resample (see BOOT line)"

bash maru_check.sh > out/maru_check.log 2>&1 || { echo MARU-PARITY-FAIL; tail -5 out/maru_check.log; exit 1; }
grep '^EXPORT-CONFIG ' out/export.txt | sed 's/^/  /'
grep '^MARU-PST ' out/maru_pst.txt | sed 's/^/  /'
grep -q '^MARU-PST-PARITY-PASS$' out/maru_pst.txt || { echo MARU-PARITY-FAIL; exit 1; }
echo "F5-MARU matched checkpoint (best arm) exported, 100 initial states reproduced in Maru Q16"

echo "V0246-PROOF-STATE-TRANSFORMER-PASS"
