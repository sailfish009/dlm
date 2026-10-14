#!/usr/bin/env bash
# DLM v0.0038 web experiment: fetch random web data -> learn on Ground/Experience.
#
#   ./web_learn.sh                 # online, seeds 1 2 3, 60 random articles each
#   DOCS=40 SEEDS="1" ./web_learn.sh
#   OFFLINE=1 CACHE=/path/to/cache ./web_learn.sh   # reproduce from cache, no network
#
# Everything is cached under experiments/web/cache, so a second run is offline
# and byte-identical.  Reports land in experiments/web/reports/.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

DOCS="${DOCS:-60}"
SEEDS="${SEEDS:-1 2 3}"
MAX_EDGES="${MAX_EDGES:-200}"
SUBCLASS_DEPTH="${SUBCLASS_DEPTH:-3}"
TRAIN_FRAC="${TRAIN_FRAC:-0.7}"
PAUSE="${PAUSE:-0.5}"
RETRIES="${RETRIES:-4}"
CACHE="${CACHE:-$HERE/cache}"
OUTDIR="${OUTDIR:-$HERE/reports}"
mkdir -p "$CACHE" "$OUTDIR"

FLAGS=(--docs "$DOCS" --max-edges "$MAX_EDGES" --subclass-depth "$SUBCLASS_DEPTH"
       --train-frac "$TRAIN_FRAC" --pause "$PAUSE" --retries "$RETRIES" --cache "$CACHE")
if [ "${OFFLINE:-0}" = "1" ]; then FLAGS+=(--offline); fi

echo "DLM v0.0038 web experiment"
echo "  root=$ROOT  docs=$DOCS seeds=[$SEEDS] max_edges=$MAX_EDGES offline=${OFFLINE:-0}"
echo "  cache=$CACHE  reports=$OUTDIR"
echo

fail=0
for s in $SEEDS; do
    echo "== seed $s =="
    python experiments/web/run.py "${FLAGS[@]}" --seed "$s" \
        --json "$OUTDIR/result_seed${s}.json" | tail -n 40
    rc=${PIPESTATUS[0]}
    if [ "$rc" -ne 0 ]; then echo "  (verdict not all-true, exit=$rc)"; fail=1; fi
    echo
done

# determinism: rerun one seed (from cache) and require byte-identical output
echo "== determinism check (seed $(echo $SEEDS | awk '{print $1}')) =="
s1=$(echo $SEEDS | awk '{print $1}')
python experiments/web/run.py "${FLAGS[@]}" --seed "$s1" > "$OUTDIR/.det_a.json" 2>/dev/null
python experiments/web/run.py "${FLAGS[@]}" --seed "$s1" > "$OUTDIR/.det_b.json" 2>/dev/null
if cmp -s "$OUTDIR/.det_a.json" "$OUTDIR/.det_b.json"; then
    echo "  deterministic: byte-identical"
else
    echo "  NON-DETERMINISTIC"; fail=1
fi
rm -f "$OUTDIR/.det_a.json" "$OUTDIR/.det_b.json"

echo
if [ "$fail" -eq 0 ]; then echo "VERDICT: PASS"; else echo "VERDICT: FAIL"; fi
exit "$fail"