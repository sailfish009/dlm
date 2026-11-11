#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/scripts/run.sh" proof "$ROOT/experiments/constraint_graph_repl/start.l"
