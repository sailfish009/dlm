#!/usr/bin/env bash
# 0.0268 gates (audit F1/F2/F3/F6 + the missing controls).
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"
export PROBES=probes_x
export ARMS="A_nocost A_b5 A_b6 B_pair16 C_pair64 D_pair16_b5 E_pair16_e6 F_pair16_intg G_pair16_lift H_pair16_focus"
row () { awk -v a="$1" -v k="$2" '$1=="ARM" && $2==a{ for(i=3;i<=NF;i++){ split($i,kv,"="); if(kv[1]==k) print kv[2] } }' out/recomb0268.txt; }

echo "== 1. gradient check, ten configurations"
for f in "A_nocost:-DVALMODE=1 -DLABEL_NCOST=1" \
         "A_b5:-DVALMODE=1 -DLABEL_NCOST=1" \
         "B_pair16:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1" \
         "D_pair16_b5:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1" \
         "E_pair16_e6:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1" \
         "F_pair16_intg:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -DINTEGRAL=1" \
         "G_pair16_lift:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -DLIFTED=1 -DLIFT_RHO=0.25" \
         "H_pair16_focus:-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -DFOCUS=1"; do
  n="${f%%:*}"; fl="${f#*:}"
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $fl src/pst.c -o "bin/gcy_$n" -lm
  "./bin/gcy_$n" --gradcheck > "out/gcy_$n.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/gcy_$n.txt" || { echo "RECOMB-GRADCHECK-FAIL $n"; exit 1; }
done
echo "RECOMB-GRADCHECK-PASS"

echo "== 2. F1: labels and weights independent of the evaluation budget (behavioural)"
CFG="--collect full --sample sub --train-n 40 --val-n 20 --test-n 20 --goal-scan --balance-reward"
for b in 4 6; do
  ./bin/gcy_A_nocost --train --seeds 1 --seed-base 71 --epochs 2 $CFG --goaldepth 2 \
    --eval-budget $b --no-bound > "out/f1_$b.txt" 2>&1
done
p4=$(grep -o 'pchk=[0-9.]*' out/f1_4.txt | head -1)
p6=$(grep -o 'pchk=[0-9.]*' out/f1_6.txt | head -1)
c4=$(grep 'split=train' out/f1_4.txt | head -1 | grep -o 'mean_top=[0-9.]*')$(grep 'split=train' out/f1_4.txt | head -1 | grep -o 'top_share=[0-9.]*')
c6=$(grep 'split=train' out/f1_6.txt | head -1 | grep -o 'mean_top=[0-9.]*')$(grep 'split=train' out/f1_6.txt | head -1 | grep -o 'top_share=[0-9.]*')
[ -n "$p4" ] && [ "$p4" = "$p6" ] || { echo "LABEL-INDEPENDENT-FAIL pchk $p4 vs $p6"; exit 1; }
[ -n "$c4" ] && [ "$c4" = "$c6" ] || { echo "LABEL-INDEPENDENT-FAIL census $c4 vs $c6"; exit 1; }
echo "LABEL-INDEPENDENT-PASS ($p4, $c4 at both budgets)"

echo "== 3. F2: label flags in the weight header"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -Iinclude -Isrc src/pst.c -o bin/gcy_cost -lm   # LABEL_NCOST=0
ra="--train --seeds 1 --seed-base 71 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/gcy_cost $ra --load-weights probes_x/A_nocost/w_71.bin --no-bound > out/hh_a.txt 2>&1; ea=$?
./bin/gcy_A_nocost $ra --label-rem 3 --load-weights probes_x/A_nocost/w_71.bin --no-bound > out/hh_b.txt 2>&1; eb=$?
./bin/gcy_A_nocost $ra --load-weights probes_x/A_nocost/w_71.bin --no-bound > out/hh_c.txt 2>&1; ec=$?
set -e
[ "$ea" -eq 4 ] || { echo "HEADER-LABELFLAGS-FAIL ncost mismatch not refused (exit $ea)"; exit 1; }
[ "$eb" -eq 4 ] || { echo "HEADER-LABELFLAGS-FAIL label_rem mismatch not refused (exit $eb)"; exit 1; }
[ "$ec" -eq 0 ] || { echo "HEADER-LABELFLAGS-FAIL own weights rejected (exit $ec)"; exit 1; }
echo "HEADER-LABELFLAGS-PASS (ncost and label_rem cross-loads refused)"

echo "== 4. budget ladder + guard exit code (F6)"
CFG8="--collect full --sample sub --train-n 8 --val-n 4 --test-n 4 --goal-scan --balance-reward"
for b in 4 5 6; do
  t0=$(date +%s%N)
  ./bin/gcy_A_nocost --train --seeds 1 --seed-base 71 --epochs 1 $CFG8 --goaldepth 4 \
    --eval-budget $b --dfs --branch 3 --subsume 1 --prop 1 --no-bound > "out/y_ladder_$b.txt" 2>&1
  t1=$(date +%s%N); ms=$(( (t1-t0)/1000000 ))
  [ "$ms" -lt 30000 ] || { echo "BUDGET-LADDER-FAIL budget $b took ${ms}ms"; exit 1; }
  printf "  budget %s: %s ms\n" "$b" "$ms"
