#!/usr/bin/env bash
# ONE original Maru process: generated programs, branch execution, checking,
# recursive definitions, replay-verified storage and the existing REPL reader.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO=false; ROUNDS=0; INTERVAL=1000; BUDGET=8
STORE=""; HAVE_STORE=false
usage() {
  printf '%s\n' 'usage: recursive-selfssl.sh [--demo] [--rounds N] [--interval MS] [--budget N] [snapshot.sexp]' \
    'Default: original interactive Maru REPL with cooperative recursive learning.' \
    '--demo adds explicit observations only when no source episodes remain; no hidden axioms.' \
    '--rounds 1..1000 runs a finite native experiment and closes durably.' \
    '--interval 20..60000 milliseconds; --budget 1..16 candidate decisions per batch.' \
    'Ctrl-C ends the process; only already completed checkpoints are durable.'
}
while (( $# )); do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --demo) DEMO=true; shift ;;
    --rounds|--interval|--budget)
      option="$1"; (( $# >= 2 )) || { usage >&2; exit 2; }
      [[ "$2" =~ ^(0|[1-9][0-9]{0,4})$ ]] || { echo "Invalid number: $2" >&2; exit 2; }
      case "$option" in
        --rounds) ROUNDS="$2"; (( ROUNDS >= 1 && ROUNDS <= 1000 )) || exit 2 ;;
        --interval) INTERVAL="$2"; (( INTERVAL >= 20 && INTERVAL <= 60000 )) || exit 2 ;;
        --budget) BUDGET="$2"; (( BUDGET >= 1 && BUDGET <= 16 )) || exit 2 ;;
      esac
      shift 2 ;;
    --*) usage >&2; exit 2 ;;
    *) [[ "$HAVE_STORE" == false ]] || { usage >&2; exit 2; }
       STORE="$1"; HAVE_STORE=true; shift ;;
  esac
done
STORE="${STORE:-${DLM_STORE:-$ROOT/experiments/repl/store/recursive86.sexp}}"
# run.sh changes directory; preserve the caller's relative snapshot path.
if [[ "$STORE" != /* ]]; then STORE="$PWD/$STORE"; fi
exec "$ROOT/scripts/run.sh" recursive86 "$STORE" "$DEMO" "$ROUNDS" "$INTERVAL" "$BUDGET"
