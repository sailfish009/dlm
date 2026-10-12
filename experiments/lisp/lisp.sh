#!/usr/bin/env bash
# Reproduce the DLM v0.0029 Lisp-seam report.
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p reports
PYTHONPATH=. python experiments/lisp/run.py "$@" --json reports/lisp.json > /dev/null
echo "wrote reports/lisp.json"
