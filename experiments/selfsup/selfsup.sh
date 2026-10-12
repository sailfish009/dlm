#!/usr/bin/env bash
# Run the verifiable-reward self-supervised loop (DLM v0.0024).
# Offline, deterministic; writes a timestamped JSON report under reports/.
set -euo pipefail
cd "$(dirname "$0")/../.."          # repo root
export PYTHONPATH="${PYTHONPATH:-.}:."
mkdir -p reports
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${OUT:-reports/selfsup_${STAMP}.json}"
exec python3 -u experiments/selfsup/run.py --json "$OUT" "$@"
