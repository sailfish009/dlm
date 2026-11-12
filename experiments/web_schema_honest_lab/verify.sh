#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^WEB TEXT 11 RECORDS 11 SCHEMA isa/2 has-web$' lab.out || { echo 'schema not web-derived'; exit 1; }
grep -q '^SYNTH TRAIN 5 TEST 6 TEST-GOALS 2$' lab.out || { echo 'split changed'; exit 1; }
grep -q '^BASELINE 0/2 TEMPLATE 2/2 LEARNED 1 AFTER 2/2$' lab.out || { echo 'learning gate changed'; exit 1; }
grep -q '^CANDIDATES 2 TRANS-NEG 0 SYM-NEG 1 (want 0 0) RENAME 2/2 DESTROY 0/2$' lab.out || { echo 'controls changed'; exit 1; }
grep -q '^WEB TEXT 0 RECORDS 0 SCHEMA none/2 no-web$' noweb.out || { echo 'empty-web schema changed'; exit 1; }
grep -q '^SYNTH TRAIN 0 TEST 0 TEST-GOALS 0$' noweb.out || { echo 'empty-web dataset not empty'; exit 1; }
echo 'SCHEMA isa/2 (derived)'
echo 'BASELINE 0/2 TEMPLATE 2/2 AFTER 2/2'
echo 'NEG trans=0 sym=1 (sym rejected)'
echo 'RENAME 2/2 DESTROY 0/2'
grep -q '^ORACLE PROVED 9/15 NEG 0 (want 0)$' oracle.out || { echo 'oracle changed'; exit 1; }
echo 'NO-WEB SCHEMA none, SYNTH 0'
echo 'ORACLE PROVED 9/15 NEG 0'
echo 'V0231-WEB-SCHEMA-HONEST-PASS'
