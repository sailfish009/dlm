#!/usr/bin/env bash
# B -- CONVERSATION ability: sentence <-> relation, kernel-gated.
#
# An IR reader maps a sentence to the right relation and a realizer maps a
# relation back to a sentence; entity-level K-fold, cue ablation, surface and
# majority baselines, a scrambled-label control, and an invented-predicate
# control that proves the harness actually has signal. Reading is only accepted
# where the kernel entails it; the kernel never asserts on its behalf.
#
# Usage:
#   ./B_conversation.sh                            # offline cache (n=60, seed=1)
#   ./B_conversation.sh --quick                    # fast smoke test
#   ./B_conversation.sh --online --docs 120 --seed 3
#   OUT=my.json FOLDS=5 EPOCHS=50 ./B_conversation.sh
#
# Env knobs:
#   DOCS=60 SEED=1 FOLDS=4 EPOCHS=30 REALIZER_EPOCHS=10 REALIZER_ATOMS=60
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

DOCS="${DOCS:-60}"
SEED="${SEED:-1}"
FOLDS="${FOLDS:-4}"
EPOCHS="${EPOCHS:-30}"
REALIZER_EPOCHS="${REALIZER_EPOCHS:-10}"
REALIZER_ATOMS="${REALIZER_ATOMS:-60}"

mkdir -p "$HERE/reports"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="${OUT:-$HERE/reports/conversation_${STAMP}.json}"
# an explicit --json on the command line wins over the timestamped default
prev=""
for a in "$@"; do [[ "$prev" == "--json" ]] && OUT="$a"; prev="$a"; done

echo "[B] conversation  docs=$DOCS seed=$SEED folds=$FOLDS epochs=$EPOCHS report=$OUT"
python3 -u -m experiments.webloop.run \
  --part conversation \
  --docs "$DOCS" \
  --seed "$SEED" \
  --folds "$FOLDS" \
  --epochs "$EPOCHS" \
  --realizer-epochs "$REALIZER_EPOCHS" \
  --realizer-atoms "$REALIZER_ATOMS" \
  --json "$OUT" \
  "$@"
echo "[B] report -> $OUT"