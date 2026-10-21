#!/usr/bin/env bash
# Compatibility fixture for symbolic-state73; NOT the DLM77 learning launcher.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STORE="${STORE:?test STORE directory required}"
ROUNDS="${1:?bounded round count required}"
[[ "$ROUNDS" =~ ^[1-9][0-9]*$ ]] || exit 2
mkdir -p "$STORE"
exec 9>"$STORE/lock"
flock -n 9 || exit 1
TMP="$(mktemp "$STORE/.candidate.XXXXXX")"
trap 'rm -f "$TMP"' EXIT
for ((count=0; count<ROUNDS; count++)); do
  if [[ -f "$STORE/state.sexp" ]]; then
    "$ROOT/scripts/run.sh" session "$ROOT/experiments/symbolic/session.l" < "$STORE/state.sexp" > "$TMP"
  else
    printf '()\n' | "$ROOT/scripts/run.sh" session "$ROOT/experiments/symbolic/session.l" > "$TMP"
  fi
  ID="$(date -u +%Y%m%dT%H%M%S%N)-$RANDOM"
  cp "$TMP" "$STORE/$ID.sexp"
  mv -f "$TMP" "$STORE/state.sexp"
done
