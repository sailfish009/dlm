#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/adapters/web_rule.py"
exec env MARU="${MARU:-$ROOT/maru-compiler}" \
  "$ROOT/scripts/run.sh" proof-extra \
  "$ROOT/experiments/web_rule_repl/web_observations.l" \
  "$ROOT/experiments/web_rule_repl/start.l"
