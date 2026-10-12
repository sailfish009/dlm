#!/usr/bin/env bash
# Reproduce the DLM v0.0030 explanation / abstraction report.
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p reports
PYTHONPATH=. python experiments/explain/run.py "$@" --json reports/explain.json > /dev/null
echo "wrote reports/explain.json"
