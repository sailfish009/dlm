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
files+=("$ROOT/src/dlm/space.l" "$ROOT/src/dlm/space-execution.l" "$ROOT/src/dlm/space-learning.l" "$ROOT/src/dlm/space-definitions.l" "$ROOT/src/dlm/space-session.l")
files+=("$ROOT/src/dlm/ground-space.l" "$ROOT/src/dlm/ground-session.l" "$ROOT/src/dlm/ground-bridge.l")
files+=("$ROOT/src/dlm/search-control.l" "$ROOT/src/dlm/search-session.l" "$ROOT/src/dlm/recursive86.l")
files+=("$ROOT/src/dlm/contracts87-ir.l" "$ROOT/src/dlm/contracts87-check.l" "$ROOT/src/dlm/contracts87-runtime.l")
files+=("$ROOT/src/dlm/contracts88-curriculum.l" "$ROOT/src/dlm/contracts88-session.l")
files+=("$ROOT/src/dlm/basis90-ir.l" "$ROOT/src/dlm/basis90-rewrite.l" "$ROOT/src/dlm/basis90-discover.l")
files+=("$ROOT/src/dlm/basis90-check.l" "$ROOT/src/dlm/basis90-execution.l" "$ROOT/src/dlm/basis90-session.l")
case "${1:-repl}" in
 proof) exec "$MARU" "${files[@]}" "${2:?proof driver required}" ;;
 basis90) exec "$MARU" "${files[@]}" "$ROOT/experiments/basis90/run.l" ;;
 basis90-input) exec "$MARU" "${files[@]}" "$ROOT/experiments/basis90/input.l" ;;
 graph-session) exec "$MARU" "${files[@]}" "$ROOT/experiments/graph/session.l" ;;
 graph-report) exec "$MARU" "${files[@]}" "$ROOT/experiments/graph/report.l" ;;
 graph) exec "$MARU" "${files[@]}" "$ROOT/experiments/graph/run.l" "$ROOT/tests/graph-tests.l" "$ROOT/experiments/graph/transfer.l" ;;
 web-ingest) exec "$MARU" "${files[@]}" "$ROOT/experiments/web/ingest.l" ;;
 web-report) exec "$MARU" "${files[@]}" "$ROOT/experiments/web/report.l" ;;
 symbolic) exec "$MARU" "${files[@]}" "$ROOT/experiments/symbolic/run.l" "$ROOT/tests/symbolic-tests.l" "$ROOT/experiments/symbolic/controls.l" ;;
 session) exec "$MARU" "${files[@]}" "$ROOT/experiments/symbolic/data.l" "${2:?session driver required}" ;;
 constraints) exec "$MARU" "${files[@]}" "$ROOT/experiments/constraints/run.l" "$ROOT/tests/constraint-tests.l" ;;
 interaction) exec "$MARU" "${files[@]}" "$ROOT/experiments/interaction/run.l" "$ROOT/tests/interaction-tests.l" ;;
 recursive86)
  STORE="${2:?snapshot path required}"
  DEMO="${3:-false}"; ROUNDS="${4:-0}"; INTERVAL="${5:-1000}"; BUDGET="${6:-8}"
  [[ "$DEMO" == true || "$DEMO" == false ]] || exit 2
  [[ "$ROUNDS" =~ ^(0|[1-9][0-9]{0,4})$ && "$INTERVAL" =~ ^(0|[1-9][0-9]{0,4})$ && "$BUDGET" =~ ^(0|[1-9][0-9]{0,4})$ ]] || exit 2
  (( ROUNDS <= 1000 && INTERVAL >= 20 && INTERVAL <= 60000 && BUDGET >= 1 && BUDGET <= 16 )) || exit 2
  CONTRACTS_DEMO="${7:-false}"; CONTRACT_BATCH="${8:-0}"; CONTRACT_FUEL="${9:-0}"; BUDGET_SET="${10:-false}"; CURRICULUM="${11:-0}"
  [[ "$CONTRACTS_DEMO" == true || "$CONTRACTS_DEMO" == false ]] || exit 2
  [[ "$BUDGET_SET" == true || "$BUDGET_SET" == false ]] || exit 2
  [[ "$CONTRACT_BATCH" =~ ^(0|[1-9][0-9]{0,1})$ && "$CONTRACT_FUEL" =~ ^(0|[1-9][0-9]{0,5})$ && "$CURRICULUM" =~ ^[0-3]$ ]] || exit 2
  (( CONTRACT_BATCH <= 16 && CONTRACT_FUEL <= 200000 )) || exit 2
  mkdir -p "$(dirname "$STORE")"
  tail=(); if (( ROUNDS == 0 )); then tail=(-); fi
  exec "$MARU" "${files[@]}" --define '*dlm-session-path*' "$STORE" --define '*r86-demo*' "$DEMO" \
    --define '*r86-rounds*' "$ROUNDS" --define '*r86-interval*' "$INTERVAL" --define '*r86-budget*' "$BUDGET" \
    --define '*r88-contracts-demo*' "$CONTRACTS_DEMO" --define '*r88-contract-batch*' "$CONTRACT_BATCH" \
    --define '*r88-contract-fuel*' "$CONTRACT_FUEL" --define '*r88-budget-set*' "$BUDGET_SET" --define '*r88-mode*' "$CURRICULUM" \
    "$ROOT/experiments/repl/recursive86.l" "${tail[@]}" ;;
 repl) exec "$MARU" "${files[@]}" - ;;
 space)
  STORE="${2:-$ROOT/experiments/repl/store/space79.sexp}"
  mkdir -p "$(dirname "$STORE")"
  exec "$MARU" "${files[@]}" --define '*dlm-session-path*' "$STORE" "$ROOT/experiments/repl/space.l" - ;;
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
 test) exec "$MARU" "${files[@]}" "$ROOT/tests/demo.l" "$ROOT/tests/kernel-tests.l" "$ROOT/tests/model-tests.l" "$ROOT/tests/safety-tests.l" "$ROOT/experiments/interaction/run.l" "$ROOT/tests/interaction-tests.l" "$ROOT/experiments/constraints/run.l" "$ROOT/tests/constraint-tests.l" "$ROOT/experiments/symbolic/run.l" "$ROOT/tests/symbolic-tests.l" "$ROOT/experiments/symbolic/controls.l" "$ROOT/tests/web-tests.l" "$ROOT/experiments/graph/run.l" "$ROOT/tests/graph-tests.l" "$ROOT/experiments/graph/transfer.l" "$ROOT/tests/sequent-tests.l" "$ROOT/tests/axiom-space-tests.l" "$ROOT/tests/reasoning-tests.l" "$ROOT/tests/space-tests.l" ;;
 *) echo 'usage: run.sh [basis90|basis90-input|proof DRIVER|repl|learn|reason|space|recursive86 STORE DEMO ROUNDS INTERVAL BUDGET|test|interaction|constraints|symbolic|session|web-ingest|web-report|graph|graph-session|graph-report]' >&2; exit 2 ;;
esac
