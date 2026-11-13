#!/usr/bin/env bash
# Computed gates (bash + awk; no Python). Every PASS line is backed by a check.
set -euo pipefail
cd "$(dirname "$0")"
# C kernel parity fixture
grep -q '^PARITY2 derived=6 reached=2 known=63$' out/O0.txt || { echo C-PARITY-FAIL; exit 1; }
# Maru oracle parity (same theory, p-close)
grep -q '^PARITY2 derived=6 reached=2$' out/maru_parity.txt || { echo MARU-PARITY-VAL-FAIL; exit 1; }
grep -q '^MARU-PARITY-PASS$' out/maru_parity.txt || { echo MARU-PARITY-FAIL; exit 1; }
echo "PARITY C==Maru ground closure (derived=6 reached=2)"
# LLVM opt-level identity
diff -q out/O0.txt out/O2.txt >/dev/null && diff -q out/O0.txt out/O3.txt >/dev/null || { echo LLVM-IDENTITY-FAIL; exit 1; }
echo "LLVM O0/O2/O3 byte-identical"
# Discriminative: integral > single+3pp AND > random AND > uniform, every seed.
for S in 777 778 779; do
  awk -v s="$S" '
    /^TEST integral/ {split($5,a,"="); ip=a[2]}
    /^TEST single/   {split($5,a,"="); sp=a[2]}
    /^TEST random/   {split($5,a,"="); rp=a[2]}
    /^TEST uniform/  {split($5,a,"="); up=a[2]}
    END {
      if (ip <= sp+3.0) {printf "SEED %s FAIL integral<=single+3 (%.2f vs %.2f)\n", s, ip, sp; exit 1}
      if (ip <= rp) {printf "SEED %s FAIL integral<=random\n", s; exit 1}
      if (ip <= up) {printf "SEED %s FAIL integral<=uniform\n", s; exit 1}
      printf "SEED %s integral=%.2f single=%.2f random=%.2f uniform=%.2f (integral-single=+%.2fpp)\n", s, ip, sp, rp, up, ip-sp
    }' out/seed$S.txt || exit 1
done
echo "DISCRIMINATIVE integral > single+3pp AND > random AND > uniform (3 seeds, computed)"
# Determinism
./llvm/icredit_s777 > out/repeat777.txt
cmp -s out/seed777.txt out/repeat777.txt || { echo DETERMINISM-FAIL; exit 1; }
echo "DETERMINISM seed777 re-run byte-identical"
echo "V0242-NATIVE-INTEGRAL-PASS"