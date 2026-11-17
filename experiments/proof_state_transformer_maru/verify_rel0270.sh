#!/usr/bin/env bash
# 0.0270 gates: relational fixture + typed structure (S1/S2) + controls.
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"
export PROBES=probes_r
export ARMS="S0 S0e S1 S2 S1shuf S0_focus S1_focus S1_assert S1_assert_rand S1_assert_union"

echo "== 1. gradient check (episode scalar = trained scalar; small dataset for speed)"
for f in "S0:" "S0e:-DENTFEAT=1" "S1:-DTYPED=1" "S2:-DTYPED=1 -DOBLREAD=1" "S1shuf:-DTYPED=1 -DTYPEDSHUF=1" "S1_assert:-DTYPED=1 -DASSERT=1 -DASSERTW=0.5" "S1_assert_rand:-DTYPED=1 -DASSERT=1 -DASSERTW=0" "S1_assert_union:-DTYPED=1 -DASSERT=1 -DASSERTW=0.5 -DASSERTUNION=1"; do
  n="${f%%:*}"; fl="${f#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DRELATOM=1 -DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -Iinclude -Isrc $fl src/pst.c -o "bin/gr_$n" -lm
  "./bin/gr_$n" --gradcheck --train-n 8 --val-n 4 --test-n 4 > "out/gr_$n.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gr_$n.txt" || { echo "REL-GRADCHECK-FAIL $n"; cat "out/gr_$n.txt"; exit 1; }
  case "$n" in S1|S2|S1shuf|S1_assert|S1_assert_rand)
    grep -q 'TYPED-GRAD .* OK' "out/gr_$n.txt" || { echo "TYPED-GRAD-FAIL $n"; exit 1; } ;;
  esac
  case "$n" in S1_assert|S1_assert_rand)
    grep -q 'ASSERT-GRAD .* OK' "out/gr_$n.txt" || { echo "ASSERT-GRAD-FAIL $n"; exit 1; } ;;
  esac
done
echo "REL-GRADCHECK-PASS (8 builds; typed + assert liveness asserted)"

echo "== 2. independent oracle parity (rules/features/utility/witness/DP labels)"
./bin/gr_S0 --dump-rules out/rel_rules.txt > /dev/null
./bin/gr_S0 --dump out/rel_worlds_gate.txt --worlds 30 --goal-scan --goaldepth 2 > /dev/null 2>&1
./bin/gr_S1 --dump-dp out/rel_dp_gate.txt --train-n 12 --val-n 4 --test-n 4 --goal-scan --goaldepth 2 --collect full > /dev/null 2>&1
python3 tools/check_parity_rel.py --rules out/rel_rules.txt --worlds out/rel_worlds_gate.txt --dp out/rel_dp_gate.txt \
  | tee out/parity_rel_gate.txt
grep -q '^PARITY-REL-PASS$' out/parity_rel_gate.txt || { echo PARITY-FAIL; exit 1; }

echo "== 3. fixture discriminative power: binding aliases at eval depth"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DRELATOM=1 -DVALMODE=1 -DLABEL_NCOST=1 -Iinclude -Isrc tools/alias_census.c -o bin/alias_census -lm
./bin/alias_census 4 2 2>/dev/null | tee out/alias_gate.txt
awk '/ALIAS-CENSUS/ { for(i=1;i<=NF;i++){ split($i,kv,"="); if(kv[1]=="top_mixed") tm=kv[2]+0 } }
     END { if (tm > 0) print "ALIAS-PASS top-mixed alias groups at depth 4:", tm;
           else { print "ALIAS-FAIL fixture has no feature-only decision limit"; exit 1 } }' out/alias_gate.txt

echo "== 4. permutation equivariance (candidates AND fact-token order)"
for a in S1 S2 S1shuf; do
  pm=$(grep -o 'perm_maxdiff=[0-9.e-]*' "probes_r/$a/cfg_4_4.txt" | head -1 | cut -d= -f2)
  awk -v v="$pm" 'BEGIN{ if (!(v+0 < 1e-9)) { printf "PERM-FAIL %s\n", v; exit 1 } }' || { echo "PERM-FAIL $a"; exit 1; }
done
echo "PERM-PASS"

echo "== 5. label-budget independence (typed arm, behavioural)"
CFG="--collect full --sample sub --train-n 40 --val-n 20 --test-n 20 --goal-scan --balance-reward"
for b in 4 6; do
  ./bin/gr_S1 --train --seeds 1 --seed-base 71 --epochs 2 $CFG --goaldepth 2 \
    --eval-budget $b --no-bound > "out/lr_$b.txt" 2>&1
done
p4=$(grep -o 'pchk=[0-9.]*' out/lr_4.txt | head -1)
p6=$(grep -o 'pchk=[0-9.]*' out/lr_6.txt | head -1)
[ -n "$p4" ] && [ "$p4" = "$p6" ] || { echo "LABEL-INDEPENDENT-FAIL $p4 vs $p6"; exit 1; }
echo "LABEL-INDEPENDENT-PASS ($p4)"

