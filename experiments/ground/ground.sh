#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
PYTHONPATH=. python experiments/ground/run.py