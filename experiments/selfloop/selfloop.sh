#!/usr/bin/env bash
# DLM v0.0056 closed-loop recursive self-supervised learning -- the north star.
#
# Each round the model: PERCEIVES a new program (real main.py -> the 12-program
# corpus -> generated variants), LEARNS concepts over the corpus it already had
# (its own past output), EVALUATES by re-deriving those concepts on the held-out
# new program through the kernel and reifying its own `calls` relation, then
# SUMMARISES the round in one natural-language sentence built from its own
# derived conclusions -- and folds the new program in, so the next round learns
# from strictly more of its own output.  Nothing is supervised; the kernel is the
# only judge.
#
# TERMINATION IS MANUAL.  The loop runs forever; watch the round summaries and
# press Ctrl-C when you have seen enough.  The current round is allowed to finish
# and then the report is written.  Press Ctrl-C a second time to force an
# immediate stop.  A bounded run is available for testing with `-- --rounds N`.
#
# Usage:
#   ./experiments/selfloop/selfloop.sh                 # run until you Ctrl-C
#   ./experiments/selfloop/selfloop.sh --rounds 3      # bounded (for a check)
#   ./experiments/selfloop/selfloop.sh --online        # allow live acquisition
#   OUTDIR=reports/selfloop/mine ./experiments/selfloop/selfloop.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTDIR="${OUTDIR:-reports/selfloop/${STAMP}}"
mkdir -p "$OUTDIR"

echo "== closed-loop recursive self-supervised learning -> $OUTDIR"
echo "== watch the round summaries; press Ctrl-C to stop when you choose"
# -u so every round summary is visible immediately, not buffered.
set +e
python3 -u "$HERE/run.py" --json "$OUTDIR/result.json" "$@"
STATUS=$?
set -e
echo
echo "result: $OUTDIR/result.json"
exit "$STATUS"