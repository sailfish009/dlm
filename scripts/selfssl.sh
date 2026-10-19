#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STORE="${STORE:-$ROOT/experiments/symbolic/store}"
ROUNDS="${1:-3}"
[[ "$ROUNDS" =~ ^[0-9]+$ ]] || { echo 'usage: selfssl.sh [rounds, 0=endless]' >&2; exit 2; }
mkdir -p "$STORE"
exec 9>"$STORE/lock"
flock -n 9 || { echo 'Store is already in use' >&2; exit 1; }
TMP="$(mktemp "$STORE/.candidate.XXXXXX")"
trap 'rm -f "$TMP"' EXIT
count=0
while (( ROUNDS == 0 || count < ROUNDS )); do
  if [[ -f "$STORE/state.sexp" ]]; then
    "$ROOT/scripts/run.sh" session "$ROOT/experiments/symbolic/session.l" < "$STORE/state.sexp" > "$TMP"
  else
    printf '()\n' | "$ROOT/scripts/run.sh" session "$ROOT/experiments/symbolic/session.l" > "$TMP"
  fi
  # Keep every committed full event-log generation for inspection/recovery.
  ID="$(date -u +%Y%m%dT%H%M%S%N)-$RANDOM"
  cp "$TMP" "$STORE/$ID.sexp"
  mv -f "$TMP" "$STORE/state.sexp"
  count=$((count + 1))
  echo "Committed recursive round $count ($ID)"
  if (( ROUNDS == 0 )); then sleep 1; fi
done
