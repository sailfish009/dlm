#!/usr/bin/env bash
# Goal-conditioned execution control (DLM v0.0028, NOTE 80).
# Writes a timestamped report under reports/ and prints it.
set -euo pipefail
cd "$(dirname "$0")/../.."
stamp="$(date +%Y%m%d-%H%M%S)"
PYTHONPATH=. python experiments/control/run.py "$@" --json "reports/control_${stamp}.json"
