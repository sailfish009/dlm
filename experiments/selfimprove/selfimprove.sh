#!/usr/bin/env bash
# DLM v0.0056 self-evaluation + weakness-targeted curriculum experiment.
#
# The model is NOT told what to look for.  It reads its own ability off the
# kernel closure (dlm.ability), finds the deduction target it cannot yet
# conclude, asks the web only for the premise it lacks (dlm.curriculum through
# Reader.self_improve), re-closes, re-assesses, and stops on a named reason.
#
# North-star slice: the reader proves `trains` but cannot prove
# `recognizes(<program>, <what>)` until it discovers the `dataset_of` gap itself.
# A synthetic multi-gap theory proves the loop iterates over several weak spots;
# scramble / no-web controls prove the content (not the act) is what helps.
#
# Usage:
#   ./experiments/selfimprove/selfimprove.sh
#   OUTDIR=reports/selfimprove/mine ./experiments/selfimprove/selfimprove.sh
set -euo pipefail
cd "$(dirname "$0")/../.."          # repo root
export PYTHONPATH="${PYTHONPATH:-.}:."
mkdir -p reports/selfimprove

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTDIR="${OUTDIR:-reports/selfimprove/${STAMP}}"
mkdir -p "$OUTDIR"

echo "== self-evaluation + weak-spot curriculum -> $OUTDIR"
python3 -u experiments/selfimprove/run.py --json "$OUTDIR/result.json" "$@"
echo
echo "result: $OUTDIR/result.json"