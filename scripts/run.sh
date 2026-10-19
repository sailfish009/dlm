#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARU="${MARU:-$ROOT/maru-compiler}"
# boot.l and compiler baseline dependencies are read from the executable.
cd "$ROOT"
files=(boot.l "$ROOT/src/dlm/kernel.l" "$ROOT/src/dlm/learning.l" "$ROOT/src/dlm/experience.l" "$ROOT/src/dlm/dialogue.l" "$ROOT/src/dlm/interaction.l" "$ROOT/src/dlm/constraints.l" "$ROOT/src/dlm/symbolic-learning.l" "$ROOT/src/dlm/web.l")
case "${1:-repl}" in
 web-ingest) exec "$MARU" "${files[@]}" "$ROOT/experiments/web/ingest.l" ;;
 web-report) exec "$MARU" "${files[@]}" "$ROOT/experiments/web/report.l" ;;
 symbolic) exec "$MARU" "${files[@]}" "$ROOT/experiments/symbolic/run.l" "$ROOT/tests/symbolic-tests.l" "$ROOT/experiments/symbolic/controls.l" ;;
 session) exec "$MARU" "${files[@]}" "$ROOT/experiments/symbolic/data.l" "${2:?session driver required}" ;;
 constraints) exec "$MARU" "${files[@]}" "$ROOT/experiments/constraints/run.l" "$ROOT/tests/constraint-tests.l" ;;
 interaction) exec "$MARU" "${files[@]}" "$ROOT/experiments/interaction/run.l" "$ROOT/tests/interaction-tests.l" ;;
 repl) exec "$MARU" "${files[@]}" - ;;
 test) exec "$MARU" "${files[@]}" "$ROOT/tests/demo.l" "$ROOT/tests/kernel-tests.l" "$ROOT/tests/model-tests.l" "$ROOT/tests/safety-tests.l" "$ROOT/experiments/interaction/run.l" "$ROOT/tests/interaction-tests.l" "$ROOT/experiments/constraints/run.l" "$ROOT/tests/constraint-tests.l" "$ROOT/experiments/symbolic/run.l" "$ROOT/tests/symbolic-tests.l" "$ROOT/experiments/symbolic/controls.l" "$ROOT/tests/web-tests.l" ;;
 *) echo 'usage: run.sh [repl|test|interaction|constraints|symbolic|session|web-ingest|web-report]' >&2; exit 2 ;;
esac
