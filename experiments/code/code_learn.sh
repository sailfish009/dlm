#!/usr/bin/env bash
# DLM v0.0039 code experiment: download small random Python repos from GitHub,
# turn their module import graphs into (imports M N) Horn facts, hold out whole
# repos, and let the kernel induce the transitivity law on the train repos.
#
# Usage:
#   ./experiments/code/code_learn.sh                       # 5 repos, seed 1
#   ./experiments/code/code_learn.sh --synthetic           # network-free smoke test
#   ./experiments/code/code_learn.sh --repos 8 --seed 3
#   ./experiments/code/code_learn.sh --offline             # replay from cache
#   OUTDIR=reports/code/mine ./experiments/code/code_learn.sh
#
# Runs write to a timestamped directory under reports/code/:
#   <outdir>/result.json     the experiment record (corpus/graph/arms/verdict)
#
# Note: unauthenticated GitHub API allows ~10 search requests/minute.  Repos are
# cached under experiments/code/cache/ so reruns and --offline never re-fetch.
set -euo pipefail
cd "$(dirname "$0")/../.."          # repo root
export PYTHONPATH="${PYTHONPATH:-.}:."
mkdir -p reports/code

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTDIR="${OUTDIR:-reports/code/${STAMP}}"
mkdir -p "$OUTDIR"

echo "== code learning -> $OUTDIR"
python3 -u experiments/code/run.py --json "$OUTDIR/result.json" "$@"

echo
echo "result: $OUTDIR/result.json"