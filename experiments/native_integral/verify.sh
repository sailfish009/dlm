#!/usr/bin/env bash
# Computed gates (bash + awk; no Python). Every PASS line is backed by a check.
set -euo pipefail
cd "$(dirname "$0")"
R=out/O0.txt

# --- 1. C parity on the 6-atom toy theory ------------------------------------
grep -q '^PARITY2 derived=6 reached=2 known=63$' "$R" || { echo C-PARITY-FAIL; exit 1; }
grep -q '^PARITY2 derived=6 reached=2$' out/maru_parity.txt || { echo MARU-PARITY-VAL-FAIL; exit 1; }
grep -q '^MARU-PARITY-PASS$' out/maru_parity.txt || { echo MARU-PARITY-FAIL; exit 1; }
echo "PARITY toy C==Maru (derived=6 reached=2)"

# --- 2. Maru parity on the GENERATED 40-atom worlds --------------------------
grep -q '^MARU-WORLD-PASS$' out/maru_world.txt || { echo MARU-WORLD-FAIL; exit 1; }
if ! diff -q <(grep '^WORLD ' "$R") <(grep '^WORLD ' out/maru_world.txt) >/dev/null; then
  echo WORLD-PARITY-MISMATCH
  diff <(grep '^WORLD ' "$R") <(grep '^WORLD ' out/maru_world.txt) || true
  exit 1
fi
grep '^WORLD ' "$R" | sed 's/^/  parity /'
echo "PARITY generated worlds C==Maru (2 worlds, ground closure)"

# --- 3. LLVM identity --------------------------------------------------------
diff -q out/O0.txt out/O2.txt >/dev/null && diff -q out/O0.txt out/O3.txt >/dev/null \
  || { echo LLVM-IDENTITY-FAIL; exit 1; }
echo "LLVM O0/O2/O3 byte-identical (12 seeds, full diagnostics)"

# --- 4. data/compute-matched discrimination, every seed ----------------------
awk '
/^SEED [0-9]+ ARMS/ {
  seed=$2; p=l=u=r=v=0;
  for (i=4;i<=NF;i++){ split($i,kv,"=");
    if (kv[1]=="prior") p=kv[2]+0; else if (kv[1]=="last") l=kv[2]+0;
    else if (kv[1]=="uniform") u=kv[2]+0; else if (kv[1]=="random") r=kv[2]+0;
    else if (kv[1]=="pos_oracle") v=kv[2]+0; }
  if (p < l+10) { printf "SEED %s FAIL prior<=last+10 (%.2f vs %.2f)\n", seed, p, l; bad=1 }
  if (p < u+10) { printf "SEED %s FAIL prior<=uniform+10\n", seed; bad=1 }
  if (p < r+10) { printf "SEED %s FAIL prior<=random+10\n", seed; bad=1 }
  if (v < u+5)  { printf "SEED %s FAIL positive-control pos_oracle<=uniform+5\n", seed; bad=1 }
  n++; if (p-l < minmargin || n==1) minmargin=p-l
  printf "  seed %s prior=%.2f last=%.2f uniform=%.2f random=%.2f pos_oracle=%.2f (margin +%.2fpp)\n", seed, p, l, u, r, v, p-l
}
END { if (bad) exit 1; if (n!=12) {printf "FAIL expected 12 seeds, got %d\n", n; exit 1}
      printf "DISCRIMINATIVE prior>last/uniform/random+10pp and pos_oracle>uniform+5 on %d seeds (min margin +%.2fpp)\n", n, minmargin }
' "$R"

