#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
(cd proof_path_integral_rebuild && ./run.sh > out.txt && ./verify.sh)
(cd prior_decorrelated_matrix && ./run_prior0.sh && ./verify.sh)
echo V0229-INTEGRAL-REBUILD-ALL-PASS
