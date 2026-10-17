#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TREE="${MARU_HOME:-$ROOT/vendor/maru}"
OUT="$TREE/build/llvm-linux/x86_64-unknown-linux-gnu"
"$ROOT/scripts/bootstrap.sh"
cmp "$OUT/eval1" "$OUT/eval2"
(cd "$TREE" && ./build.sh eval0-phase=false default-backend=llvm default-platform=linux test-evaluator)
MARU_HOME="$TREE" MARU="$OUT/eval2" "$ROOT/scripts/run.sh" test
printf '%s\n' 'Compiler checks passed; no runtime was automatically promoted.'
printf 'Candidate runtime: %s\n' "$OUT/eval2"