echo "== 6. header cross-loads"
ra="--train --seeds 1 --seed-base 71 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/gr_S0 $ra --load-weights probes_r/S1/w_71.bin --no-bound > out/hr_a.txt 2>&1; ea=$?
./bin/gr_S1 $ra --load-weights probes_r/S2/w_71.bin --no-bound > out/hr_b.txt 2>&1; eb=$?
./bin/gr_S0 $ra --load-weights probes_r/S0e/w_71.bin --no-bound > out/hr_c.txt 2>&1; ec=$?
./bin/gr_S1 $ra --load-weights probes_r/S1shuf/w_71.bin --no-bound > out/hr_d.txt 2>&1; ed=$?
./bin/gr_S2 $ra --load-weights probes_r/S2/w_71.bin --no-bound > out/hr_e.txt 2>&1; ee=$?
./bin/gr_S1 $ra --load-weights probes_r/S1_assert/w_71.bin --no-bound > out/hr_f.txt 2>&1; ef=$?
./bin/gr_S1_assert_rand $ra --load-weights probes_r/S1_assert/w_71.bin --no-bound > out/hr_g.txt 2>&1; eg=$?
set -e
[ "$ea" -eq 4 ] || { echo "HEADER-FAIL typed->untyped (exit $ea)"; exit 1; }
[ "$eb" -eq 4 ] || { echo "HEADER-FAIL oblread mismatch (exit $eb)"; exit 1; }
[ "$ec" -eq 4 ] || { echo "HEADER-FAIL entfeat mismatch (exit $ec)"; exit 1; }
[ "$ed" -eq 4 ] || { echo "HEADER-FAIL typedshuf mismatch (exit $ed)"; exit 1; }
[ "$ee" -eq 0 ] || { echo "HEADER-FAIL own weights (exit $ee)"; exit 1; }
[ "$ef" -eq 4 ] || { echo "HEADER-FAIL assert mismatch (exit $ef)"; exit 1; }
[ "$eg" -eq 4 ] || { echo "HEADER-FAIL assertw mismatch (exit $eg)"; exit 1; }
echo "HEADER-PASS"

echo "== 7. contrasts (pre-registered: S1/S2 may beat S0 ONLY if binding info matters)"
bash tools/hybrid_stats.sh contrast S1 S0 goal | tee out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S2 S1 goal | tee -a out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S0e S0 goal | tee -a out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S1 S1shuf goal | tee -a out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S2 S0 goal | tee -a out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S1_assert S1_focus goal | tee -a out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S1_assert S1_assert_rand goal | tee -a out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S1_assert S1 goal | tee -a out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S1_assert_union S1_focus goal | tee -a out/rel_contrast.txt
bash tools/hybrid_stats.sh contrast S1_assert_union S1 goal | tee -a out/rel_contrast.txt
echo "CONTRASTS-REPORTED (directions are findings, not gate requirements)"

echo "== 8. ceilings: no-contract exhaustive (branch 24 = POOL), per-seed, all arms below"
python3 - <<'PY' || { echo CEILING-FAIL; exit 1; }
import glob, re, statistics as st
ceil = {}
for f in glob.glob('probes_r/ceiling/seed_*.txt'):
    seed = int(re.search(r'seed_(\d+)', f).group(1))
    for line in open(f):
        if line.startswith('DFS'):
            kv = dict(x.split('=') for x in line.split()[1:] if '=' in x)
            assert int(kv['branch']) >= 24, 'no-contract exhaustive needs branch >= POOL'
            ceil[seed] = float(kv['goal'])
assert ceil, 'no ceiling artefacts'
arms = ['S0','S0e','S1','S2','S1shuf','S0_focus','S1_focus','S1_assert','S1_assert_rand','S1_assert_union']
seen = set()
for a in arms:
    for line in open(f'probes_r/{a}/cfg_4_4.txt'):
        if line.startswith('DFS'):
            kv = dict(x.split('=') for x in line.split()[1:] if '=' in x)
            s = int(kv['seed']); seen.add(s)
            assert float(kv['goal']) <= ceil[s] + 1e-9, f'{a} seed {s} exceeds exhaustive ceiling'
assert seen == set(ceil), 'seed set mismatch'
print(f"CEILING-PASS mean={st.mean(ceil.values()):.4f} {sorted(round(v,4) for v in ceil.values())}; all arms below per-seed exhaustive")
PY

