#!/usr/bin/env bash
# DLM v0.0055 recursive self-supervised learning experiment.
#
# The model bootstraps reachability from a graph of `edge` facts WITHOUT the
# relational transitive rule: each round it kernel-closes its current relation
# under two definitional level rules and reifies the certified extension, so its
# own output is the next round's input.  It reaches the full transitive closure
# in O(log diameter) rounds, then abstains (fixpoint).  A depth-1 control shows a
# single composition cannot.
#
# Usage:
#   ./experiments/recursive/recursive.sh                 # chain24 + dag16
#   OUTDIR=reports/recursive/mine ./experiments/recursive/recursive.sh
set -euo pipefail
cd "$(dirname "$0")/../.."          # repo root
export PYTHONPATH="${PYTHONPATH:-.}:."
mkdir -p reports/recursive

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTDIR="${OUTDIR:-reports/recursive/${STAMP}}"
mkdir -p "$OUTDIR"

echo "== recursive self-supervised learning -> $OUTDIR"
python3 -u experiments/recursive/run.py --json "$OUTDIR/result.json" "$@"
echo
echo "result: $OUTDIR/result.json"