#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
rm -rf out
mkdir -p out
CC=${CC:-clang}
$CC -O0 -Ireference reference/dt_full_infer.c -o out/reference_infer -lm
./out/reference_infer > out/reference.out
$CC -O0 -Ireference -DM0_TRACE reference/dt_full_trace.c -o out/reference_trace -lm
./out/reference_trace > out/reference_trace.out
for O in 0 2 3; do
  $CC -O$O -Ireference -Iinclude src/dt_m0_infer.c -o out/m0_O$O -lm
  ./out/m0_O$O > out/m0_O$O.out
done
$CC -O0 -Ireference -Iinclude -DM0_TRACE src/dt_m0_infer.c -o out/m0_trace -lm
./out/m0_trace > out/m0_trace.out
$CC -O0 -Ireference -Iinclude -DM0_LAYERS=1 src/dt_m0_infer.c -o out/m0_loop1 -lm
./out/m0_loop1 > out/m0_loop1.out
echo M0-BUILD-PASS
