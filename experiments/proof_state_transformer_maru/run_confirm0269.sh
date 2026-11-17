#!/usr/bin/env bash
# 0.0269 confirmation round: extend the six branch-5 arms to 15 seeds (71-85)
# and run the mechanism control D_detachpred (static z0 + world-model head).
# The gated matrix (run_loop0269.sh) stays at 5 seeds; this round produces
# probes_y/*/cfg_ext.txt and out/confirm0269.txt.
set -euo pipefail
cd "$(dirname "$0")"
CFG="--collect full --sample sub --train-n 180 --val-n 60 --test-n 100 --goal-scan --balance-reward"
clang -O2 -DHARD_GOALS=1 -DRELOB=1 -DVALMODE=1 -DLABEL_NCOST=1 -DEPTRAIN=1 -DLEMMA=1 -DPAIRMODE=1 \
  -DLOOPCELL=1 -DCELLDETACH=1 -DPREDW=0.5 -Iinclude -Isrc src/pst.c -o bin/y9_D_detachpred -lm
mkdir -p probes_y/D_detachpred
for a in D_pair16_b5 D_cell D_cellpred D_detach D_shuf D_rem D_detachpred; do : > probes_y/$a/cfg_ext.txt; done
: > probes_y/D_detachpred/cfg_4_4.txt
for a in D_pair16_b5 D_cell D_cellpred D_detach D_shuf D_rem; do
(
  for s in 76 77 78 79 80 81 82 83 84 85; do
    [ -f "probes_y/$a/w_$s.bin" ] || bin/y9_$a --train --seeds 1 --seed-base $s --epochs 40 $CFG --goaldepth 2 \
      --save-weights probes_y/$a/w_$s.bin --no-bound > probes_y/$a/train_$s.log 2>&1
    bin/y9_$a --train --seeds 1 --seed-base $s $CFG --goaldepth 4 --beam 3 --dfs --subsume 1 --prop 1 --no-bound --branch 5 \
      --load-weights probes_y/$a/w_$s.bin > probes_y/$a/eval_$s.txt 2>&1
    cat probes_y/$a/eval_$s.txt >> probes_y/$a/cfg_ext.txt
  done
) &
done
(
  for s in 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85; do
    bin/y9_D_detachpred --train --seeds 1 --seed-base $s --epochs 40 $CFG --goaldepth 2 \
      --save-weights probes_y/D_detachpred/w_$s.bin --no-bound > probes_y/D_detachpred/train_$s.log 2>&1
    bin/y9_D_detachpred --train --seeds 1 --seed-base $s $CFG --goaldepth 4 --beam 3 --dfs --subsume 1 --prop 1 --no-bound --branch 5 \
      --load-weights probes_y/D_detachpred/w_$s.bin > probes_y/D_detachpred/eval_$s.txt 2>&1
  done
  for s in 71 72 73 74 75; do cat probes_y/D_detachpred/eval_$s.txt >> probes_y/D_detachpred/cfg_4_4.txt; done
  for s in 76 77 78 79 80 81 82 83 84 85; do cat probes_y/D_detachpred/eval_$s.txt >> probes_y/D_detachpred/cfg_ext.txt; done
) &
wait
python3 - <<'PY' | tee out/confirm0269.txt
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
for a in arms:
    assert len(R[a])==15, f"{a}: {len(R[a])} seeds, need 15"
    print(f"MEAN15 {a} goal={st.mean(R[a].values()):.4f}")
def paired(a,b):
    ds=[R[a][s]-R[b][s] for s in sorted(R[a])]
    m=st.mean(ds); se=st.stdev(ds)/len(ds)**0.5
    print(f"CONTRAST15 {a}-{b} mean={m:+.4f} se1={se:.4f} 2se={2*se:.4f} {'SIGNIFICANT' if abs(m)>2*se else 'INCONCLUSIVE'}")
for a,b in [("D_cell","D_pair16_b5"),("D_cell","D_detach"),("D_cell","D_shuf"),
            ("D_cellpred","D_pair16_b5"),("D_cellpred","D_cell"),
            ("D_cellpred","D_detachpred"),("D_shuf","D_pair16_b5"),("D_rem","D_pair16_b5")]:
    paired(a,b)
PY
echo "V0269-CONFIRM-DONE"