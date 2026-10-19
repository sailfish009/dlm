#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ACTIONS="${1:-$ROOT/experiments/graph/actions.sexp}"
BUDGET="${2:-100}"
STORE="${STORE:-$ROOT/experiments/graph/store}"
[[ "$BUDGET" =~ ^[0-9]+$ ]] || { echo 'Expected nonnegative pass budget' >&2; exit 2; }
mkdir -p "$STORE"
exec 9>"$STORE/lock"
flock -n 9 || { echo 'Graph store is already in use' >&2; exit 1; }
TMP="$(mktemp "$STORE/.state.XXXXXX")"
INPUT="$(mktemp "$STORE/.input.XXXXXX")"
trap 'rm -f "$TMP" "$INPUT"' EXIT
{
  printf '(graph-input 75 '
  if [[ -f "$STORE/state.sexp" ]]; then cat "$STORE/state.sexp"; else printf '()'; fi
  cat "$ACTIONS"
  printf ' %s)\n' "$BUDGET"
} > "$INPUT"
"$ROOT/scripts/run.sh" graph-session < "$INPUT" > "$TMP"
# Verify the actual serialized datum before replacing the last good snapshot.
REPORT="$("$ROOT/scripts/run.sh" graph-report < "$TMP")"
ID="$(date -u +%Y%m%dT%H%M%S%N)-$RANDOM"
cp "$TMP" "$STORE/$ID.sexp"
mv -f "$TMP" "$STORE/state.sexp"
printf '%s\n' "$REPORT"
