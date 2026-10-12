#!/usr/bin/env bash
# Run the bounded execution-control + experience-feedback experiment (DLM v0.0027).
# Offline, deterministic; writes a timestamped JSON report under reports/.
set -euo pipefail
cd "$(dirname "$0")/../.."          # repo root
export PYTHONPATH="${PYTHONPATH:-.}:."
mkdir -p reports
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${OUT:-reports/execution_${STAMP}.json}"
exec python3 -u experiments/execution/run.py --json "$OUT" "$@"
