#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARU="${MARU:-$ROOT/maru-compiler}"
# boot.l and compiler baseline dependencies are read from the executable.
cd "$ROOT"
files=(boot.l "$ROOT/src/dlm/kernel.l" "$ROOT/src/dlm/learning.l" "$ROOT/src/dlm/experience.l" "$ROOT/src/dlm/dialogue.l")
case "${1:-repl}" in
 repl) exec "$MARU" "${files[@]}" - ;;
 test) exec "$MARU" "${files[@]}" "$ROOT/tests/demo.l" "$ROOT/tests/kernel-tests.l" "$ROOT/tests/model-tests.l" "$ROOT/tests/safety-tests.l" ;;
 *) echo 'usage: run.sh [repl|test]' >&2; exit 2 ;;
esac
