#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -f /tmp/dlm-web-recursive-basis.l
python3 "$ROOT/adapters/web_recursive.py"
"$ROOT/scripts/run.sh" proof-extra \
  "$ROOT/experiments/web_recursive_repl/web_data.l" \
  "$ROOT/experiments/web_recursive_persist_repl/p1.l"
"$ROOT/scripts/run.sh" proof-extra \
  "$ROOT/experiments/web_recursive_repl/web_data.l" \
  "$ROOT/experiments/web_recursive_persist_repl/p2.l"
