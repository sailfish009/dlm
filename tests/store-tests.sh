#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
export STORE="$WORK/store"
"$ROOT/scripts/selfssl.sh" 2 >/dev/null
cp "$STORE/state.sexp" "$WORK/before.sexp"
"$ROOT/scripts/selfssl.sh" 1 >/dev/null
[[ $(find "$STORE" -name '*.sexp' | wc -l) == 4 ]]
# Corrupt the format version, not Lisp code: it must be rejected, not committed.
cp "$STORE/state.sexp" "$WORK/good.sexp"
{ printf '(store 74'; tail -c +10 "$WORK/good.sexp"; } > "$STORE/state.sexp"
cp "$STORE/state.sexp" "$WORK/corrupt.sexp"
if "$ROOT/scripts/selfssl.sh" 1 >"$WORK/rejection.log" 2>&1; then
  echo 'FAIL corrupt store accepted' >&2; exit 1
fi
cmp "$STORE/state.sexp" "$WORK/corrupt.sexp"
awk '{sub(/step 60/, "step 0"); print}' "$WORK/good.sexp" > "$STORE/state.sexp"
cp "$STORE/state.sexp" "$WORK/forged.sexp"
if "$ROOT/scripts/selfssl.sh" 1 >"$WORK/forged.log" 2>&1; then
  echo 'FAIL forged transition accepted' >&2; exit 1
fi
cmp "$STORE/state.sexp" "$WORK/forged.sexp"
echo 'PASS process restart replays experience; corrupt and forged stores rejected without overwrite'
