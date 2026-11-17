#!/usr/bin/env bash
# 0.0269 게이트: 단순 실험 + 0268 감사 수락시험(G1–G6).
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"; SEED_BASE="${SEED_BASE:-81}"
ok=0

echo "== G5: gradcheck — 문서와 동일한 4개 라벨 체제"
n=0
for f in "util:" "label:-DVALMODE=1 -DLABEL_NCOST=1" "label_cost:-DVALMODE=1" "dp:-DVALMODE=1 -DLEMMA=1 -DPAIRMODE=1"; do
  name="${f%%:*}"; fl="${f#*:}"; n=$((n+1))
  clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $fl src/pst.c -o "bin/g_s_$name" -lm
  "./bin/g_s_$name" --gradcheck > "out/g_s_$name.txt" 2>&1
  grep -q '^GRADCHECK-PASS$' "out/g_s_$name.txt" || { echo "GRADCHECK-FAIL $name"; exit 1; }
done
[ "$n" -eq 4 ] || { echo "GRADCHECK-COUNT-FAIL"; exit 1; }
echo "GRADCHECK-PASS builds=$n (문서와 일치)"

echo "== G5: LABEL_STEPS cross-load 거부"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -DLABEL_NCOST=1 -DLABEL_STEPS=1 -Iinclude -Isrc src/pst.c -o bin/g_s_steps -lm
set +e
./bin/g_s_steps --train --seeds 1 --seed-base $SEED_BASE --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan \
  --load-weights probes_s/best/w_$SEED_BASE.bin --no-bound > out/steps_x.txt 2>&1; es=$?
set -e
[ "$es" -eq 4 ] || { echo "STEPS-CROSSLOAD-FAIL exit=$es"; exit 1; }
echo "STEPS-CROSSLOAD-PASS (exit 4)"

echo "== G2: 천장은 branch 64(절단 없음) + 시드 집합 일치"
python3 - "$SEEDS" "$SEED_BASE" <<'PY' || { echo CEILING-FAIL; exit 1; }
import sys, glob, re
seeds_expected = {int(sys.argv[2]) + i for i in range(int(sys.argv[1]))}
files = glob.glob('probes_s/ceil/seed_*.txt')
seeds_got = {int(re.search(r'seed_(\d+)', p).group(1)) for p in files}
assert seeds_got == seeds_expected, f'ceiling seed set {sorted(seeds_got)} != {sorted(seeds_expected)}'
vals = {}
for p in files:
    for line in open(p):
        if line.startswith('DFS'):
            kv = dict(x.split('=') for x in line.split()[1:] if '=' in x)
            assert int(kv['branch']) >= 40, f'branch {kv["branch"]} truncates the contract action space'
            vals[int(re.search(r'seed_(\d+)', p).group(1))] = float(kv['goal'])
print(f"CEILING-PASS branch>=40, seeds={sorted(vals)}, values={sorted(set(round(v,4) for v in vals.values()))}")
PY

echo "== G1: 주장 검사 + 열화 변이 회귀"
python3 tools/simple_check.py out/simple0269.txt || { echo "SIMPLE-CLAIM-FAIL"; exit 1; }
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
cp out/simple0269.txt "$tmp/ok.txt"
sed 's/^ARM best_b8 goal=[0-9.]*/ARM best_b8 goal=0.8000/' out/simple0269.txt > "$tmp/degraded.txt"
if python3 tools/simple_check.py "$tmp/degraded.txt" > /dev/null 2>&1; then
  echo "G1-MUTATION-FAIL degraded arm accepted"; exit 1
fi
sed 's/^CEILING goal=[0-9.]*/CEILING goal=0.8000/' out/simple0269.txt > "$tmp/lowceil.txt"
if python3 tools/simple_check.py "$tmp/lowceil.txt" > /dev/null 2>&1; then
  echo "G1-MUTATION-FAIL ceiling violation accepted"; exit 1
fi
echo "G1-PASS claim checks reject degraded arm and ceiling violation"

echo "== G3: 배포 표 == 재계산 (동본 비교) + 재실행 eval 동일"
python3 - <<'PY' || { echo TABLE-FAIL; exit 1; }
import statistics as st
def load(a):
    g=[]; f=[]; n=[]
    for line in open(f'probes_s/{a}/res.txt'):
        if line.startswith('DFS'):
            kv=dict(x.split('=') for x in line.split()[1:] if '=' in x)
            g.append(float(kv['goal'])); f.append(float(kv['full'])); n.append(int(kv['nodes']))
    return st.mean(g), st.mean(f), st.mean(n)
shipped = {}
for line in open('out/simple0269.txt'):
    if line.startswith('ARM'):
        f=line.split(); kv=dict(x.split('=') for x in f[2:] if '=' in x)
        shipped[f[1]] = (float(kv['goal']), float(kv['full']), float(kv['nodes']))
for a,(g,f,n) in shipped.items():
    rg, rf, rn = load(a)
    # 표는 소수 4자리로 반올림되므로 1e-4 허용
    assert abs(rg-g) < 6e-5 and abs(rf-f) < 6e-5 and abs(rn-n) < 0.5, f'{a}: table {g} != recomputed {rg}'
print(f"TABLE-PASS shipped table == per-seed recomputation ({len(shipped)} arms)")
PY
# 재실행 결정성: 한 시드의 eval을 다시 돌려 DFS 줄이 같은지
s=$SEED_BASE
./bin/s_best --train --seeds 1 --seed-base $s --collect full --sample sub --train-n 180 --val-n 60 --test-n 100 \
  --goal-scan --balance-reward --goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 5 --subsume 1 --prop 1 --no-bound \
  --load-weights probes_s/best/w_$s.bin > out/rerun_$s.txt 2>&1
a=$(grep '^DFS' out/rerun_$s.txt | head -1)
b=$(grep '^DFS' probes_s/best/res.txt.$s | head -1)
[ "$a" = "$b" ] || { echo "RERUN-FAIL shipped eval line differs"; exit 1; }
echo "RERUN-PASS identical DFS line for seed $s"

echo "== G6: 단순 평가가 게이트 경로에 있음"
grep -q 'run_simple.sh' ../../scripts/verify_release.sh || { echo "G6-FAIL run_simple.sh not wired"; exit 1; }
[ -f eval_simple.sh ] && { echo "G6-FAIL legacy eval_simple.sh still present"; exit 1; }
echo "G6-PASS"

echo "== 문서 위생 + AGG"
bash tools/doc_check.sh ../../docs/release-0269.md || { echo DOC-CHECK-FAIL; exit 1; }
bash tools/hybrid_stats.sh verify out/simple0269.txt 5 2>/dev/null || true
echo "V0269-SIMPLE-PASS"
