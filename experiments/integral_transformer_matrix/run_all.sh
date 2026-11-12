#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run_matrix.sh
./verify.sh
(cd training && ./run_credit.sh && ./verify_credit.sh)
(cd proof_path && ./run.sh > out.txt && ./verify.sh)
echo V0228-INTEGRAL-MATRIX-ALL-PASS
