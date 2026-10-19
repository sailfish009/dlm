#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="$(realpath "${MARU:-$ROOT/maru-compiler}")"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
(cd "$WORK"; printf '%s\n' \
  '(print "CHOICES=" (symbolic-length (symbolic-choose (quote ((x (a b)))) (quote x))))' \
  '(print "SOLUTIONS=" (symbolic-length (symbolic-nth (symbolic-solutions (quote ((x (a b)) (y (a b)))) (quote ((neq x y))) 100) 2)))' \
  | "$IMAGE" boot.l -) > "$WORK/runtime.log" 2>&1
grep -q 'CHOICES=2' "$WORK/runtime.log"
grep -q 'SOLUTIONS=2' "$WORK/runtime.log"
echo 'PASS source-free embedded symbolic choice/backtracking/propagation'
