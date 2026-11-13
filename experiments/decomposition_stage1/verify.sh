#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^WEB 15 SPANS 894 PREDS-FULL 11 PREDS-WEB 1$' stage1.out || { echo 'stage1 span shape changed'; exit 1; }
grep -q '^GOLD 22 CANDIDATE-SPACE-FULL 8791596$' stage1.out || { echo 'stage1 candidate space changed'; exit 1; }
grep -q '^PRED-COVERAGE-FULL 22/22 PRED-COVERAGE-WEB 6/22$' stage1.out || { echo 'predicate coverage changed'; exit 1; }
grep -q '^SPAN-COVERAGE 11/22$' stage1.out || { echo 'span coverage regressed'; exit 1; }
grep -q '^CANDIDATE-RECALL-FULL 11/22 CANDIDATE-RECALL-WEB 5/22$' stage1.out || { echo 'candidate recall regressed'; exit 1; }
grep -q '^ORACLE-SPAN-PRED 22/22 (upper bound)$' stage1.out || { echo 'oracle upper bound changed'; exit 1; }
echo 'M4-SPAN-COVERAGE 11/22'
echo 'M4-CANDIDATE-RECALL 11/22 WEB 5/22'
echo 'M4-ORACLE-UPPER-BOUND 22/22'
echo 'M4-NO-RANKER-TRAINING-BEFORE-RECALL yes'
echo 'V0238-M4-GENERATION-PASS'
