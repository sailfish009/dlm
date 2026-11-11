#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/scripts/run.sh" proof "$ROOT/experiments/synth_mlir_pipeline_repl/start.l"
