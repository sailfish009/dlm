#!/usr/bin/env bash
# 0.0269 gates: loop cell (BPTT) + controls + the 0268-review fixes.
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"
export PROBES=probes_y
export ARMS="A_nocost B_pair16 D_pair16_b5 D_rem D_cell D_cellpred D_detach D_shuf D_remcell D_wide"

echo "== 1. gradient check, ten configurations (episode scalar = trained scalar)"
for f in "A_nocost:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1" \
         "B_pair16:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1" \
         "D_pair16_b5:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1" \
         "D_rem:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 -DREMFEAT=1" \
         "D_cell:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 -DLOOPCELL=1" \
         "D_cellpred:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 -DLOOPCELL=1 -DPREDW=0.5" \
         "D_detach:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 -DLOOPCELL=1 -DCELLDETACH=1" \
         "D_shuf:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 -DLOOPCELL=1 -DCELLSHUF=1" \
         "D_remcell:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 -DLOOPCELL=1 -DREMFEAT=1" \
         "D_wide:-DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 -DMNL=3"; do
  n="${f%%:*}"; fl="${f#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $fl src/pst.c -o "bin/gc9_$n" -lm
  "./bin/gc9_$n" --gradcheck > "out/gc9_$n.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gc9_$n.txt" || { echo "LOOP-GRADCHECK-FAIL $n"; cat "out/gc9_$n.txt"; exit 1; }
  case "$n" in
    D_cell|D_cellpred|D_shuf|D_remcell)
      grep -q 'CELL-GRAD .* detach=0 OK' "out/gc9_$n.txt" || { echo "CELL-GRAD-FAIL $n (dead recurrence)"; exit 1; } ;;
    D_detach)
      grep -q 'CELL-GRAD .* detach=1 OK' "out/gc9_$n.txt" || { echo "CELL-GRAD-FAIL $n (detach must have zero cell grad)"; exit 1; } ;;
  esac
done
echo "LOOP-GRADCHECK-PASS (10 configs; BPTT liveness asserted)"

echo "== 2. label-budget independence (0268 F1 regression, behavioural)"
CFG="--collect full --sample sub --train-n 40 --val-n 20 --test-n 20 --goal-scan --balance-reward"
for b in 4 6; do
  ./bin/gc9_D_cell --train --seeds 1 --seed-base 71 --epochs 2 $CFG --goaldepth 2 \
    --eval-budget $b --no-bound > "out/l9_$b.txt" 2>&1
done
p4=$(grep -o 'pchk=[0-9.]*' out/l9_4.txt | head -1)
p6=$(grep -o 'pchk=[0-9.]*' out/l9_6.txt | head -1)
[ -n "$p4" ] && [ "$p4" = "$p6" ] || { echo "LABEL-INDEPENDENT-FAIL pchk $p4 vs $p6"; exit 1; }
echo "LABEL-INDEPENDENT-PASS ($p4 at budgets 4 and 6, cell arm)"

echo "== 3. header: cell/remfeat/eptrain/predw cross-loads refused"
ra="--train --seeds 1 --seed-base 71 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/gc9_D_pair16_b5 $ra --load-weights probes_y/D_cell/w_71.bin --no-bound > out/h9_a.txt 2>&1; ea=$?
./bin/gc9_D_pair16_b5 $ra --load-weights probes_y/D_rem/w_71.bin --no-bound > out/h9_b.txt 2>&1; eb=$?
./bin/gc9_D_cell $ra --load-weights probes_y/D_cellpred/w_71.bin --no-bound > out/h9_c.txt 2>&1; ec=$?
./bin/gc9_B_pair16 $ra --load-weights probes_y/B_pair16/w_71.bin --no-bound > out/h9_d.txt 2>&1; ed=$?
./bin/gc9_D_cell $ra --load-weights probes_y/D_cell/w_71.bin --no-bound > out/h9_e.txt 2>&1; ee=$?
set -e
[ "$ea" -eq 4 ] || { echo "HEADER-CELL-FAIL cell->nocell not refused (exit $ea)"; exit 1; }
[ "$eb" -eq 4 ] || { echo "HEADER-CELL-FAIL remfeat mismatch not refused (exit $eb)"; exit 1; }
[ "$ec" -eq 4 ] || { echo "HEADER-CELL-FAIL predw mismatch not refused (exit $ec)"; exit 1; }
[ "$ed" -eq 0 ] || { echo "HEADER-CELL-FAIL own weights rejected (exit $ed)"; exit 1; }
[ "$ee" -eq 0 ] || { echo "HEADER-CELL-FAIL own cell weights rejected (exit $ee)"; exit 1; }
echo "HEADER-CELL-PASS"

