#!/usr/bin/env bash
# DLM v0.0042 north-star slice: acquire the PyTorch MNIST example, REDUCE it to
# function-free Horn facts, look the used library symbols UP ON THE WEB and reduce
# their definitions to `meaning(symbol, concept)` facts, LEARN a call rule from the
# reduction, derive an understanding set through the trusted kernel, emit it as an
# IR form, and gloss it into verified natural-language sentences.
#
# Usage:
#   ./experiments/mnist/mnist.sh                 # fetch (or reuse cache)
#   ./experiments/mnist/mnist.sh --offline       # replay from cache, no network
#   ./experiments/mnist/mnist.sh --local path.py # use a local file
#   OUTDIR=reports/mnist/mine ./experiments/mnist/mnist.sh
#
# Writes reports/mnist/<stamp>/result.json (IR form + narrative + proofs).
set -euo pipefail
cd "$(dirname "$0")/../.."          # repo root
export PYTHONPATH="${PYTHONPATH:-.}:."
python3 -u experiments/mnist/run.py "$@"