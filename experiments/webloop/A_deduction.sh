#!/usr/bin/env bash
# A -- DEDUCTION ability: induce the subclass law from kernel-derived pairs.
#
# The transitivity law is never given. The learner sees only ground facts plus
# the pairs the trusted kernel itself derived, must invent the law, and is then
# tested on entities it never trained on. Controls: facts-only (floor), oracle
# law (ceiling), shuffled labels (no signal). The kernel stays the only label
# source; a fabricated rule can never be asserted (reported false-derivations=0).
#
# Usage:
#   ./A_deduction.sh                              # offline cache (n=60, seed=1)
#   ./A_deduction.sh --quick                      # fast smoke test
#   ./A_deduction.sh --online --docs 120 --seed 3 # fetch more, then induce
#   OUT=my.json DEDUCE_EDGES=80 ./A_deduction.sh  # custom report / knobs
#
# Env knobs:
#   DOCS=60 SEED=1 DEDUCE_FOLDS=3 DEDUCE_EDGES=60 DEDUCE_POSITIVES=120 BUDGET=20000
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

DOCS="${DOCS:-60}"
SEED="${SEED:-1}"
DEDUCE_FOLDS="${DEDUCE_FOLDS:-3}"
DEDUCE_EDGES="${DEDUCE_EDGES:-60}"
DEDUCE_POSITIVES="${DEDUCE_POSITIVES:-120}"
BUDGET="${BUDGET:-20000}"

mkdir -p "$HERE/reports"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="${OUT:-$HERE/reports/deduction_${STAMP}.json}"
# an explicit --json on the command line wins over the timestamped default
prev=""
for a in "$@"; do [[ "$prev" == "--json" ]] && OUT="$a"; prev="$a"; done

echo "[A] deduction  docs=$DOCS seed=$SEED folds=$DEDUCE_FOLDS edges=$DEDUCE_EDGES report=$OUT"
python3 -u -m experiments.webloop.run \
  --part deduction \
  --docs "$DOCS" \
  --seed "$SEED" \
  --deduce-folds "$DEDUCE_FOLDS" \
  --deduce-edges "$DEDUCE_EDGES" \
  --deduce-positives "$DEDUCE_POSITIVES" \
  --budget "$BUDGET" \
  --json "$OUT" \
  "$@"
echo "[A] report -> $OUT"