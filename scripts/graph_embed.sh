#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/adapters/graph_embed.py" \
  "$ROOT/experiments/graph_embed_repl/graph.json" \
  "$ROOT/experiments/graph_embed_repl/embeddings.l"
exec env MARU="${MARU:-$ROOT/maru-compiler}" \
  "$ROOT/scripts/run.sh" proof-extra \
  "$ROOT/experiments/graph_embed_repl/embeddings.l" \
  "$ROOT/experiments/graph_embed_repl/start.l"
