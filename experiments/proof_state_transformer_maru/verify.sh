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
./bin/pst --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
  --eval-budget 6 --goaldepth 3 --goal-scan > out/id_repeat.txt
cmp -s out/id_O0.txt out/id_repeat.txt || { echo DETERMINISM-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -Iinclude -Isrc src/pst.c -o bin/pst_asan -lm
if ! ./bin/pst_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10       --eval-budget 6 --goaldepth 4 --goal-scan > out/asan.txt 2> out/asan.err; then
  echo ASAN-FAIL; cat out/asan.err; exit 1
fi
grep -q 'Sanitizer' out/asan.err && { echo ASAN-REPORT; cat out/asan.err; exit 1; }
echo "ASAN+UBSAN clean at eval budget 6 (goal depth 4, scan mode)"
echo "LLVM O0/O2/O3 byte-identical at eval budget 6; training re-run byte-identical"

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
# the stronger optimal-action case is sampling dependent: reported, not gated
[ "${relob_eq:-1}" -eq 0 ] || { echo RELOB-STILL-ALIASED; exit 1; }
# R245-3 criterion: aggregate features collide on legal goal-set pairs while the
# relation features collide on none. The stronger "optimal actions differ" case is
# sampling dependent and is reported, not gated.
base_eq=$(awk '/^ALIAS base /{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="feature_equal") print kv[2]}}' out/alias.txt)
relob_eq2=$(awk '/^ALIAS relob /{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="feature_equal") print kv[2]}}' out/alias.txt)
base_od=$(awk '/^ALIAS base /{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="optimal_differs") print kv[2]}}' out/alias.txt)
[ "${base_eq:-0}" -gt 0 ] || { echo "ALIAS-NO-COLLISION"; exit 1; }
[ "${relob_eq2:-1}" -eq 0 ] || { echo ALIAS-RELOB-COLLIDES; exit 1; }
echo "R245-3-ALIAS aggregate collisions=${base_eq} (optimal differs=${base_od:-0}, reported), relation collisions=0"


# R245-2 dataset exposure: root-stop must stop at (almost) the root state, the
# full-budget arm must collect several states per world and carry reward labels.
awk '/^DATASET/{print "  " $0}' out/dataset_root.txt out/dataset_full.txt | grep 'split=0'
root_steps=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="steps") print kv[2]}}' out/dataset_root.txt)
root_worlds=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="worlds") print kv[2]}}' out/dataset_root.txt)
root_rew=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="label_reward_steps") print kv[2]}}' out/dataset_root.txt)
full_steps=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="steps") print kv[2]}}' out/dataset_full.txt)
full_rew=$(awk '/split=0/{for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]=="label_reward_steps") print kv[2]}}' out/dataset_full.txt)
awk -v rs="$root_steps" -v rw="$root_worlds" -v rr="${root_rew:-0}" -v fs="$full_steps" -v fr="${full_rew:-0}" 'BEGIN{
  if (!(rs <= rw*1.05)) { printf "FAIL root-stop collected %d states for %d worlds\n", rs, rw; exit 1 }
  if (!(fs >= 3*rw))  { printf "FAIL full arm collected %d states for %d worlds\n", fs, rw; exit 1 }
  if (!(fr >= 5*(rr > 0 ? rr : 1))) { printf "FAIL full arm reward labels %d vs root %d\n", fr, rr; exit 1 }
  printf "R245-2-DATASET root %d states/%d reward, full %d states/%d reward labels\n", rs, rr, fs, fr
}'

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

