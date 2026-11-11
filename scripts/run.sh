#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARU="${MARU:-$ROOT/maru-compiler}"
cd "$ROOT"
files=("$ROOT/src/maru/boot.l" "$ROOT/src/dlm/logic.l" "$ROOT/src/dlm/infer.l" "$ROOT/src/dlm/deduce.l" "$ROOT/src/dlm/fragment.l" "$ROOT/src/dlm/assemble.l" "$ROOT/src/dlm/match.l" "$ROOT/src/dlm/typed.l" "$ROOT/src/dlm/proof.l" "$ROOT/src/dlm/synth.l" "$ROOT/src/dlm/basis.l" "$ROOT/src/dlm/axiom.l" "$ROOT/src/dlm/axiom-graph.l" "$ROOT/src/dlm/dtir.l" "$ROOT/src/dlm/mlir.l" "$ROOT/src/dlm/graph-ir.l" "$ROOT/src/dlm/nl.l" "$ROOT/src/dlm/web.l" "$ROOT/src/dlm/selfssl.l" "$ROOT/src/dlm/repl.l")
case "${1:-repl}" in
  repl) exec "$MARU" "${files[@]}" - ;;
  experiment) exec "$MARU" "${files[@]}" "$ROOT/experiments/fragment_repl/start.l" - ;;
  mlir) exec "$MARU" "${files[@]}" "$ROOT/experiments/mlir_repl/start.l" - ;;
  typed) exec "$MARU" "${files[@]}" "$ROOT/experiments/typed_repl/start.l" - ;;
  synth) exec "$MARU" "${files[@]}" "$ROOT/experiments/synth_repl/start.l" - ;;
  proof) exec "$MARU" "${files[@]}" "${2:?driver required}" ;;
  proof-extra) exec "$MARU" "${files[@]}" "${2:?extra file required}" "${3:?driver required}" ;;
  test) exec "$MARU" "${files[@]}" "$ROOT/tests/core-tests.l" ;;
  *) echo "usage: run.sh [repl|experiment|proof DRIVER|test]" >&2; exit 2 ;;
esac
