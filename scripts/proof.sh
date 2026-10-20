#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROBLEM="${1:-$ROOT/experiments/proof/problem.sexp}"
BUDGET="${2:-1000}"
STORE="${STORE:-$ROOT/experiments/proof/store}"
[[ "$BUDGET" =~ ^[0-9]+$ ]] && (( BUDGET <= 9000 )) || { echo 'budget must be 0..9000' >&2; exit 2; }
mkdir -p "$STORE"
exec 9>"$STORE/lock"
flock -n 9 || { echo 'proof store is in use' >&2; exit 1; }
TMP="$(mktemp "$STORE/.state.XXXXXX")"
INPUT="$(mktemp "$STORE/.input.XXXXXX")"
trap 'rm -f "$TMP" "$INPUT"' EXIT
# Normalize with the data reader; shell metadata is not an executable Lisp form.
HASH="$("$ROOT/scripts/run.sh" proof "$ROOT/experiments/proof/normalize.l" < "$PROBLEM" | sha256sum | cut -d' ' -f1)"
if [[ -f "$STORE/state.sexp" ]]; then "$ROOT/scripts/proof-verify.sh" "$STORE/state.sexp" >/dev/null; fi
{
 printf '(proof-request-v1 '
 if [[ -f "$STORE/state.sexp" ]]; then cat "$STORE/state.sexp"; else printf '()'; fi
 cat "$PROBLEM"
 printf ' %s "input-file-sha256:%s" "%s")\n' "$BUDGET" "$(sha256sum "$PROBLEM" | cut -d' ' -f1)" "$HASH"
} > "$INPUT"
"$ROOT/scripts/run.sh" proof "$ROOT/experiments/proof/session.l" < "$INPUT" > "$TMP"
REPORT="$("$ROOT/scripts/proof-verify.sh" "$TMP")"
ID="$(date -u +%Y%m%dT%H%M%S%N)-$RANDOM"
cp "$TMP" "$STORE/$ID.sexp"
mv -f "$TMP" "$STORE/state.sexp"
printf '%s\n' "$REPORT"
