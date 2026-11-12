#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^DISTINCT-RULES true$' out.txt || { echo 'rules not distinct'; exit 1; }
grep -q '^PATHS 2 OK1 1 OK2 1$' out.txt || { echo 'paths invalid'; exit 1; }
grep -q '^COSTS 2 3 WEIGHTS 21845 16384 Z 38229$' out.txt || { echo 'cost weighting invalid'; exit 1; }
grep -q '^CREDITS 37448 28087 (not 1/count)$' out.txt || { echo 'credit not cost-weighted'; exit 1; }
grep -q '^SINGLE-RULE-INDEX 0 NEG 0 (want 0)$' out.txt || { echo 'negative/single failed'; exit 1; }
echo 'DISTINCT-RULES true'
echo 'PATHS 2 OK1 1 OK2 1'
echo 'COSTS 2 3 WEIGHTS 21845 16384 Z 38229'
echo 'CREDITS 37448 28087 (not 1/count)'
echo 'SINGLE-RULE-INDEX 0 NEG 0'
echo 'V0229-PROOF-PATH-INTEGRAL-REBUILD-PASS'
