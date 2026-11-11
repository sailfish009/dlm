#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
D="/research/dlm_v0.0204"
exec "${MARU:-$D/maru-compiler}" \
  "$D/src/maru/boot.l" "$D/src/dlm/logic.l" "$D/src/dlm/infer.l" \
  "$D/src/dlm/deduce.l" "$D/src/dlm/fragment.l" "$D/src/dlm/assemble.l" \
  "$D/src/dlm/match.l" "$D/src/dlm/typed.l" "$D/src/dlm/proof.l" \
  "$D/src/dlm/synth.l" "$D/src/dlm/basis.l" "$D/src/dlm/axiom.l" \
  "$D/src/dlm/axiom-graph.l" \
  "$ROOT/src/exp_table.l" "$ROOT/src/fx.l" "$ROOT/src/prior_table.l" \
  "$ROOT/src/data.l" "$ROOT/src/rules218.l" \
  "$D/experiments/mnist_deduce/cases.l" "$ROOT/src/dt.l" "$ROOT/src/learn.l" \
  "$ROOT/src/library_selfsup.l"
