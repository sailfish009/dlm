#!/usr/bin/env bash
# DLM v0.0046 leveled final NL reading: tag every sentence with its abstraction
# level (N1..N8 here) and check each against the kernel closure.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
exec env PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 "$HERE/run.py" "$@"