#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run_full.sh
./run_train.sh
echo V0218-DT-FULL-NO-MLIR-PASS
