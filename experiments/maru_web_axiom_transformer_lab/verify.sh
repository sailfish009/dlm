#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^TRANSFORMER_TOP1 0/4$' lab.out || { echo transformer expectation changed; exit 1; }
grep -q '^BASELINE_TOP1 4/4$' lab.out || { echo baseline expectation changed; exit 1; }
grep -q '^GATE FACTS 6 RULES 2 PROOF proof$' lab.out || { echo gate expectation changed; exit 1; }
echo "TRANSFORMER_TOP1 0/4 (negative)"
echo "BASELINE_TOP1 4/4"
echo "GATE FACTS 6 RULES 2 PROOF proof"
echo "V0226-MARU-WEB-AXIOM-TRANSFORMER-PASS"
