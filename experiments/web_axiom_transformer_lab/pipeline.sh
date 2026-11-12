#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 proposer.py > proposer.out
./run_gate.sh > gate.out
python3 verify_web.py