echo "== 4. episode permutation equivariance (cell arms)"
for a in D_cell D_cellpred D_shuf; do
  pm=$(grep -o 'perm_maxdiff=[0-9.e-]*' "probes_y/$a/cfg_4_4.txt" | head -1 | cut -d= -f2)
  awk -v v="$pm" 'BEGIN{ if (!(v+0 < 1e-9)) { printf "PERM-FAIL %s\n", v; exit 1 } }' || { echo "PERM-FAIL $a"; exit 1; }
done
echo "PERM-PASS (episode-level, cell arms)"

echo "== 5. world-model learning curve (directional, train split)"
m0=$(grep 'PRED-TRAIN ep=0 ' probes_y/D_cellpred/train_71.log | grep -o 'mse=[0-9.]*' | cut -d= -f2)
m1=$(grep 'PRED-TRAIN ep=39 ' probes_y/D_cellpred/train_71.log | grep -o 'mse=[0-9.]*' | cut -d= -f2)
awk -v a="$m0" -v b="$m1" 'BEGIN{ if (!(a > 5*b)) { printf "PRED-LEARN-FAIL %s -> %s\n", a, b; exit 1 } }' \
  || { echo "PRED-LEARN-FAIL"; exit 1; }
grep -h 'LOOPCELL-VAL' probes_y/D_cellpred/train_71.log
echo "PRED-LEARN-PASS (train mse $m0 -> $m1; val-vs-constant reported above, fixture targets near-constant)"

echo "== 6. claims (recomb core under the new protocol + cell contrasts)"
bash tools/hybrid_stats.sh contrast B_pair16 A_nocost goal | tee out/l9_contrast.txt
bash tools/hybrid_stats.sh contrast D_pair16_b5 B_pair16 goal | tee -a out/l9_contrast.txt
bash tools/hybrid_stats.sh contrast D_cell D_detach goal | tee -a out/l9_contrast.txt
bash tools/hybrid_stats.sh contrast D_cell D_shuf goal | tee -a out/l9_contrast.txt
bash tools/hybrid_stats.sh contrast D_rem D_pair16_b5 goal | tee -a out/l9_contrast.txt
bash tools/hybrid_stats.sh contrast D_cellpred D_cell goal | tee -a out/l9_contrast.txt
bash tools/hybrid_stats.sh contrast D_cell D_remcell goal | tee -a out/l9_contrast.txt
bash tools/hybrid_stats.sh contrast D_cellpred D_detachpred goal | tee -a out/l9_contrast.txt
awk '
/B_pair16-A_nocost goal/ && /SIGNIFICANT/ { b=1 }
/D_pair16_b5-B_pair16 goal/ && /SIGNIFICANT/ { d=1 }
END{ if (b && d) print "LOOP-CLAIMS-PASS recomb core survives the episode protocol"
     else { print "LOOP-CLAIMS-FAIL core contrasts lost significance"; exit 1 } }' out/l9_contrast.txt

echo "== 7. ceilings: per-arm per-seed (own mined contracts), branch 64, seed sets match"
python3 - <<'PY' || { echo CEILING-FAIL; exit 1; }
import glob, re, statistics as st
# B ceiling (cross-version reference)
ceil = {}
for f in glob.glob('probes_y/ceiling/seed_*.txt'):
    seed = int(re.search(r'seed_(\d+)', f).group(1))
    for line in open(f):
        if line.startswith('DFS'):
            kv = dict(x.split('=') for x in line.split()[1:] if '=' in x)
            assert int(kv['branch']) >= 40, 'ceiling branch must cover POOL+pair_keep'
            ceil[seed] = float(kv['goal'])
