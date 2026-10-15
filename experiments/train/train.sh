#!/usr/bin/env bash
# DLM v0.0039 train harness: the accumulating learner vs a memoryless refit.
#
#   ./experiments/train/train.sh                 # synthetic, seeds 1 2 3
#   SEEDS="1 2 3 4 5" ./experiments/train/train.sh
#   ROUNDS=6 N_TRAIN=32 ./experiments/train/train.sh
#   ./experiments/train/train.sh --no-compress   # ablation: MDL compression off
#
# Negatives are revealed progressively, so an early over-general rule is later
# falsified; accumulation RETRACTS it, a refit merely rebuilds.  Every report
# carries the two deterministic probes (retraction fires, checkpoint round-trips).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

SEEDS="${SEEDS:-1 2 3}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUTDIR="${OUTDIR:-$HERE/reports/$STAMP}"
mkdir -p "$OUTDIR"

FLAGS=(--rounds "${ROUNDS:-4}" --n-train "${N_TRAIN:-24}" --n-test "${N_TEST:-18}"
       --chains "${CHAINS:-3}" --chain-len "${CHAIN_LEN:-6}" --max-neg "${MAX_NEG:-8000}")
[ "${NO_COMPRESS:-0}" = "1" ] && FLAGS+=(--no-compress)

echo "DLM v0.0039 train harness  (seeds=[$SEEDS] out=$OUTDIR)"
echo
fail=0
for s in $SEEDS; do
    python experiments/train/accumulate.py "${FLAGS[@]}" --seed "$s" \
        --json "$OUTDIR/acc_seed${s}.json" >/dev/null 2>&1
    rc=$?
    if [ "$rc" -ne 0 ]; then echo "  (seed $s: verdict not all-true, exit=$rc)"; fail=1; fi
    echo
done

echo "== summary =="
python - "$OUTDIR" $SEEDS <<'PY'
import json, sys
outdir, seeds = sys.argv[1], sys.argv[2:]
for s in seeds:
    try:
        d = json.load(open(f"{outdir}/acc_seed{s}.json"))
    except OSError:
        continue
    a, r = d["arms"]["accumulate"], d["arms"]["refit"]
    curve = " ".join(f"{x['held_recovery']:.3f}" for x in a["records"])
    ok = "OK " if all(d["verdict"].values()) else "FAIL"
    print(f"  seed {s}: {ok} identity={d['identity_recovery']:.3f} "
          f"accumulate={a['held_recovery']:.3f} refit={r['held_recovery']:.3f} "
          f"retractions={a['retraction_events']} false={a['false_final']} "
          f"dups={a['duplicate_rules']} curve=[{curve}]")
PY

echo
if [ "$fail" -eq 0 ]; then echo "VERDICT: PASS"; else echo "VERDICT: FAIL"; fi
exit "$fail"