#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
base=$(awk '/RESULT/{printf "%s ",$10}' p0_E00.out)
[ "$base" = "211 154 2 22 61 61 34 76 125 5 " ] || { echo 'prior0 baseline changed'; exit 1; }
for n in E01 E02 E03 E04 E05 E06 E07; do
  p=$(awk '/RESULT/{printf "%s ",$10}' p0_$n.out)
  [ "$p" != "$base" ] || { echo "$n did not differ from prior0 baseline"; exit 1; }
  echo "$n $p"
done
echo "PRIOR0-BASELINE $base"
echo 'V0229-PRIOR-DECORRELATED-MATRIX-PASS'
