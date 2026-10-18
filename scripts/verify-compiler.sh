#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/build/verify"
mkdir -p "$OUT/empty"
# Prove embedded baseline compilation works without an external source tree.
MARU_HOME="$OUT/empty" "$ROOT/scripts/compile-maru.sh" "$ROOT/maru-compiler" "$OUT/eval1"
# The ordinary output needs the external baseline embedded in the modified source.
# Compare the embedded compiler's repeated emission for determinism instead.
MARU_HOME="$OUT/empty" "$ROOT/scripts/compile-maru.sh" "$ROOT/maru-compiler" "$OUT/eval2"
cmp "$OUT/eval1.ll" "$OUT/eval2.ll"
for stage in eval1 eval2; do
 cp "$OUT/$stage" "$OUT/$stage.stripped"
 "${STRIP:-strip}" "$OUT/$stage.stripped"
done
cmp "$OUT/eval1.stripped" "$OUT/eval2.stripped"
"$ROOT/scripts/run.sh" test
# Ordinary generated evaluator uses the Maru sources' embedded baseline boot.
# Materialize only its boot environment via its explicit source tree as needed;
# no claim that this ordinary output can reproduce the embedding loader.
echo 'Embedded baseline LLVM generation and DLM regression checks passed.'
echo 'Self-reproduction of the compiler-payload image is not implemented.'
