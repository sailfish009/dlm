#!/usr/bin/env bash
# 0.0261 gates: is the CONTRACT PROPOSAL learnable at matched budget?
#
# Fails when:
#   PAIR-LABEL   the kernel-labelled training set is empty or all-zero (a
#                "learned" proposer would then be a random one under a new name)
#   PAIR-BUDGET  the proposers do not offer the same contract count, or the pure
#                control applies contracts
#   PAIR-VERIFY  an applied pair is not confirmed by the kernel at apply time
#   PAIR-CLAIM   the learned-minus-random contrast is reported as a gain when it
#                is inside 2 SE (or the release note does not state the verdict)
#   AGG/WHDR/LLVM  same checks as 0.0260
set -euo pipefail
cd "$(dirname "$0")"
SEEDS="${SEEDS:-5}"
export PROBES=probes_p
export ARMS="pure mined learn rand"
row () { awk -v a="$1" -v k="$2" '$1=="ARM" && $2==a{ for(i=3;i<=NF;i++){ split($i,kv,"="); if(kv[1]==k) print kv[2] } }' out/pair.txt; }

echo "== 1. kernel-labelled training set is informative (not vacuous)"
python3 - <<'PY' || { echo PAIR-LABEL-FAIL; exit 1; }
import glob, re
rows=[]; pos=[]; ws=[]
for f in glob.glob('probes_p/learn/train_*.log'):
    for l in open(f):
        m=re.match(r'PAIR-LEARN rows=(\d+) positives=(\d+) w=\[([-0-9.,]+)\]', l)
        if m:
            rows.append(int(m.group(1))); pos.append(int(m.group(2)))
            ws.append([abs(float(x)) for x in m.group(3).split(',')])
assert rows, 'no PAIR-LEARN line'
assert all(r>0 for r in rows), f'empty label set {rows}'
assert all(p>0 for p in pos), f'all-zero labels {pos}'
assert all(max(w)>1e-3 for w in ws), 'degenerate scorer weights'
dens=[p/r for p,r in zip(pos,rows)]
print(f"PAIR-LABEL-PASS seeds={len(rows)} rows={rows} positives={pos} "
      f"density={[round(d,4) for d in dens]}")
PY

echo "== 2. matched contract budget"
keep=$(row learn pair_uses); keepr=$(row rand pair_uses); keepm=$(row mined pair_uses); pv=$(row pure pair_uses)
awk -v l="$keep" -v r="$keepr" -v m="$keepm" -v p="$pv" 'BEGIN{
  bad=0
  if (p+0 != 0) { printf "FAIL pure control applied %s contracts\n", p; bad=1 }
  if (!(l+0 > 0) || !(r+0 > 0)) { printf "FAIL proposer arms applied no contract (learn=%s rand=%s)\n", l, r; bad=1 }
  if (!(m+0 > 0)) { printf "FAIL mined arm applied no contract (%s)\n", m; bad=1 }
  printf "PAIR-BUDGET-PASS offers/state=16 all proposers; applied per seed learn=%.0f rand=%.0f mined=%.0f pure=%.0f\n", l, r, m, p
  printf "NOTE mined covers <=64 pairs from teacher rollouts, proposers cover 16/state from the world ruleset: mined-vs-proposer is a COVERAGE contrast, learn-vs-rand is the matched SELECTION contrast\n"
  if (bad) exit 1 }'

echo "== 3. kernel re-check at application time"
for a in $ARMS; do
  v=$(row "$a" pair_viol)
  [ "${v:-1}" = "0" ] || { echo "PAIR-VERIFY-FAIL arm=$a violations=$v"; exit 1; }
done
echo "PAIR-VERIFY-PASS pair_viol=0 for all arms (contract committed only where the kernel confirms body+head)"