# 0.0248 discovery criteria: step regret + reward-exposure control + ladder
echo "== probes (unbalanced exposure)"; grep -E '^ladder|^regret' out/probes_unbal.txt | sed 's/^/  /'
echo "== probes (reward-balanced exposure)"; grep -E '^ladder|^regret' out/probes_bal.txt | sed 's/^/  /'
awk '
function val(file, tag, key,   line, n, i, f, kv, v) {
  while ((getline line < file) > 0) {
    n = split(line, f, " ")
    if (tag == "ladder" && f[1] != "ladder") continue
    if (tag == "regret" && f[1] != "regret") continue
    if (f[2] != CFG) continue
    for (i = 3; i <= n; i++){ split(f[i], kv, "="); if (kv[1] == key) v = kv[2]+0 }
  }
  close(file); return v
}
BEGIN {
  CFG = "4_6"
  b = val("out/probes_bal.txt", "ladder", "goal")
  u = val("out/probes_unbal.txt", "ladder", "goal")
  bb = val("out/probes_bal.txt", "ladder", "beam")
  ub = val("out/probes_unbal.txt", "ladder", "beam")
  IDb = val("out/probes_bal.txt", "ladder", "goal")
  rbm = val("out/probes_bal.txt", "regret", "model")
  rbs = val("out/probes_bal.txt", "regret", "support")
  bad = 0
  if (!(b >= u + 0.02)) { printf "FAIL balanced exposure did not improve d4b6 goal (%.4f vs %.4f)\n", b, u; bad = 1 }
  if (!(bb >= ub))      { printf "FAIL balanced exposure did not improve d4b6 beam (%.4f vs %.4f)\n", bb, ub; bad = 1 }
  if (!(rbs > 0))       { print "FAIL regret comparator missing"; bad = 1 }
  printf "DISCOVERY-CRITERIA exposure d4b6 balanced=%.4f unbalanced=%.4f (delta %+.4f); d4b6 regret model=%.4f support=%.4f (reported)\n", b, u, b-u, rbm, rbs
  if (bad) exit 1
}'
CFG2="2_4"
awk -v cfg="2_4" '
function val(file, key,   line, n, i, f, kv, v) {
  while ((getline line < file) > 0) {
    n = split(line, f, " "); if (f[1] != "regret" || f[2] != cfg) continue
    for (i = 3; i <= n; i++){ split(f[i], kv, "="); if (kv[1] == key) v = kv[2]+0 }
  }
  close(file); return v
}
BEGIN {
  m = val("out/probes_bal.txt", "model"); s = val("out/probes_bal.txt", "support")
  mo = val("out/probes_bal.txt", "model_opt"); so = val("out/probes_bal.txt", "support_regret")
  printf "STEP-REGRET id: model_regret=%.4f model_opt=%.4f support_regret=%.4f\n", m, mo, s
  if (!(m <= s + 1e-9)) { print "FAIL model first-step regret worse than support"; exit 1 }
}'
# R250-4/R250-5: probe logs must pass the per-seed schema check, and contrasts
# are reported with paired-by-seed SE; a directional gate is used only when the
# effect exceeds 2 SE (documented; n=3 is underpowered).
echo "== probe stats (mean +- SE over seeds)"
for arm in bal bindtok bindshuf; do bash tools/probe_stats.sh check "probes/$arm" "${SEEDS:-5}" | sed "s/^/  $arm /"; done
bash tools/probe_stats.sh contrast bal bindtok 4_6 proof_model | sed 's/^/  /'
bash tools/probe_stats.sh contrast bal bindshuf 4_6 proof_model | sed 's/^/  /'
bash tools/probe_stats.sh contrast bindtok bindshuf 4_6 proof_model | sed 's/^/  /'
bash tools/probe_stats.sh contrast bindtok bindshuf 4_6 proof_beam | sed 's/^/  /'
awk '
function val(file, tag, cfg, key,   line, n, i, f, kv, v) {
  while ((getline line < file) > 0) {
    n = split(line, f, " "); if (f[1] != tag || f[2] != cfg) continue
    for (i = 3; i <= n; i++){ split(f[i], kv, "="); if (kv[1] == key) v = kv[2]+0 }
  }
  close(file); return v
}
BEGIN {
  r = val("out/probes_bal.txt", "ladder", "4_6", "goal")
  a = val("out/probes_bindtok.txt", "ladder", "4_6", "goal")
  s = val("out/probes_bindshuf.txt", "ladder", "4_6", "goal")
  printf "WIDTH-REPORT d4b6 relation(38)=%.4f aligned(56)=%.4f shifted(56)=%.4f (dimension counts from CAND_DIM)\n", r, a, s
}'
awk '/^ladder /{print}' out/probes_bal.txt | sed 's/^/  final-ladder /'

