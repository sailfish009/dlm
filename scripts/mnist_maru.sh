#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cat "$ROOT/experiments/mnist_maru/data/train.l" \
    "$ROOT/experiments/mnist_maru/data/test.l" \
    "$ROOT/experiments/mnist_maru/train.l" > "$ROOT/experiments/mnist_maru/all.l"
exec env MARU="${MARU:-$ROOT/maru-compiler}" "$ROOT/scripts/run.sh" proof "$ROOT/experiments/mnist_maru/all.l"
