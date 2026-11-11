#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -f /tmp/dlm-web-store.l
"$ROOT/scripts/run.sh" proof "$ROOT/experiments/web_persist_repl/p1.l"
"$ROOT/scripts/run.sh" proof "$ROOT/experiments/web_persist_repl/p2.l"
