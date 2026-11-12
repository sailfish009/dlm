#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^WEB TEXT 11 RECORDS 11 WEB-FACTS 9 WEB-RULES 2$' lab.out || { echo 'web extraction changed'; exit 1; }
grep -q '^SCHEMA isa/2 SYNTH-TRAIN 5 SYNTH-TEST 6$' lab.out || { echo 'synthetic split changed'; exit 1; }
grep -q '^BASELINE 0/2 LEARNED 1$' lab.out || { echo 'baseline/learning changed'; exit 1; }
grep -q '^AFTER 2/2 NEG 0 (want 0) SCRAMBLE 0/2$' lab.out || { echo 'post-learning gate changed'; exit 1; }
echo 'WEB TEXT 11 WEB-FACTS 9 WEB-RULES 2'
echo 'SYNTH TRAIN 5 TEST 6'
echo 'BASELINE 0/2 -> AFTER 2/2'
echo 'NEG 0 SCRAMBLE 0/2'
echo 'V0230-WEB-SYNTHETIC-DEDUCTIVE-PASS'
