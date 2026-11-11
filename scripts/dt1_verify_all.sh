#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo '=== E14 candidate ablation ==='
python3 experiments/dt1_candidate/run.py
echo '=== E15 verifier proxy ==='
python3 experiments/dt1_verifier_proxy/run.py | tail -3
