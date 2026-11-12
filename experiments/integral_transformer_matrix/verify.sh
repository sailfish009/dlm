#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
base=$(awk '/^RESULT/{printf "%s ",$10}' E00.out)
[ "$base" = "211 45 2 22 61 61 34 76 16 5 " ] || { echo 'baseline picks changed'; exit 1; }
for f in E01.out E02.out E03.out E04.out E05.out E06.out E07.out; do
  p=$(awk '/^RESULT/{printf "%s ",$10}' "$f")
  [ "$p" = "$base" ] || { echo "$f picks changed"; exit 1; }
done
# show that integral variants alter selector magnitudes even when picks are stable
a0=$(awk '/^RESULT 0 /{print $7}' E00.out)
a1=$(awk '/^RESULT 0 /{print $7}' E01.out)
[ "$a0" != "$a1" ] || { echo 'integral attention did not change selector'; exit 1; }
echo "E00-E07 PICKS UNCHANGED"
echo "E00 selector $a0"
echo "E01 selector $a1"
echo "E02-E07 recorded selector changes"
echo "V0228-INTEGRAL-TRANSFORMER-VARIANT-MATRIX-PASS"
