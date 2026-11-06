#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARU="${MARU:-$ROOT/maru-compiler}"
cd "$ROOT"
files=(boot.l
  "$ROOT/src/dlm/d107-util.l" "$ROOT/src/dlm/d107-form.l" "$ROOT/src/dlm/d107-close.l"
  "$ROOT/src/dlm/d107-def.l"
  "$ROOT/src/dlm/d107-session.l" "$ROOT/src/dlm/d107-plan.l" "$ROOT/src/dlm/d107-learn.l"
  "$ROOT/src/dlm/d107-read.l" "$ROOT/src/dlm/d107-agenda.l"
  "$ROOT/src/dlm/d107-command.l")
case "${1:-repl}" in
  repl) exec "$MARU" "${files[@]}" - ;;
  proof) exec "$MARU" "${files[@]}" "${2:?driver required}" ;;
  northstar) exec "$MARU" "${files[@]}" "$ROOT/experiments/northstar/run.l" ;;
  test) exec "$MARU" "${files[@]}" "$ROOT/tests/core-tests.l" ;;
  *) echo "usage: run.sh [repl|proof DRIVER|northstar|test]" >&2; exit 2 ;;
esac
