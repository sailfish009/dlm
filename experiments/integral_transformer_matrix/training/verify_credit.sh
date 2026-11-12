#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
base=$(awk '/PICK/{printf "%s ",$4}' credit_0.out)
[ "$base" = "211 45 2 22 61 61 34 76 16 5 " ] || { echo 'baseline training changed'; exit 1; }
for n in 1 2; do
  p=$(awk '/PICK/{printf "%s ",$4}' credit_$n.out)
  [ "$p" = "$base" ] || { echo "credit $n picks changed"; exit 1; }
done
echo "CREDIT 0/1/2 PICKS IDENTICAL"
echo "V0228-INTEGRAL-CREDIT-NEUTRAL-PASS"
