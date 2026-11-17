#!/usr/bin/env bash
# 단순 평가: 같은 탐색(branch 5, 예산 4)에서 3개 구성만 비교한다.
#   base  = 기존 라벨(단일스텝 knob: utility, 규칙비용 포함), 계약 없음
#   label = 새 라벨(정확 DP 값, 규칙비용 제거), 계약 없음
#   best  = 새 라벨 + 2규칙 계약
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out probes_s
SEEDS="${SEEDS:-5}"; SEED_BASE="${SEED_BASE:-81}"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
EVAL="--goaldepth 4 --eval-budget 4 --beam 3 --dfs --branch 5 --subsume 1 --prop 1 --no-bound"
declare -A FLAGS=( [base]="" [label]="-DVALMODE=1 -DLABEL_NCOST=1"
                   [best]="-DVALMODE=1 -DLABEL_NCOST=1 -DLEMMA=1 -DPAIRMODE=1" )
for a in base label best; do clang -O2 -DHARD_GOALS=1 -DRELOB=1 -Iinclude -Isrc ${FLAGS[$a]} src/pst.c -o "bin/s_$a" -lm; done
run_arm () {
  local a="$1"; mkdir -p "probes_s/$a"; : > "probes_s/$a/res.txt"
  for i in $(seq 0 $((SEEDS-1))); do
    local s=$((SEED_BASE+i))
    "bin/s_$a" --train --seeds 1 --seed-base "$s" --epochs 40 $CFG --goaldepth 2 \
      --save-weights "probes_s/$a/w_$s.bin" --no-bound > "probes_s/$a/train_$s.log" 2>&1
    "bin/s_$a" --train --seeds 1 --seed-base "$s" $CFG $EVAL \
      --load-weights "probes_s/$a/w_$s.bin" >> "probes_s/$a/res.txt"
  done
}
for a in base label best; do run_arm "$a" & done
wait
python3 - <<'PY'
import statistics as st
def load(a):
    g=[]; f=[]; n=[]
    for line in open(f'probes_s/{a}/res.txt'):
        if line.startswith('DFS'):
            kv=dict(x.split('=') for x in line.split()[1:] if '=' in x)
            g.append(float(kv['goal'])); f.append(float(kv['full'])); n.append(int(kv['nodes']))
    return g,f,n
print()
print("구성     목표달성   완전성공   노드     (5시드 평균, 예산4·branch5)")
base_g,base_f,_=load('base')
for a,name in [('base','base'),('label','label'),('best','best')]:
    g,f,n=load(a)
    m=st.mean(g); mf=st.mean(f)
    dg=m-st.mean(base_g)
    print(f"{name:8s} {m:8.4f} {mf:10.4f} {st.mean(n):8.0f}   ({dg:+.4f} vs base)")
print()
# 시드별 paired 차이의 2SE (간단히)
def pair(a,b):
    ga,_,_=load(a); gb,_,_=load(b)
    d=[x-y for x,y in zip(ga,gb)]
    return st.mean(d), 2*st.stdev(d)/len(d)**0.5
for a in ['label','best']:
    m,s=pair(a,'base')
    print(f"{a}-base = {m:+.4f}  (2SE {s:.4f})  {'유의' if abs(m)>s else '잡음'}")
PY
