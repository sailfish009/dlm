#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
D="/research/dlm_v0.0204"
exec "${MARU:-$D/maru-compiler}" \
  "$D/src/maru/boot.l" "$D/src/dlm/logic.l" \
  "$ROOT/src/exp_table.l" "$ROOT/src/fx.l" "$ROOT/src/prior_table.l" \
  "$ROOT/src/data.l" "$ROOT/src/rules218.l" \
  "$D/experiments/mnist_deduce/cases.l" "$ROOT/src/dt.l" \
  "$ROOT/src/rulelearn.l"
