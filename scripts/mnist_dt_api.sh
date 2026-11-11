#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cat "$ROOT/experiments/mnist_maru/data/train.l" \
    "$ROOT/experiments/mnist_deduce/rules.l" \
    "$ROOT/experiments/mnist_deduce/cases.l" \
    "$ROOT/experiments/mnist_dt/rule_ids.l" \
    "$ROOT/experiments/mnist_dt/api.l" > "$ROOT/experiments/mnist_dt/api_all.l"
exec env MARU="${MARU:-$ROOT/maru-compiler}" "$ROOT/scripts/run.sh" proof "$ROOT/experiments/mnist_dt/api_all.l"
