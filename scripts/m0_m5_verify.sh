#!/usr/bin/env bash
# Master roadmap verification: M0–M5 + tree release regression.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo '== M0 =='
(cd experiments/dt_kernel_m0 && ./run_m0.sh >/tmp/m0_run.log 2>&1 && ./verify_m0.sh)

echo '== M1 =='
(cd experiments/m1_proof_state && ./run_m1.sh)

echo '== M2 =='
(cd experiments/m1_proof_state && ./run_m2.sh)

echo '== M3 =='
(cd experiments/m3_selfssl && ./run_m3.sh)

echo '== M4 (separate track) =='
(cd experiments/decomposition_stage1 && ./run_all.sh >/tmp/m4_run.log 2>&1 && ./verify.sh)

echo '== M5 (conditional) =='
(cd experiments/m5_constrained_proposal && ./run_m5.sh)

echo '== tree release regression =='
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh | tail -3

echo 'M0-M5-VERIFY-PASS'
