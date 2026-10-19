#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STORE="${STORE:-$ROOT/experiments/web/store}"
PYTHON="${PYTHON:-python3}"
mkdir -p "$STORE"
exec 9>"$STORE/lock"
flock -n 9 || { echo 'Web store is already in use' >&2; exit 1; }
TMP="$(mktemp "$STORE/.state.XXXXXX")"
INPUT="$(mktemp "$STORE/.input.XXXXXX")"
trap 'rm -f "$TMP" "$INPUT"' EXIT
# Override transport limits only via explicit adapter flags; no model code execution.
"$PYTHON" "$ROOT/adapters/web.py" --cache "$STORE/cache" --output "$STORE/batch.sexp" "$@"
{
  printf '(web-input 74 '
  if [[ -f "$STORE/state.sexp" ]]; then cat "$STORE/state.sexp"; else printf '()'; fi
  cat "$STORE/batch.sexp"
  printf ')\n'
} > "$INPUT"
"$ROOT/scripts/run.sh" web-ingest < "$INPUT" > "$TMP"
ID="$(date -u +%Y%m%dT%H%M%S%N)-$RANDOM"
cp "$TMP" "$STORE/$ID.sexp"
mv -f "$TMP" "$STORE/state.sexp"
"$ROOT/scripts/run.sh" web-report < "$STORE/state.sexp"
