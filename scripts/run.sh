#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARU_HOME="${MARU_HOME:-$ROOT/vendor/maru}"
MARU="${MARU:-$ROOT/bootstrap/maru-seed}"
cd "$MARU_HOME"
files=(boot.l "$ROOT/src/kernel.l" "$ROOT/src/learning.l" "$ROOT/src/experience.l" "$ROOT/src/dialogue.l")
case "${1:-repl}" in
  repl) exec "$MARU" "${files[@]}" - ;;
  test) exec "$MARU" "${files[@]}" "$ROOT/tests/demo.l" "$ROOT/tests/kernel-tests.l" "$ROOT/tests/model-tests.l" ;;
  *) echo 'usage: run.sh [repl|test]' >&2; exit 2 ;;
esac