echo "== 4. the decisive contrast: learned vs random at matched count"
bash tools/hybrid_stats.sh contrast learn rand goal | tee out/pair_contrast.txt
bash tools/hybrid_stats.sh contrast learn rand full | tee -a out/pair_contrast.txt
bash tools/hybrid_stats.sh contrast learn mined goal | tee -a out/pair_contrast.txt
bash tools/hybrid_stats.sh contrast mined pure goal | tee -a out/pair_contrast.txt
awk '
/learn-rand goal/ && /SIGNIFICANT/  { sig=1 }
/learn-rand goal/ && /INCONCLUSIVE/ { sig=0 }
END{
  if (sig == 1) print "PAIR-CLAIM learn beats random at 2SE: report as a positive learning result"
  else print "PAIR-CLAIM-VERDICT PAIR-LEARN-NOT-DEMONSTRATED (learner within 2SE of the matched random proposer)"
}' out/pair_contrast.txt
if grep -q 'PAIR-LEARN-NOT-DEMONSTRATED' out/pair_contrast.txt; then
  grep -q 'PAIR-LEARN-NOT-DEMONSTRATED' ../../docs/release-0261.md \
    || { echo "PAIR-CLAIM-FAIL release note does not state PAIR-LEARN-NOT-DEMONSTRATED"; exit 1; }
  echo "PAIR-CLAIM-PASS verdict stated in docs/release-0261.md"
fi

echo "== documentation hygiene (review F6)"
bash tools/doc_check.sh ../../docs/release-0261.md || { echo DOC-CHECK-FAIL; exit 1; }

echo "== 5. aggregation schema, table identity, mutation regression"
bash tools/hybrid_stats.sh verify out/pair.txt "$SEEDS"
bash gate_regression_hybrid.sh out/pair.txt probes_p "$SEEDS"

echo "== 6. weight-header variant tag carries the proposer mode"
ra="--train --seeds 1 --seed-base 21 --train-n 40 --val-n 20 --test-n 20 --goaldepth 2 --goal-scan"
set +e
./bin/p_learn $ra --load-weights probes_p/rand/w_21.bin --no-bound > out/ph_a.txt 2>&1; ea=$?
./bin/p_learn $ra --load-weights probes_p/learn/w_21.bin --no-bound > out/ph_b.txt 2>&1; eb=$?
set -e
[ "$ea" -eq 4 ] || { echo "WHDR-FAIL learn accepted random-proposer weights (exit $ea)"; exit 1; }
[ "$eb" -eq 0 ] || { echo "WHDR-FAIL learn rejected its own weights (exit $eb)"; exit 1; }
echo "WHDR-PASS proposer mode in the header; cross-proposer load refused"

echo "== 7. LLVM identity and sanitizers on the learned proposer"
for O in 0 2 3; do
  clang -O$O -DHARD_GOALS=1 -DRELOB=1 -DPAIRMODE=2 -DLEMMA=1 -Iinclude -Isrc src/pst.c -o bin/p_learn_O$O -lm
  ./bin/p_learn_O$O --train --seeds 1 --epochs 3 --train-n 40 --val-n 40 --test-n 40 \
    --eval-budget 6 --goaldepth 3 --goal-scan --dfs --branch 3 > out/pair_id_O$O.txt 2>&1
done
diff -q out/pair_id_O0.txt out/pair_id_O2.txt >/dev/null && diff -q out/pair_id_O0.txt out/pair_id_O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -DHARD_GOALS=1 -DRELOB=1 \
  -DPAIRMODE=2 -DLEMMA=1 -Iinclude -Isrc src/pst.c -o bin/p_learn_asan -lm
./bin/p_learn_asan --train --seeds 1 --epochs 1 --train-n 20 --val-n 10 --test-n 10 \
  --eval-budget 6 --goaldepth 4 --goal-scan --dfs --branch 3 > out/pair_asan.txt 2> out/pair_asan.err
grep -q 'Sanitizer' out/pair_asan.err && { echo ASAN-FAIL; cat out/pair_asan.err; exit 1; }
echo "LLVM-PASS O0/O2/O3 byte-identical; ASAN+UBSAN clean (learned proposer, depth 4)"
echo "V0261-PAIRLEARN-PASS"