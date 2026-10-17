#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TREE="${MARU_HOME:-$ROOT/vendor/maru}"
# Maru's bootstrap needs historical stages, not only current Lisp sources.
if [[ ! -d "$TREE/.git" ]]; then
  git init -q "$TREE"
  git -C "$TREE" fetch -q "$ROOT/bootstrap/maru.bundle" \
    refs/heads/maru.11:refs/heads/maru.11 \
    refs/heads/maru.10:refs/heads/maru.10
  git -C "$TREE" symbolic-ref HEAD refs/heads/maru.11
  git -C "$TREE" reset --mixed -q HEAD
fi
cd "$TREE"
# Compile the working sources, not the cached committed eval0 checkout.
exec ./build.sh eval0-phase=false bootstrap llvm linux