assert ceil, 'no B ceiling artefacts'
arms = ['D_pair16_b5','D_cell','D_cellpred','D_detach','D_shuf','D_rem','D_remcell','D_wide']
for a in arms:
    ac = {}
    for f in glob.glob(f'probes_y/ceiling/{a}_seed_*.txt'):
        seed = int(re.search(r'seed_(\d+)', f).group(1))
        for line in open(f):
            if line.startswith('DFS'):
                kv = dict(x.split('=') for x in line.split()[1:] if '=' in x)
                assert int(kv['branch']) >= 40
                ac[seed] = float(kv['goal'])
    assert set(ac) == set(ceil), f'{a}: ceiling seed set mismatch'
    seen = set()
    for line in open(f'probes_y/{a}/cfg_4_4.txt'):
        if line.startswith('DFS'):
            kv = dict(x.split('=') for x in line.split()[1:] if '=' in x)
            s = int(kv['seed']); seen.add(s)
            if s in ac:
                assert float(kv['goal']) <= ac[s] + 1e-9, f'{a} seed {s} exceeds its OWN ceiling'
    assert seen >= set(ceil), f'{a}: arm seeds missing from ceiling set'
    print(f"CEILING-ARM {a} own-mean={st.mean(ac.values()):.4f}")
print(f"CEILING-PASS B mean={st.mean(ceil.values()):.4f} {sorted(round(v,4) for v in ceil.values())}; "
      f"every branch-5 arm below its own per-seed ceiling; seed sets match")
PY

echo "== documentation hygiene"
bash tools/doc_check.sh ../../docs/release-0269.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 8. aggregation + mutation regression"
bash tools/hybrid_stats.sh verify out/loop0269.txt "$SEEDS"
bash gate_regression_hybrid.sh out/loop0269.txt probes_y "$SEEDS"

echo "== 9. LLVM identity + sanitizers (cellpred arm, BPTT stack)"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 \
    -DLOOPCELL=1 -DPREDW=0.5 -Iinclude -Isrc src/pst.c -o bin/y9_O$O -lm
  ./bin/y9_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 5 > out/y9_id_O$O.txt 2>&1
done
diff -q out/y9_id_O0.txt out/y9_id_O2.txt >/dev/null && diff -q out/y9_id_O0.txt out/y9_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 -DLOOPCELL=1 -DPREDW=0.5 \
  -Iinclude -Isrc src/pst.c -o bin/y9_asan -lm
./bin/y9_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 5 > out/y9_asan.txt 2> out/y9_asan.err
grep -q 'Sanitizer' out/y9_asan.err && { echo ASAN-FAIL; cat out/y9_asan.err; exit 1; }
echo "LLVM-PASS"

echo "== 10. 15-seed confirmation table == recomputation"
python3 - <<'PY' || { echo CONFIRM-TABLE-FAIL; exit 1; }
import re, statistics as st
def rows(a):
    d={}
    for f in [f"probes_y/{a}/cfg_4_4.txt", f"probes_y/{a}/cfg_ext.txt"]:
        try: fh=open(f)
        except FileNotFoundError: continue
        for l in fh:
            if l.startswith("DFS"):
                kv=dict(x.split('=') for x in l.split()[1:] if '=' in x)
                d[int(kv['seed'])]=float(kv['goal'])
    return d
arms=["D_pair16_b5","D_rem","D_cell","D_cellpred","D_detach","D_shuf","D_detachpred"]
R={a:rows(a) for a in arms}
shipped={}
for l in open('out/confirm0269.txt'):
    f=l.split()
    if f and f[0]=='MEAN15': shipped[f[1]]=float(f[2].split('=')[1])
for a in arms:
    assert len(R[a])==15, f'{a}: need 15 seeds, got {len(R[a])}'
    m=st.mean(R[a].values())
    assert abs(m-shipped[a])<6e-5, f'{a}: shipped {shipped[a]} != recomputed {m:.4f}'
print(f'CONFIRM-TABLE-PASS 15-seed means == per-seed recomputation ({len(arms)} arms)')
PY
echo "V0269-LOOPCELL-PASS"