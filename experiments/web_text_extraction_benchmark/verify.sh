#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^TEXT 11 EXTRACTED 11$' extraction.out || { echo 'text/extracted mismatch'; exit 1; }
grep -q '^TP 8 FP 3 FN 0$' extraction.out || { echo 'metric mismatch'; exit 1; }
grep -q '^PRECISION 8/11 RECALL 8/8$' extraction.out || { echo 'precision/recall mismatch'; exit 1; }
grep -q '^GATE FACTS 9 RULES 2 PROOF proof$' extraction.out || { echo 'gate mismatch'; exit 1; }
grep -q '^GOLD-FIELDS-IN-INPUT false$' extraction.out || { echo 'gold-field claim missing'; exit 1; }
if grep -Ev '^[[:space:]]*;' data/web_text.l | grep -Eq 'subj|obj|kind|gold'; then echo 'gold/field leakage in input'; exit 1; fi
echo 'TEXT 11 EXTRACTED 11'
echo 'TP 8 FP 3 FN 0'
echo 'PRECISION 8/11 RECALL 8/8'
echo 'GATE FACTS 9 RULES 2 PROOF proof'
echo 'GOLD-FIELDS-IN-INPUT false'
echo 'V0227-WEB-TEXT-EXTRACTION-BENCHMARK-PASS'
