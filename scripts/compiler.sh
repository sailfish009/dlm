#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOL="$ROOT/src/maru/tools-for-build/build-compiler-image.sh"
MODE="${1:-}"; shift || true
case "$MODE" in
 rebuild|reproduce)
  ID="$(date -u +%Y%m%dT%H%M%SZ)-$RANDOM"
  DIR="$ROOT/runtime/releases/$ID"; mkdir -p "$DIR"
  PARENT="$(sha256sum "$ROOT/maru-compiler" | cut -d' ' -f1)"
  (cd "$ROOT"; find src -type f -print0 | sort -z | xargs -0 sha256sum) > "$DIR/sources.sha256"
  if [[ "$MODE" == rebuild ]]; then
   "$TOOL" "$ROOT/bootstrap/maru-seed" "$DIR/maru" > "$DIR/build.log" 2>&1
  else
   "$TOOL" --self "$ROOT/maru-compiler" "$DIR/maru" > "$DIR/build.log" 2>&1
  fi
  printf 'mode=%s\nparent_sha256=%s\n' "$MODE" "$PARENT" > "$DIR/record"
  (cd "$DIR"; sha256sum maru maru.ll sources.sha256 record) > "$DIR/artifacts.sha256"
  echo "$ID" ;;
 verify)
  ID="${1:?release ID required}"
  [[ "$ID" =~ ^[A-Za-z0-9_-]+$ ]] || exit 2
  DIR="$ROOT/runtime/releases/$ID"
  (cd "$DIR"; sha256sum -c artifacts.sha256) > "$DIR/verify.log" 2>&1
  MARU="$DIR/maru" "$ROOT/scripts/run.sh" test >> "$DIR/verify.log" 2>&1
  "$TOOL" --self "$DIR/maru" "$DIR/next" >> "$DIR/verify.log" 2>&1
  cmp "$DIR/maru.ll" "$DIR/next.ll" >> "$DIR/verify.log" 2>&1
  cp "$DIR/maru" "$DIR/maru.stripped"; cp "$DIR/next" "$DIR/next.stripped"
  strip "$DIR/maru.stripped" "$DIR/next.stripped"
  cmp "$DIR/maru.stripped" "$DIR/next.stripped" >> "$DIR/verify.log" 2>&1
  (cd "$ROOT"; sha256sum src/dlm/*.l tests/*.l experiments/interaction/*.l scripts/run.sh) > "$DIR/tests.sha256"
  (cd "$DIR"; sha256sum artifacts.sha256 tests.sha256 verify.log) > "$DIR/verified"
  echo "Verified: $ID" ;;
 promote)
  ID="${1:?release ID required}"
  [[ "$ID" =~ ^[A-Za-z0-9_-]+$ ]] || exit 2
  DIR="$ROOT/runtime/releases/$ID"
  (cd "$DIR"; sha256sum -c verified; sha256sum -c artifacts.sha256) >/dev/null
  (cd "$ROOT"; sha256sum -c "$DIR/tests.sha256") >/dev/null
  if grep -qx 'mode=rebuild' "$DIR/record"; then
   CURRENT="$(mktemp)"
   (cd "$ROOT"; find src -type f -print0 | sort -z | xargs -0 sha256sum) > "$CURRENT"
   if ! cmp -s "$CURRENT" "$DIR/sources.sha256"; then
    rm -f "$CURRENT"; echo 'Source changed since candidate build' >&2; exit 1
   fi
   rm -f "$CURRENT"
  fi
  [[ -L "$ROOT/maru-compiler" ]] || { echo 'Active runtime must be a symlink' >&2; exit 1; }
  OLD="$(readlink "$ROOT/maru-compiler")"
  ln -s "$OLD" "$ROOT/runtime/previous.new"; mv -Tf "$ROOT/runtime/previous.new" "$ROOT/runtime/previous"
  ln -s "runtime/releases/$ID/maru" "$ROOT/maru-compiler.new"
  mv -Tf "$ROOT/maru-compiler.new" "$ROOT/maru-compiler"
  echo "Promoted: $ID" ;;
 rollback)
  OLD="$(readlink "$ROOT/runtime/previous")"
  [[ -x "$ROOT/$OLD" ]] || exit 1
  ln -s "$OLD" "$ROOT/maru-compiler.new"; mv -Tf "$ROOT/maru-compiler.new" "$ROOT/maru-compiler"
  echo 'Rolled back to previous runtime' ;;
 *) echo 'usage: compiler.sh rebuild|reproduce|verify ID|promote ID|rollback' >&2; exit 2 ;;
esac
