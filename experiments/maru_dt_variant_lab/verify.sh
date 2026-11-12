#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for f in baseline.out loops1.out loops3.out prior0.out prior8.out; do
  [ -s "$f" ] || { echo "missing $f"; exit 1; }
  grep -q '^CASE 9 ' "$f"
  [ "$(awk '/^CASE /{printf "%s",$13}' "$f")" = "1111111111" ] || { echo "proof fail $f"; exit 1; }
done
base=$(awk '/^CASE /{printf "%s ",$7}' baseline.out)
echo "PICKS $base"
[ "$base" = "$(cat expected_picks.txt) " ] || { echo 'baseline pick mismatch'; exit 1; }
for f in loops1 loops3 prior8; do
  [ "$(awk '/^CASE /{printf "%s ",$7}' $f.out)" = "$base" ] || { echo "$f pick changed"; exit 1; }
done
p0=$(awk '/^CASE /{printf "%s ",$7}' prior0.out)
[ "$p0" != "$base" ] || { echo 'prior0 did not change picks'; exit 1; }
echo "BASELINE 10/10 PROOF 10/10"
echo "LOOPS1/3 PICKS UNCHANGED"
echo "PRIOR0 PICKS CHANGED"
echo "V0225-MARU-NATIVE-TRANSFORMER-VARIANT-PASS"
