#!/usr/bin/env bash
# Only a launcher: learning and input scheduling stay in one Maru process.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO=false
MODE=learn
if [[ "${1:-}" == --help || "${1:-}" == -h ]]; then
  echo 'usage: selfssl.sh [--demo|--reasoning] [snapshot.sexp]'; exit 0
fi
if [[ "${1:-}" == --demo ]]; then DEMO=true; shift
elif [[ "${1:-}" == --reasoning ]]; then MODE=reason; shift; fi
(( $# <= 1 )) || { echo 'usage: selfssl.sh [--demo|--reasoning] [snapshot.sexp]' >&2; exit 2; }
DEFAULT="$ROOT/experiments/repl/store/state.sexp"
if [[ "$MODE" == reason ]]; then DEFAULT="$ROOT/experiments/repl/store/reasoning78.sexp"; fi
STORE="${1:-${DLM_STORE:-$DEFAULT}}"
[[ ! "$STORE" =~ ^[0-9]+$ ]] || { echo 'This is the native REPL launcher, not the old rounds argument. Use --help.' >&2; exit 2; }
exec "$ROOT/scripts/run.sh" "$MODE" "$STORE" "$DEMO"