echo "== 9. FOCUS re-measurement (vacuous on unary at d4/b4; binding-sensitive here?)"
for a in S0_focus S1_focus; do
  fr=$(awk '/^HYBRID/ { for(i=1;i<=NF;i++){ split($i,kv,"="); if(kv[1]=="focus_removed") s+=kv[2] } } END{ print s+0 }' "probes_r/$a/cfg_4_4.txt")
  fs=$(awk '/^HYBRID/ { for(i=1;i<=NF;i++){ split($i,kv,"="); if(kv[1]=="focus_states") s+=kv[2] } } END{ print s+0 }' "probes_r/$a/cfg_4_4.txt")
  echo "FOCUS $a states=$fs removed=$fr"
done

echo "== 9b. assert invention: kernel-judged adoption learning curve"
a0=$(grep 'ASSERT-TRAIN' probes_r/S1_assert/train_71.log | head -1 | grep -o 'top1_adopt=[0-9.]*' | cut -d= -f2)
a1=$(grep 'ASSERT-TRAIN' probes_r/S1_assert/train_71.log | tail -1 | grep -o 'top1_adopt=[0-9.]*' | cut -d= -f2)
awk -v x="$a0" -v y="$a1" 'BEGIN{ if (!(y > x + 0.1)) { printf "ASSERT-LEARN-FAIL %s -> %s\n", x, y; exit 1 } }' \
  || { echo ASSERT-LEARN-FAIL; exit 1; }
echo "ASSERT-LEARN-PASS (top-1 kernel adoption $a0 -> $a1; chance ~0.07)"
for a in S1_assert S1_assert_rand; do
  awk '/^ASSERT / { for(i=1;i<=NF;i++){ split($i,kv,"="); if(kv[1]=="adopt") ad+=kv[2]; if(kv[1]=="states") st+=kv[2]; if(kv[1]=="fallback") fb+=kv[2] } }
       END{ printf "ASSERT-EVAL %s states=%d adopt=%d fallback=%d rate=%.4f\n", "'$a'", st, ad, fb, st?ad/st:0 }' probes_r/$a/cfg_4_4.txt
done

echo "== documentation hygiene"
bash tools/doc_check.sh ../../docs/release-0270.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 10. aggregation + mutation regression"
bash tools/hybrid_stats.sh verify out/rel0270.txt "$SEEDS"
bash gate_regression_hybrid.sh out/rel0270.txt probes_r "$SEEDS"

echo "== 11. LLVM identity + sanitizers (S2 arm)"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DRELATOM=1 -DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 \
    -DTYPED=1 -DOBLREAD=1 -Iinclude -Isrc src/pst.c -o bin/r_O$O -lm
  ./bin/r_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 5 > out/r_id_O$O.txt 2>&1
done
diff -q out/r_id_O0.txt out/r_id_O2.txt >/dev/null && diff -q out/r_id_O0.txt out/r_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 -DRELATOM=1 \
  -DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DTYPED=1 -DOBLREAD=1 -Iinclude -Isrc src/pst.c -o bin/r_asan -lm
./bin/r_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 5 > out/r_asan.txt 2> out/r_asan.err
grep -q 'Sanitizer' out/r_asan.err && { echo ASAN-FAIL; cat out/r_asan.err; exit 1; }
echo "LLVM-PASS"

echo "== 12. unary regression (default build unaffected)"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -Iinclude -Isrc src/pst.c -o bin/r_unary -lm
./bin/r_unary --gradcheck > out/r_unary_gc.txt 2>&1
grep -q '^GRADCHECK-PASS$' out/r_unary_gc.txt || { echo UNARY-REGRESSION-FAIL; exit 1; }
echo "UNARY-REGRESSION-PASS"

echo "== 13. 15-seed confirmation table == recomputation"
python3 - <<'PY' || { echo CONFIRM-TABLE-FAIL; exit 1; }
import re, statistics as st
def rows(a):
    d={}
    for f in [f"probes_r/{a}/cfg_4_4.txt", f"probes_r/{a}/cfg_ext.txt"]:
        try: fh=open(f)
        except FileNotFoundError: continue
        for l in fh:
            if l.startswith("DFS"):
                kv=dict(x.split('=') for x in l.split()[1:] if '=' in x)
                d[int(kv['seed'])]=float(kv['goal'])
    return d
arms=["S0","S0e","S1","S1shuf","S0_focus","S1_focus","S1_assert","S1_assert_rand","S1_assert_union"]
R={a:rows(a) for a in arms}
shipped={}
for l in open('out/confirm0270.txt'):
    f=l.split()
    if f and f[0]=='MEAN15': shipped[f[1]]=float(f[2].split('=')[1])
for a in arms:
    assert len(R[a])==15, f'{a}: need 15 seeds, got {len(R[a])}'
    m=st.mean(R[a].values())
    assert abs(m-shipped[a])<6e-5, f'{a}: shipped {shipped[a]} != recomputed {m:.4f}'
print(f'CONFIRM-TABLE-PASS 15-seed means == per-seed recomputation ({len(arms)} arms)')
PY
echo "V0270-RELATIONAL-PASS"