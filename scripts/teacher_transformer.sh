#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/adapters/teacher_transformer.py"
exec env MARU="${MARU:-$ROOT/maru-compiler}" \
  "$ROOT/scripts/run.sh" proof-extra \
  "$ROOT/experiments/teacher_transformer_repl/teacher_data.l" \
  "$ROOT/experiments/teacher_transformer_repl/start.l"
