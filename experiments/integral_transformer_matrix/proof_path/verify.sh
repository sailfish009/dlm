#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^PATHS 2 R1 1 R2 1$' out.txt || { echo 'path count changed'; exit 1; }
grep -q '^INTEGRAL-R1 32768 INTEGRAL-R2 32768$' out.txt || { echo 'integral credit changed'; exit 1; }
grep -q '^NEG 0 (want 0)$' out.txt || { echo 'negative proof changed'; exit 1; }
echo 'PROOF-PATH-INTEGRAL 2 paths'
echo 'SINGLE-PROOF credit: R1 only'
echo 'PATH-INTEGRAL credit: R1=1/2 R2=1/2'
echo 'NEG 0'
echo 'V0228-PROOF-PATH-INTEGRAL-PASS'