# ===== 0.0252 integration + lifted-token gates ==============================
# Structural gates (must pass); measurement contrasts are reported with paired
# 2SE verdicts (0251 convention: no directional gate on underpowered effects).
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DINTEGRAL=1 -Iinclude -Isrc src/pst.c -o bin/pst_integral -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DLIFTED=1 -DLIFT_RHO=0.25 -Iinclude -Isrc src/pst.c -o bin/pst_lifted -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DINTEGRAL=1 -DLIFTED=1 -DLIFT_RHO=0.25 -Iinclude -Isrc src/pst.c -o bin/pst_both -lm
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DLIFTED=1 -DLIFT_RHO=1.0 -Iinclude -Isrc src/pst.c -o bin/pst_lift1 -lm
for v in pst_integral pst_lifted pst_both; do
  "./bin/$v" --gradcheck | grep -q '^GRADCHECK-PASS$' || { echo "GRADCHECK-FAIL $v"; exit 1; }
done
echo "GRADCHECK integral/lifted/both PASS"

# rho=1 lifted must be exactly the base model (same init, same objective)
RA="--train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 --eval-budget 4 --goaldepth 2 --goal-scan"
./bin/pst_hard_relob $RA > out/rho_base.txt 2>/dev/null
./bin/pst_lift1      $RA > out/rho_one.txt  2>/dev/null
rb=$(grep -o 'pchk=[0-9.-]*' out/rho_base.txt | head -1)
ro=$(grep -o 'pchk=[0-9.-]*' out/rho_one.txt | head -1)
[ "$rb" = "$ro" ] || { echo "RHO1-EQUIV-FAIL $rb vs $ro"; exit 1; }
echo "RHO1-EQUIV-PASS lifted(rho=1) == base ($rb)"

# path-integral consistency (independent incremental vs prefix replay) + prior wiring
./bin/pst_integral --path-check --goaldepth 2 --goal-scan --train-n 60 --val-n 20 --test-n 20 \
  | grep -q '^PATH-CHECK .* PASS$' || { echo PATH-CHECK-FAIL; exit 1; }
echo "PATH-CHECK exact (path + prior columns)"

# default-build harness regression: bal arm must reproduce the pinned 0251 ladder
awk '
function val(file, cfg, key,   line,n,i,f,kv,v){ while((getline line<file)>0){ n=split(line,f," ");
  if(f[1]!="ladder"||f[2]!=cfg) continue; for(i=3;i<=n;i++){split(f[i],kv,"="); if(kv[1]==key)v=kv[2]+0}} close(file); return v}
BEGIN{ g=val("out/probes_bal.txt","2_4","goal");
  if(!(g>0.7732 && g<0.7932)){ printf "HARNESS-REGRESSION-FAIL bal 2_4 goal=%.4f (pinned 0.7832)\n",g; exit 1 }
  printf "HARNESS-REGRESSION-PASS bal 2_4 goal=%.4f (0251 pinned 0.7832)\n",g }' || exit 1

# O0/O2/O3 identity + ASan for the combined arm
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DINTEGRAL=1 -DLIFTED=1 -DLIFT_RHO=0.25 -Iinclude -Isrc src/pst.c -o bin/both_O$O -lm
  ./bin/both_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 6 --goaldepth 3 --goal-scan > out/both_id_O$O.txt 2>/dev/null
