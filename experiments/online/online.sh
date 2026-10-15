#!/usr/bin/env bash
# DLM v0.0039 online experiment: referents stream in one batch at a time; the
# theory keeps up (learns, and for the `abstract` arm compresses itself).  A rich
# JSONL row is logged per round, then read back as a multi-aspect learning report.
#
# Usage:
#   ./experiments/online/online.sh                      # 4 arms x 3 seeds x 6 rounds
#   ./experiments/online/online.sh --quick              # tiny smoke test
#   ./experiments/online/online.sh --big                # more data (slower)
#   ./experiments/online/online.sh --arms plain,abstract --seeds 0,1,2
#   ./experiments/online/online.sh --rounds 10 --n-train 32 --chains 4
#   OUTDIR=reports/online/mine ./experiments/online/online.sh
#
# Every run writes to a timestamped directory under reports/online/:
#   <outdir>/<arm>_s<seed>.jsonl   one rich JSON row per online round
#   <outdir>/summary.json          per-arm aggregate + per-round curve
#   <outdir>/analysis.txt          the multi-aspect learning report (also printed)
#
# Arms: frozen (no learning) | plain (learn) | abstract (learn + abstract_theory)
#       | random (control: random positives).
set -euo pipefail
cd "$(dirname "$0")/../.."          # repo root
export PYTHONPATH="${PYTHONPATH:-.}:."
mkdir -p reports/online

STAMP="$(date +%Y%m%d-%H%M%S)"
# honour --outdir in the arguments as well as the OUTDIR env var, so the log
# analysis reads the same directory the run wrote to.
ARG_OUTDIR=""; _prev=""
for _a in "$@"; do [[ "$_prev" == "--outdir" ]] && ARG_OUTDIR="$_a"; _prev="$_a"; done
OUTDIR="${ARG_OUTDIR:-${OUTDIR:-reports/online/${STAMP}}}"
mkdir -p "$OUTDIR"

echo "== online learning -> $OUTDIR"
if [[ -n "$ARG_OUTDIR" ]]; then
  python3 -u experiments/online/run.py "$@"
else
  python3 -u experiments/online/run.py --outdir "$OUTDIR" "$@"
fi

echo
echo "== log analysis"
python3 -u experiments/online/run.py --analyze "$OUTDIR" | tee "$OUTDIR/analysis.txt"

echo
echo "logs: $OUTDIR"