#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cat "$ROOT/experiments/mnist_maru/data/train.l" \
    "$ROOT/experiments/mnist_deduce/rules.l" \
    "$ROOT/experiments/proof_rl_dlm/decoys.l" \
    "$ROOT/experiments/mnist_deduce/cases.l" \
    "$ROOT/experiments/proof_rl_dlm/rule_ids218.l" \
    "$ROOT/experiments/mnist_dt/api.l" \
    "$ROOT/experiments/proof_rl_dlm/singleton.l" > "$ROOT/experiments/proof_rl_dlm/p1_all.l"
exec env MARU="${MARU:-$ROOT/maru-compiler}" "$ROOT/scripts/run.sh" proof "$ROOT/experiments/proof_rl_dlm/p1_all.l"