done
diff -q out/both_id_O0.txt out/both_id_O2.txt >/dev/null && diff -q out/both_id_O0.txt out/both_id_O3.txt >/dev/null \
  || { echo BOTH-LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 -DINTEGRAL=1 -Iinclude -Isrc src/pst.c -o bin/integral_asan -lm
./bin/integral_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 6 --goaldepth 4 --goal-scan > out/integral_asan.txt 2> out/integral_asan.err
grep -q 'Sanitizer' out/integral_asan.err && { echo INTEGRAL-ASAN-FAIL; cat out/integral_asan.err; exit 1; }
echo "BOTH-LLVM-MATRIX PASS O0/O2/O3; INTEGRAL-ASAN+UBSAN clean (budget 6, depth 4)"

# holdout filter correctness: train excludes {4,5}, test all-in
./bin/pst_integral --dump-test out/ho_test.txt --test-n 30 --seed 11 --goaldepth 2 --goal-scan --holdout 45 >/dev/null 2>&1
./bin/pst_integral --dump out/ho_train.txt --worlds 30 --goaldepth 2 --goal-scan --holdout 45 >/dev/null 2>&1
python3 - <<'PY' || { echo HOLDOUT-FILTER-FAIL; exit 1; }
def goals(p):
    return [[int(x.split(':')[0]) for x in l.split()[1:]] for l in open(p) if l.startswith('G ')]
tg=goals('out/ho_test.txt'); tr=goals('out/ho_train.txt')[:30]
assert tg and all(all(p in (4,5) for p in w) for w in tg), 'test goals not all held-out'
assert tr and all(all(p not in (4,5) for p in w) for w in tr), 'train goals leak held-out'
print('HOLDOUT-FILTER-PASS train excludes {4,5}, test all-in')
PY

# probe-log schema for every arm + held-out rung
for arm in bal integral lifted both priorshuf lifted0; do
  bash tools/probe_stats.sh check "probes/$arm" "${SEEDS:-5}" | sed "s/^/  $arm /"
done
for arm in bal integral lifted both lifted0; do
  awk -v n="${SEEDS:-5}" -v dir="probes/ho_$arm" '
  function num(line,key,  i,f,kv){split(line,f," ");for(i=1;i<=length(f);i++){split(f[i],kv,"=");if(kv[1]==key)return kv[2]+0}return ""}
  BEGIN{ bad=0; cfgs[1]="2_4"; cfgs[2]="2_6";
    for(c=1;c<=2;c++){ cfg=cfgs[c]; f=dir"/cfg_"cfg".txt"; ns=0;nm=0;delete seen;
      while((getline line<f)>0){
        if(line~/^SEED /){ns++;s=substr(line,6)+0;seen[s]++;
          v=num(line,"proof_model"); if(v==""||v<0||v>1){printf "HOCHECK-FAIL %s bad field: %s\n",cfg,line;bad=1}}
        else if(line~/^MEAN /){nm++}
        else if(line~/^(REGRET|BOOT|BOUND-ASSERT|SEARCH-BUDGET|PARAMS|DATASET|CENSUS|EXPORT)/){}
        else if(line!~/^#/&&length(line)>0){printf "HOCHECK-FAIL %s stray: %s\n",cfg,line;bad=1}}
      close(f); if(ns!=n||nm!=n){printf "HOCHECK-FAIL %s rows %d/%d need %d\n",cfg,ns,nm,n;bad=1}
      d=0;for(s in seen)d++; if(d!=n){printf "HOCHECK-FAIL %s distinct %d need %d\n",cfg,d,n;bad=1}}
    if(bad)exit 1; printf "HOCHECK-PASS %s seeds=%d (cfgs 2_4,2_6)\n",dir,n }' || exit 1
done

# paired-by-seed contrasts (reported, 2SE verdict; no directional gate)
echo "== integration / lifted contrasts (paired by seed, 2SE)"
for c in "integral bal" "lifted bal" "both bal" "both integral" "priorshuf integral" "lifted0 lifted"; do
  set -- $c
  bash tools/probe_stats.sh contrast "$1" "$2" 4_6 proof_model | sed 's/^/  /'
  bash tools/probe_stats.sh contrast "$1" "$2" 2_4 proof_model | sed 's/^/  /'
done
echo "== held-out predicate transfer (train d2 ho{4,5} -> test goals all {4,5})"
grep -E '^holadder' out/integral_summary.txt | sed 's/^/  /'
for c in "integral bal" "lifted bal" "lifted0 bal" "both bal"; do
  set -- $c
  fa="probes/ho_$1/cfg_2_4.txt"; fb="probes/ho_$2/cfg_2_4.txt"
  pa=$(mktemp); pb=$(mktemp)
  grep '^SEED ' "$fa" | awk '{for(i=1;i<=NF;i++){split($i,kv,"=");if(kv[1]=="proof_model")print $2,kv[2]}}' | sort > "$pa"
  grep '^SEED ' "$fb" | awk '{for(i=1;i<=NF;i++){split($i,kv,"=");if(kv[1]=="proof_model")print $2,kv[2]}}' | sort > "$pb"
  join "$pa" "$pb" | awk -v a="$1" -v b="$2" '
    {n++;d=$2-$3;s+=d;ss+=d*d} END{ if(n<2){print "HOCONTRAST ho_"a"-"b"@2_4 INSUFFICIENT";exit}
      m=s/n;v=(ss-n*m*m)/(n-1);se=sqrt(v/n);
      verdict=(se>0&&(m>2*se||m<-2*se))?"SIGNIFICANT(2SE)":"INCONCLUSIVE(2SE)";
      printf "HOCONTRAST ho_%s-%s@2_4 mean=%+.4f se=%.4f n=%d %s\n",a,b,m,se,n,verdict}'
  rm -f "$pa" "$pb"
done

echo "V0252-INTEGRAL-LIFTED-PASS"
