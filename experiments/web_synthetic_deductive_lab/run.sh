#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
D="$(cd "$ROOT/../.." && pwd)"
exec "${MARU:-$D/maru-compiler}" \
  "$D/src/maru/boot.l" "$D/src/dlm/logic.l" "$D/src/dlm/infer.l" \
  "$D/src/dlm/deduce.l" "$D/src/dlm/fragment.l" "$D/src/dlm/assemble.l" \
  "$D/src/dlm/match.l" "$D/src/dlm/typed.l" "$D/src/dlm/proof.l" \
  "$D/src/dlm/synth.l" "$D/src/dlm/basis.l" "$D/src/dlm/axiom.l" \
  "$D/src/dlm/axiom-graph.l" "$D/src/dlm/nl.l" "$D/src/dlm/web.l" \
  "$ROOT/data/web_text.l" "$ROOT/src/lab.l"
