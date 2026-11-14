#!/usr/bin/env bash
# Release gate: verify the FROZEN teacher observations natively (Maru only).
# No Python/PyTorch on this path. Regeneration is offline and separate:
#   scripts/teacher_transformer_generate.sh  (needs torch; not a release gate)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/experiments/teacher_transformer_repl/teacher_data.l"
test -f "$DATA" || { echo "missing frozen teacher data: $DATA"; exit 1; }
echo "TEACHER-DATA-FROZEN sha256=$(sha256sum "$DATA" | cut -d' ' -f1)"
exec env MARU="${MARU:-$ROOT/maru-compiler}" \
  "$ROOT/scripts/run.sh" proof-extra \
  "$DATA" \
  "$ROOT/experiments/teacher_transformer_repl/start.l"
