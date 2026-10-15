#!/usr/bin/env bash
# DLM v0.0049 integral layers: forward closure + evidence measure + credit holonomy.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
exec env PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 "$HERE/run.py" "$@"