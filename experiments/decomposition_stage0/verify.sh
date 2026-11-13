#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^WEB 15 SPANS 39 PREDS-FULL 11 PREDS-WEB 1$' stage0.out || { echo 'stage0 shape changed'; exit 1; }
grep -q '^GOLD 22 CANDIDATE-SPACE-FULL 16731$' stage0.out || { echo 'candidate space changed'; exit 1; }
grep -q '^PRED-COVERAGE-FULL 22/22 PRED-COVERAGE-WEB 6/22$' stage0.out || { echo 'predicate coverage changed'; exit 1; }
grep -q '^SPAN-COVERAGE 0/22$' stage0.out || { echo 'span coverage changed'; exit 1; }
grep -q '^CANDIDATE-RECALL-FULL 0/22 CANDIDATE-RECALL-WEB 0/22$' stage0.out || { echo 'candidate recall changed'; exit 1; }
grep -q '^ORACLE-SPAN-PRED 22/22 (upper bound)$' stage0.out || { echo 'oracle upper bound changed'; exit 1; }
echo 'PRED-COVERAGE-FULL 22/22 PRED-COVERAGE-WEB 6/22'
echo 'SPAN-COVERAGE 0/22'
echo 'CANDIDATE-RECALL-FULL 0/22 CANDIDATE-RECALL-WEB 0/22'
echo 'ORACLE-SPAN-PRED 22/22'
echo 'V0235-DECOMPOSITION-STAGE0-PASS'
