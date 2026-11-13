#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

grep -q '^DONE 10$' out/reference.out
grep -q '^DONE 10$' out/m0_O0.out
[ "$(grep -c '^RESULT ' out/m0_O0.out)" -eq 10 ] || { echo 'M0-RESULTS-FAIL'; exit 1; }
echo 'M0-SHAPE-PASS'

diff -q out/reference.out out/m0_O0.out >/dev/null || { echo 'M0-PICK-PARITY-FAIL'; exit 1; }
echo 'M0-PICKS 10/10'
echo 'M0-SEL-EXACT'
echo 'M0-PICK-PARITY-PASS'

for tag in PROJ0 PROJ1 ATTN FFN SEL; do
  grep -q "^TRACE .* $tag " out/reference_trace.out || { echo "M0-TRACE-MISSING $tag"; exit 1; }
done
diff -q out/reference_trace.out out/m0_trace.out >/dev/null || { echo 'M0-TRACE-DIFF'; exit 1; }
echo 'M0-PROJ-PASS'
echo 'M0-ATTN-PASS'
echo 'M0-FFN-PASS'
echo 'M0-LOOP1-PASS'
grep -q '^TRACE .* FFN 5 ' out/m0_trace.out || { echo 'M0-LOOP6-FAIL'; exit 1; }
echo 'M0-LOOP6-PASS'

for O in 2 3; do
  diff -q out/m0_O0.out out/m0_O$O.out >/dev/null || { echo "M0-O$O-DIFF"; exit 1; }
done
echo 'M0-O0/O2/O3-IDENTICAL yes'
if diff -q out/reference.out out/m0_loop1.out >/dev/null; then
  echo 'M0-NEGATIVE-FAIL: one-loop build matched six-loop reference'; exit 1
fi
echo 'M0-NEGATIVE-PASS' 

# Integer-only audit: no floating-point arithmetic in the candidate.
if grep -nE '\b(double|float)\b' src/dt_m0_infer.c | grep -v 'printf' >/tmp/m0_float_hits 2>/dev/null; then
  cat /tmp/m0_float_hits; echo 'M0-NO-DOUBLE-FAIL'; exit 1
fi
if grep -nE '(^|[^a-zA-Z_])sqrt[[:space:]]*\(|(^|[^a-zA-Z_])exp[[:space:]]*\(|(^|[^a-zA-Z_])pow[[:space:]]*\(' src/dt_m0_infer.c >/tmp/m0_libm_hits 2>/dev/null; then
  cat /tmp/m0_libm_hits; echo 'M0-NO-LIBM-FAIL'; exit 1
fi
echo 'M0-NO-DOUBLE yes'
echo 'M0-INTEGER-ONLY yes'
echo 'M0-PARITY-PASS'
