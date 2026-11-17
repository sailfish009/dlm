#!/usr/bin/env bash
# 단순 실험: 같은 라벨 위에서 탐색만 3가지로 비교 (5시드).
#   best      계약 + branch 5, 예산 4   (0268 최고 구성)
#   best_b8   계약 + branch 8, 예산 4
#   best_e5   계약 + branch 5, 예산 5   (라벨은 예산4로 고정)
# 그리고 완전탐색 천장(branch 64)을 시드별로 측정한다.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_s probes_s/ceil
SEEDS="${SEEDS:-5}"; SEED_BASE="${SEED_BASE:-81}"; EPOCHS="${EPOCHS:-40}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
FLAGS="-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc $FLAGS src/pst.c -o bin/s_best -lm
declare -A EXTRA=(
  [best]="--branch 5 --eval-budget 4"
  [best_b8]="--branch 8 --eval-budget 4"
  [best_e5]="--branch 5 --eval-budget 5"
)
run_arm () {
  local a="$1"; mkdir -p "probes_s/$a"; : > "probes_s/$a/res.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    [ -f "probes_s/best/w_$s.bin" ] || bin/s_best --train --seeds 1 --seed-base "$s" --epochs "$EPOCHS" \
      $CFG --goaldepth 2 --save-weights "probes_s/best/w_$s.bin" --no-bound > "probes_s/best/train_$s.log" 2>&1
    bin/s_best --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --beam 3 --dfs --subsume 1 --prop 1 \
      --no-bound ${EXTRA[$a]} --load-weights "probes_s/best/w_$s.bin" > "probes_s/$a/res.txt.$s"
  done
}
for a in best best_b8 best_e5; do run_arm "$a" & done
wait
for a in best best_b8 best_e5; do cat probes_s/$a/res.txt.* > "probes_s/$a/res.txt"; done
# 시드별 완전탐색 천장 (branch 64 = 계약 행동공간 절단 없음)
for i in $(seq 0 $((SEEDS-1))); do
  s=$((SEED_BASE+i))
  bin/s_best --train --seeds 1 --seed-base "$s" $CFG --goaldepth 4 --eval-budget 4 --dfs --branch 64 \
    --subsume 1 --prop 1 --no-bound --load-weights "probes_s/best/w_$s.bin" > "probes_s/ceil/seed_$s.txt" 2>&1 &
done
wait
python3 - <<'PY'
import statistics as st, glob, re
def load(a):
    g=[]; f=[]; n=[]; sd=[]
    for line in open(f'probes_s/{a}/res.txt'):
        if line.startswith('DFS'):
            kv=dict(x.split('=') for x in line.split()[1:] if '=' in x)
            g.append(float(kv['goal'])); f.append(float(kv['full'])); n.append(int(kv['nodes']))
    return g,f,n
ceil={}
for p in glob.glob('probes_s/ceil/seed_*.txt'):
    s=int(re.search(r'seed_(\d+)',p).group(1))
    for line in open(p):
        if line.startswith('DFS'):
            ceil[s]=float(dict(x.split('=') for x in line.split()[1:] if '=' in x)['goal'])
g0,_,_=load('best')
out=[]
print()
print(f"{'구성':10s} {'목표':>7s} {'완전':>7s} {'노드':>7s}   vs best")
for a in ['best','best_b8','best_e5']:
    g,f,n=load(a)
    d=[x-y for x,y in zip(g,g0)]
    m=st.mean(d); s2=2*st.stdev(d)/len(d)**0.5
    print(f"{a:10s} {st.mean(g):7.4f} {st.mean(f):7.4f} {st.mean(n):7.0f}   {m:+.4f} (2SE {s2:.4f}) {'유의' if len(d)>1 and abs(m)>s2 else '잡음'}")
    out.append(f"ARM {a} goal={st.mean(g):.4f} full={st.mean(f):.4f} nodes={st.mean(n):.0f} n={len(g)}")
c=st.mean(ceil.values())
print(f"\n천장(계약 완전탐색, branch 64): {c:.4f}  시드별 {sorted(round(v,4) for v in ceil.values())}")
out.append(f"CEILING goal={c:.4f} seeds={sorted(ceil)}")
open('out/simple0269.txt','w').write('\n'.join(out)+'\n')
PY
