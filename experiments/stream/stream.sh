#!/usr/bin/env bash
# DLM v0.0038 stream experiment: does Experience accumulate round by round?
#
#   ./stream.sh                       # synthetic, seeds 1 2 3  (multi-relation laws)
#   SEEDS="1 2 3 4 5" ./stream.sh     # more seeds
#   WEB=1 DOCS=120 CACHE=... ./stream.sh   # real web facts (multi-relation)
#
# The law is induced on train entities and scored after EVERY round on disjoint
# unseen test entities.  A working learning structure must (a) add a new sound
# clause each round and (b) strictly increase held-out recovery.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

SEEDS="${SEEDS:-1 2 3}"
OUTDIR="${OUTDIR:-$HERE/reports}"
mkdir -p "$OUTDIR"

FLAGS=()
if [ "${WEB:-0}" = "1" ]; then
    FLAGS+=(--web --docs "${DOCS:-120}" --cache "${CACHE:-$ROOT/experiments/web/cache}")
    [ "${OFFLINE:-0}" = "1" ] && FLAGS+=(--offline)
fi

echo "DLM v0.0038 stream experiment  (web=${WEB:-0} seeds=[$SEEDS])"
echo
fail=0
for s in $SEEDS; do
    python experiments/stream/run.py "${FLAGS[@]}" --seed "$s" \
        --json "$OUTDIR/stream_seed${s}.json" 2>/dev/null | tail -n 40
    rc=${PIPESTATUS[0]}
    if [ "$rc" -ne 0 ]; then echo "  (seed $s: verdict not all-true, exit=$rc)"; fail=1; fi
    echo
done

echo "== summary =="
python - "$OUTDIR" $SEEDS <<'PY'
import json, sys
outdir, seeds = sys.argv[1], sys.argv[2:]
for s in seeds:
    try:
        d = json.load(open(f"{outdir}/stream_seed{s}.json"))
    except OSError:
        continue
    curve = " ".join(f"{c['held_recovery']:.3f}" for c in d["curve"])
    fmax = max((c["false"] for c in d["curve"]), default=0)
    ok = "OK " if all(d["verdict"].values()) else "FAIL"
    print(f"  seed {s}: {ok} identity={d['identity_recovery']:.3f} "
          f"curve=[{curve}] false_max={fmax}")
PY

echo
if [ "$fail" -eq 0 ]; then echo "VERDICT: PASS"; else echo "VERDICT: FAIL"; fi
exit "$fail"