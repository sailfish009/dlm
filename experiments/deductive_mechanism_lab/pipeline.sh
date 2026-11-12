#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run.sh > mechanism.out
python3 verify_mechanism.py