done
set +e
./bin/gcy_A_nocost --train --seeds 1 --train-n 4 --goal-scan --eval-budget 9 > out/y_guard.txt 2>&1; ge=$?
set -e
[ "$ge" -eq 2 ] || { echo "BUDGET-GUARD-FAIL expected exit 2, got $ge"; exit 1; }
grep -q 'EVAL-BUDGET-FAIL' out/y_guard.txt || { echo "BUDGET-GUARD-FAIL missing message"; exit 1; }
echo "BUDGET-LADDER-PASS; BUDGET-GUARD-PASS (exit 2)"

echo "== 5. F3: per-seed ceiling recomputed from artefacts"
python3 - <<'PY' || { echo CEILING-FAIL; exit 1; }
import glob, re, statistics as st, sys
ceil = {}
for f in glob.glob('probes_x/ceiling/seed_*.txt'):
    seed = int(re.search(r'seed_(\d+)', f).group(1))
    for line in open(f):
        if line.startswith('DFS'):
            kv = dict(x.split('=') for x in line.split()[1:] if '=' in x)
            ceil[seed] = float(kv['goal'])
assert ceil, 'no ceiling artefacts'
mean = st.mean(ceil.values())
best = {}
for line in open('out/recomb0268.txt'):
    if line.startswith('ARM'):
        f = line.split(); name = f[1]
        kv = dict(x.split('=') for x in f[2:] if '=' in x)
        best[name] = float(kv['dfs'])
d = best['D_pair16_b5']
for s, c in ceil.items():
    assert d <= c + 1e-9, f'D {d} exceeds ceiling {c} on seed {s}'
print(f"CEILING-PASS per-seed ceilings {sorted(round(v,4) for v in ceil.values())} mean={mean:.4f}; "
      f"D={d:.4f} = {100*d/mean:.1f}% of mean, below every seed ceiling")
PY

echo "== 6. claims, incl. the node-matched control"
bash tools/hybrid_stats.sh contrast B_pair16 A_nocost goal | tee out/y_contrast.txt
bash tools/hybrid_stats.sh contrast A_b5 A_nocost goal | tee -a out/y_contrast.txt
bash tools/hybrid_stats.sh contrast D_pair16_b5 A_b5 goal | tee -a out/y_contrast.txt
bash tools/hybrid_stats.sh contrast E_pair16_e6 A_b6 goal | tee -a out/y_contrast.txt
bash tools/hybrid_stats.sh contrast C_pair64 B_pair16 goal | tee -a out/y_contrast.txt
awk '
/B_pair16-A_nocost goal/ && /SIGNIFICANT/ { b=1 }
/A_b5-A_nocost goal/ && /SIGNIFICANT/ { w=1 }
/D_pair16_b5-A_b5 goal/ && /SIGNIFICANT/ { d=1 }
/E_pair16_e6-A_b6 goal/ { for (i=1;i<=NF;i++){ split($i,kv,"="); if(kv[1]=="mean") mm=kv[2]+0 } if (mm < 0.02) e=1 }
END{ if (b && w && d && e) print "CLAIMS-PASS contracts at matched nodes, branch width, budget dependence all as stated"
     else { print "CLAIMS-FAIL a stated contrast changed direction or significance"; exit 1 } }' out/y_contrast.txt
na=$(row A_b5 nodes); nd=$(row D_pair16_b5 nodes)
awk -v a="$na" -v d="$nd" 'BEGIN{ if (!(d <= a*1.05)) { printf "CLAIMS-FAIL D nodes %s not matched to A_b5 %s\n", d, a; exit 1 }
  printf "CLAIMS-NODEMATCH D=%s <= A_b5=%s (contract gain is node-matched)\n", d, a }'
grep -q 'node-matched' ../../docs/release-0268.md || { echo "CLAIMS-FAIL note lacks the node-matched statement"; exit 1; }

echo "== documentation hygiene"
bash tools/doc_check.sh ../../docs/release-0268.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 7. aggregation + mutation regression"
bash tools/hybrid_stats.sh verify out/recomb0268.txt "$SEEDS"
bash gate_regression_hybrid.sh out/recomb0268.txt probes_x "$SEEDS"

echo "== 8. LLVM identity + sanitizers (best arm)"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 \
    -Iinclude -Isrc src/pst.c -o bin/y_O$O -lm
  ./bin/y_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 4 --goaldepth 3 --goal-scan --dfs --branch 5 > out/y_id_O$O.txt 2>&1
done
diff -q out/y_id_O0.txt out/y_id_O2.txt >/dev/null && diff -q out/y_id_O0.txt out/y_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1 -Iinclude -Isrc src/pst.c -o bin/y_asan -lm
./bin/y_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 4 --goaldepth 4 --goal-scan --dfs --branch 5 > out/y_asan.txt 2> out/y_asan.err
grep -q 'Sanitizer' out/y_asan.err && { echo ASAN-FAIL; cat out/y_asan.err; exit 1; }
echo "LLVM-PASS"
echo "V0268-RECOMB-PASS"