# --- 5. paired significance, every seed -------------------------------------
awk '
/^SEED [0-9]+ PAIRED prior_vs_last/ {
  z=0; w=lo=0;
  for (i=1;i<=NF;i++){ split($i,kv,"=");
    if (kv[1]=="z_milli") z=kv[2]+0; else if (kv[1]=="wins") w=kv[2]+0;
    else if (kv[1]=="losses") lo=kv[2]+0; }
  if (z < 1960) { printf "SEED %s FAIL z_milli=%d < 1960\n", $2, z; bad=1 }
  if (w <= lo)  { printf "SEED %s FAIL wins=%d <= losses=%d\n", $2, w, lo; bad=1 }
  n++
}
END { if (bad) exit 1; if (n!=12) {printf "FAIL expected 12 paired tests, got %d\n", n; exit 1}
      printf "SIGNIFICANCE paired prior>last z>=1960 (p<0.05) on %d seeds\n", n }
' "$R"
awk '
/^SEED [0-9]+ BOOT prior_minus_last/ {
  lo=0; for (i=1;i<=NF;i++){ split($i,kv,"="); if (kv[1]=="lo") lo=kv[2]+0 }
  if (lo <= 0) { printf "SEED %s FAIL bootstrap lo=%.2f <= 0\n", $2, lo; bad=1 }
  n++
}
END { if (bad) exit 1; printf "BOOTSTRAP prior-minus-last 95%% CI excludes 0 on %d seeds\n", n }
' "$R"

# --- 6. accumulation is measured, not assumed -------------------------------
awk '
/^SEED 777 ARMS/ { for (i=4;i<=NF;i++){ split($i,kv,"="); if (kv[1]=="prior") p=kv[2]+0 } }
/^SEED 777 SINGLEPOLICY/ { for (i=1;i<=NF;i++){ split($i,kv,"="); if (kv[1]=="mean_pct") m=kv[2]+0 } nz=1 }
/^SEED 777 CURVE/ { for (i=1;i<=NF;i++){ split($i,kv,"="); if (kv[1]=="l1_milli") l1=kv[2]+0 }
                    if ($4=="n=1") l1a=l1; if ($4=="n=400") l1b=l1 }
END { if (!nz) {print "FAIL missing SINGLEPOLICY"; exit 1}
      if (m + 10 > p) { printf "FAIL single-episode mean %.2f not << prior %.2f\n", m, p; exit 1 }
      if (!(l1b < l1a)) { printf "FAIL L1 error did not shrink (n=1 %.3f -> n=400 %.3f)\n", l1a/1000, l1b/1000; exit 1 }
      printf "ACCUMULATION 1-episode mean=%.2f%% vs prior=%.2f%%; L1 estimation error %d->%d milli (denoising measured)\n", m, p, l1a, l1b }
' "$R"

# --- 7. order controls ------------------------------------------------------
awk '
/^SEED [0-9]+ ORDER/ { rev=0; sh=0;
  for (i=1;i<=NF;i++){ split($i,kv,"=");
    if (kv[1]=="reversed") rev=kv[2]+0; else if (kv[1]=="shuffled") sh=kv[2]+0 }
  if (rev!=1 || sh!=1) { printf "SEED %s FAIL offline prior is not order invariant\n", $2; bad=1 }
  n++ }
END { if (bad) exit 1; printf "ORDER offline prior invariant to episode order on %d seeds (online feedback is path dependent, reported)\n", n }
' "$R"

# --- 8. determinism ---------------------------------------------------------
./llvm/icredit_O0 > out/repeat.txt
cmp -s out/O0.txt out/repeat.txt || { echo DETERMINISM-FAIL; exit 1; }
echo "DETERMINISM re-run byte-identical"

# --- 9. reported, not claimed ----------------------------------------------
grep -q '^SEED 777 CREDIT-GAP ' "$R" || { echo MISSING-CREDIT-GAP; exit 1; }
awk '/^SEED 777 PAIRED prior_vs_exact/ { print "  exact-credit control: " $0 }' "$R"
awk '/^SEED 777 CREDIT-GAP/ { print "  " $0 }' "$R"
awk '/^AGG / { print "  " $0 }' "$R"
echo "V0243-NATIVE-INTEGRAL-PASS"