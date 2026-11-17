#!/usr/bin/env bash
# 0.0270 confirmation round: extend six arms to 15 seeds (71-85) and recompute
# the paired contrasts. The gated matrix (run_rel0270.sh) stays at 5 seeds.
set -euo pipefail
cd "$(dirname "$0")"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
declare -A EX=( [S0]="--branch 5" [S0e]="--branch 5" [S1]="--branch 5" [S1shuf]="--branch 5" [S0_focus]="--branch 5 --goal-directed 1" [S1_focus]="--branch 5 --goal-directed 1" [S1_assert]="--branch 5" [S1_assert_rand]="--branch 5" [S1_assert_union]="--branch 5" )
for a in S0 S0e S1 S1shuf S0_focus S1_focus S1_assert S1_assert_rand S1_assert_union; do
(
  : > probes_r/$a/cfg_ext.txt
  for s in 76 77 78 79 80 81 82 83 84 85; do
    [ -f "probes_r/$a/w_$s.bin" ] || bin/r_$a --train --seeds 1 --seed-base $s --epochs 40 $CFG --goaldepth 2 \
      --save-weights probes_r/$a/w_$s.bin --no-bound > probes_r/$a/train_$s.log 2>&1
    bin/r_$a --train --seeds 1 --seed-base $s $CFG --goaldepth 4 --beam 3 --dfs --subsume 1 --prop 1 --no-bound ${EX[$a]} \
      --load-weights probes_r/$a/w_$s.bin >> probes_r/$a/cfg_ext.txt
  done
) &
done
wait
python3 - <<'PY' | tee out/confirm0270.txt
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
for a in arms:
    assert len(R[a])==15, (a,len(R[a]))
    print(f"MEAN15 {a} goal={st.mean(R[a].values()):.4f}")
def paired(a,b):
    ds=[R[a][s]-R[b][s] for s in sorted(R[a])]
    m=st.mean(ds); se=st.stdev(ds)/len(ds)**0.5
    print(f"CONTRAST15 {a}-{b} mean={m:+.4f} se1={se:.4f} 2se={2*se:.4f} {'SIGNIFICANT' if abs(m)>2*se else 'INCONCLUSIVE'}")
for a,b in [("S1","S0"),("S0e","S0"),("S1","S1shuf"),("S0_focus","S0"),("S1_focus","S1"),("S1_focus","S0_focus"),("S0_focus","S1"),("S1_assert","S1_focus"),("S1_assert","S1_assert_rand"),("S1_assert_union","S1_focus"),("S1_assert_union","S1")]:
    paired(a,b)
PY
echo "V0270-CONFIRM-DONE"