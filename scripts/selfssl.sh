#!/usr/bin/env bash
# Exec only: all jobs and the original reader live in one Maru process.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO=false
MODE=learn
if [[ "${1:-}" == --help || "${1:-}" == -h ]]; then
  echo 'usage: selfssl.sh [--demo|--reasoning|--space] [snapshot.sexp]'; exit 0
fi
case "${1:-}" in
 --demo) DEMO=true; shift ;;
 --reasoning) MODE=reason; shift ;;
 --space) MODE=space; shift ;;
esac
(( $# <= 1 )) || { echo 'usage: selfssl.sh [--demo|--reasoning|--space] [snapshot.sexp]' >&2; exit 2; }
DEFAULT="$ROOT/experiments/repl/store/state.sexp"
if [[ "$MODE" == reason ]]; then DEFAULT="$ROOT/experiments/repl/store/reasoning78.sexp"; fi
if [[ "$MODE" == space ]]; then DEFAULT="$ROOT/experiments/repl/store/space79.sexp"; fi
STORE="${1:-${DLM_STORE:-$DEFAULT}}"
[[ ! "$STORE" =~ ^[0-9]+$ ]] || { echo 'This is the native REPL launcher, not the old rounds argument. Use --help.' >&2; exit 2; }
exec "$ROOT/scripts/run.sh" "$MODE" "$STORE" "$DEMO"
