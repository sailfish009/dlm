#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/adapters/web_recursive.py"
exec env MARU="${MARU:-$ROOT/maru-compiler}" \
  "$ROOT/scripts/run.sh" proof-extra \
  "$ROOT/experiments/web_recursive_repl/web_data.l" \
  "$ROOT/experiments/web_recursive_repl/start.l"
