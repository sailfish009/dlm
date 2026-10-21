#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARU="${MARU:-$ROOT/maru-compiler}"
# boot.l and compiler baseline dependencies are read from the executable.
cd "$ROOT"
files=(boot.l "$ROOT/src/dlm/kernel.l" "$ROOT/src/dlm/learning.l" "$ROOT/src/dlm/experience.l" "$ROOT/src/dlm/dialogue.l" "$ROOT/src/dlm/interaction.l" "$ROOT/src/dlm/constraints.l" "$ROOT/src/dlm/symbolic-learning.l" "$ROOT/src/dlm/web.l" "$ROOT/src/dlm/graph.l" "$ROOT/src/dlm/graph-query.l")
files+=("$ROOT/src/dlm/formula.l" "$ROOT/src/dlm/sequent.l" "$ROOT/src/dlm/sequent-check.l" "$ROOT/src/dlm/countermodel.l" "$ROOT/src/dlm/sequent-search.l" "$ROOT/src/dlm/proof-store.l")
files+=("$ROOT/src/dlm/proof-pattern.l" "$ROOT/src/dlm/nondeterministic.l" "$ROOT/src/dlm/definability.l")
files+=("$ROOT/src/dlm/axiom-space.l" "$ROOT/src/dlm/session-store.l" "$ROOT/src/dlm/repl.l" "$ROOT/src/dlm/reasoning-session.l")
case "${1:-repl}" in
 proof) exec "$MARU" "${files[@]}" "${2:?proof driver required}" ;;
 graph-session) exec "$MARU" "${files[@]}" "$ROOT/experiments/graph/session.l" ;;
 graph-report) exec "$MARU" "${files[@]}" "$ROOT/experiments/graph/report.l" ;;
 graph) exec "$MARU" "${files[@]}" "$ROOT/experiments/graph/run.l" "$ROOT/tests/graph-tests.l" "$ROOT/experiments/graph/transfer.l" ;;
 web-ingest) exec "$MARU" "${files[@]}" "$ROOT/experiments/web/ingest.l" ;;
 web-report) exec "$MARU" "${files[@]}" "$ROOT/experiments/web/report.l" ;;
 symbolic) exec "$MARU" "${files[@]}" "$ROOT/experiments/symbolic/run.l" "$ROOT/tests/symbolic-tests.l" "$ROOT/experiments/symbolic/controls.l" ;;
 session) exec "$MARU" "${files[@]}" "$ROOT/experiments/symbolic/data.l" "${2:?session driver required}" ;;
 constraints) exec "$MARU" "${files[@]}" "$ROOT/experiments/constraints/run.l" "$ROOT/tests/constraint-tests.l" ;;
 interaction) exec "$MARU" "${files[@]}" "$ROOT/experiments/interaction/run.l" "$ROOT/tests/interaction-tests.l" ;;
 repl) exec "$MARU" "${files[@]}" - ;;
 reason)
  STORE="${2:-$ROOT/experiments/repl/store/reasoning78.sexp}"
  mkdir -p "$(dirname "$STORE")"
  exec "$MARU" "${files[@]}" --define '*dlm-session-path*' "$STORE" "$ROOT/experiments/repl/reasoning.l" - ;;
 learn)
  STORE="${2:-$ROOT/experiments/repl/store/state.sexp}"
  DEMO="${3:-false}"
  [[ "$DEMO" == true || "$DEMO" == false ]] || { echo 'demo flag must be true/false' >&2; exit 2; }
  mkdir -p "$(dirname "$STORE")"
  exec "$MARU" "${files[@]}" --define '*dlm-session-path*' "$STORE" --define '*dlm-demo-mode*' "$DEMO" "$ROOT/experiments/repl/start.l" - ;;
 test) exec "$MARU" "${files[@]}" "$ROOT/tests/demo.l" "$ROOT/tests/kernel-tests.l" "$ROOT/tests/model-tests.l" "$ROOT/tests/safety-tests.l" "$ROOT/experiments/interaction/run.l" "$ROOT/tests/interaction-tests.l" "$ROOT/experiments/constraints/run.l" "$ROOT/tests/constraint-tests.l" "$ROOT/experiments/symbolic/run.l" "$ROOT/tests/symbolic-tests.l" "$ROOT/experiments/symbolic/controls.l" "$ROOT/tests/web-tests.l" "$ROOT/experiments/graph/run.l" "$ROOT/tests/graph-tests.l" "$ROOT/experiments/graph/transfer.l" "$ROOT/tests/sequent-tests.l" "$ROOT/tests/axiom-space-tests.l" "$ROOT/tests/reasoning-tests.l" ;;
 *) echo 'usage: run.sh [proof DRIVER|repl|learn|reason|test|interaction|constraints|symbolic|session|web-ingest|web-report|graph|graph-session|graph-report]' >&2; exit 2 ;;
esac
