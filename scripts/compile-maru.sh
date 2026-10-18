#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TREE="${MARU_HOME:-$ROOT/src/maru}"
HOST="${1:-$ROOT/bootstrap/maru-seed}"
OUT="${2:-$ROOT/build/maru/eval1}"
mkdir -p "$(dirname "$OUT")"
HOST="$(realpath "$HOST")"
OUT="$(realpath -m "$OUT")"
TREE="$(realpath "$TREE")"
cd "$TREE"
"$HOST" -O \
  --define '*host-directory*' "$TREE" \
  --define '*slave-directory*' "$TREE" \
  --define '*compiler-backend*' llvm \
  --define target/arch x86_64 --define target/vendor unknown \
  --define target/os linux --define target/abi gnu --define target/platform linux \
  --define feature/profiler/build false \
  --define '+ld.so-path+' /lib64/ld-linux-x86-64.so.2 \
  --define elf-emission-type '' \
  source/bootstrapping/prepare.l boot.l \
  source/bootstrapping/host-ready.l source/bootstrapping/early.l boot.l \
  source/bootstrapping/late.l source/platforms/load-platform.l \
  source/platforms/linux/eval.l source/platforms/run-compiler.l "$OUT.ll"
"${CLANG:-clang}" -O3 -fPIE -nostdlib -nostartfiles -ffreestanding \
  -Wl,-Bstatic,-no-pie -Qunused-arguments "$OUT.ll" -o "$OUT"
