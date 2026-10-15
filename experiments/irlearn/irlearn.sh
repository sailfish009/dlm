#!/usr/bin/env bash
# DLM v0.0058 -- the IR-TREE is ONE medium: deduction improves on it, Lisp reads it.
#
# The model PERCEIVES its own source as IR forms, INDUCES the governing
# composition law AS a form, RECURSIVELY reifies each certified extension as the
# next predicate's forms until it recovers reachability, and then the SAME tree is
# read/evaluated/written by Lisp -- the recursion is executed through Lisp's own
# eval_form/findall and its conclusions are checked equal to the kernel's.
#
# Usage:
#   ./experiments/irlearn/irlearn.sh
#   ./experiments/irlearn/irlearn.sh --rounds 8
#   OUTDIR=reports/irlearn/mine ./experiments/irlearn/irlearn.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTDIR="${OUTDIR:-reports/irlearn/${STAMP}}"
mkdir -p "$OUTDIR"

echo "== one IR-TREE medium: deduction improves on it, Lisp reads it -> $OUTDIR"
python3 -u "$HERE/run.py" --json "$OUTDIR/result.json" "$@"
echo
echo "result: $OUTDIR/result.json"