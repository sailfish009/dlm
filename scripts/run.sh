#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARU="${MARU:-$ROOT/maru-compiler}"
cd "$ROOT"
files=(boot.l
  "$ROOT/src/dlm/d107-util.l" "$ROOT/src/dlm/d107-form.l" "$ROOT/src/dlm/d107-close.l" "$ROOT/src/dlm/d107-match.l" "$ROOT/src/dlm/d107-contract.l"
  "$ROOT/src/dlm/d107-def.l" "$ROOT/src/dlm/d107-surface.l"
  "$ROOT/src/dlm/d107-session.l" "$ROOT/src/dlm/d107-plan.l" "$ROOT/src/dlm/d107-learn.l"
  "$ROOT/src/dlm/d107-read.l" "$ROOT/src/dlm/d107-agenda.l"
  "$ROOT/src/dlm/d107-command.l")
case "${1:-repl}" in
  repl) exec "$MARU" "${files[@]}" - ;;
  proof) exec "$MARU" "${files[@]}" "${2:?driver required}" ;;
  northstar) exec "$MARU" "${files[@]}" "$ROOT/experiments/northstar/run.l" ;;
  test)
    log="$(mktemp)"
    "$MARU" "${files[@]}" "$ROOT/tests/core-tests.l" | tee "$log"
    if grep -q ALL-CORE-TESTS-PASSED "$log" && ! grep -q FAIL "$log"; then rm -f "$log"; exit 0; fi
    rm -f "$log"; exit 1 ;;
  *) echo "usage: run.sh [repl|proof DRIVER|northstar|test]" >&2; exit 2 ;;
esac
