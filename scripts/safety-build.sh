#!/usr/bin/env bash
# Build the SAME sources with Maru *safety* 2 and run the DLM suite.
# safety is an expand/bootstrap-time constant, so a runtime flag is not enough.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/runtime/safety2}"
rm -rf "$OUT"; mkdir -p "$OUT"
cp -a "$ROOT/src/maru" "$OUT/maru-src"
sed -i 's/^(define \*safety\* 1)$/(define *safety* 2)/' "$OUT/maru-src/boot.l"
grep -q 'define \*safety\* 2' "$OUT/maru-src/boot.l" || { echo 'safety patch failed' >&2; exit 1; }
"$OUT/maru-src/tools-for-build/build-compiler-image.sh" "$ROOT/bootstrap/maru-seed" "$OUT/maru" > "$OUT/build.log" 2>&1
chmod +x "$OUT/maru"
echo "built: $OUT/maru"
set +e
MARU="$OUT/maru" "$ROOT/scripts/run.sh" test > "$OUT/suite.log" 2>&1
rc=$?
set -e
if [ $rc -eq 0 ] && grep -q ALL-CORE-TESTS-PASSED "$OUT/suite.log"; then
  echo "safety2-gate: PASS"; exit 0
fi
echo "safety2-gate: FAIL (rc=$rc)"; tail -5 "$OUT/suite.log"; exit 1
