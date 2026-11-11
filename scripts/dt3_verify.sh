#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/scripts/dt3_pool5.sh" > "$ROOT/experiments/dt3_pool5/pool5.out" 2>&1
python3 "$ROOT/adapters/pool5_reward.py" "$ROOT/experiments/dt3_pool5/pool5.out"
