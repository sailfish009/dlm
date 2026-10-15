#!/usr/bin/env bash
# DLM v0.0058 -- recursive self-supervised learning (the ONE loop).
#
# Each round the model:
#   PERCEIVE  a new program (the real main.py -> the 12-program corpus -> a
#             deterministic stream of generated variants),
#   LEARN     concepts over the corpus it ALREADY had (its own past output),
#   EVALUATE  re-derive them by proof on the held-out program through the
#             kernel, recursively reify its own `calls` relation, and
#             self-assess from the kernel closure only,
#   SUMMARIZE the round in one natural-language sentence built from its own
#             derived conclusions -- never from a label,
#   ADMIT     fold the program in, so the next round learns from more.
#
# The kernel is the only judge and nothing is supervised.  THE LOOP DOES NOT STOP
# ON ITS OWN: watch the round summaries and press Ctrl-C when you have seen
# enough.  The round in flight is finished and the report is written; press
# Ctrl-C a second time to force an immediate stop.
#
# Usage (no arguments needed):
#   ./experiments/selfssl/selfssl.sh
# Extra flags are forwarded for the harness / a bounded check:
#   ./experiments/selfssl/selfssl.sh --rounds 3      # bounded (CI / quick look)
#   ./experiments/selfssl/selfssl.sh --online        # allow live acquisition
#   OUTDIR=reports/selfssl/mine ./experiments/selfssl/selfssl.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTDIR="${OUTDIR:-reports/selfssl/${STAMP}}"
mkdir -p "$OUTDIR"

echo "== recursive self-supervised learning -> $OUTDIR"
echo "== watch the round summaries; press Ctrl-C to stop when you choose"
# -u so every round summary is visible immediately, not buffered.
set +e
python3 -u "$HERE/run.py" --json "$OUTDIR/result.json" "$@"
STATUS=$?
set -e
echo
echo "result: $OUTDIR/result.json"
exit "$STATUS"