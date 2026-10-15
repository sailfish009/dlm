#!/usr/bin/env bash
# DLM v0.0043 core-concept (gist) capture: list concrete facts, detect the gap,
# SEARCH for the missing domain knowledge, re-learn, and certify the concept.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
exec env PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 "$HERE/run.py" "$@"
