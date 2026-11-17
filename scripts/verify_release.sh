#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ID="$(cat docs/release.txt)"
VER="$(cat VERSION)"
echo "VERSION=$VER RUNTIME=$ID"
test -x maru-compiler
test "$(readlink -f maru-compiler)" = "$ROOT/runtime/releases/$ID/maru"
test -f "runtime/releases/$ID/artifacts.sha256"
echo "runtime symlink: ok"
sha256sum -c docs/release.sources.sha256 >/dev/null
sha256sum -c docs/release.tests.sha256 >/dev/null
echo "manifests: ok"
# no unapproved large files outside runtime
BAD="$(find . -path ./runtime -prune -o -type f -size +5M -print)"
if [ -n "$BAD" ]; then echo "large files outside runtime:"; echo "$BAD"; exit 1; fi
echo "tree size: ok"

# --- version consistency (capabilities.json is a release source) -------------
CAPVER="$(sed -n 's/.*"version": "\([^"]*\)".*/\1/p' capabilities.json | head -1)"
if [ "$CAPVER" != "$VER" ]; then
  echo "VERSION-MISMATCH capabilities.json=$CAPVER VERSION=$VER"; exit 1
fi
echo "VERSION-MATCH capabilities.json=$CAPVER"

# --- native scope: release sources and release gate must be torch-free -------
PY_SRC="$(awk '{print $2}' docs/release.sources.sha256 | grep '\.py$' || true)"
if [ -n "$PY_SRC" ] && grep -l "import torch\|from torch" $PY_SRC 2>/dev/null | grep -q .; then
  echo "NATIVE-SCOPE-FAIL: torch imported by release python sources:"
  grep -l "import torch\|from torch" $PY_SRC 2>/dev/null
  exit 1
fi
if grep -q "import torch\|from torch" scripts/teacher_transformer.sh scripts/compiler.sh; then
  echo "NATIVE-SCOPE-FAIL: torch import on the release-gate path"; exit 1
fi
sha256sum -c docs/research-snapshots.sha256 >/dev/null
echo "NATIVE-SCOPE-PASS release sources/gate are torch-free"
echo "SCOPE torch_files_outside_native_scope=$(wc -l < docs/research-snapshots.sha256) (pinned in docs/research-snapshots.sha256)"

# --- headline lab gate (0.0243) ---------------------------------------------
( cd experiments/native_integral && SEEDS="${LEGACY_SEEDS:-5}" ./run_all.sh > /tmp/native_integral_release_0256.log 2>&1 ) \
  || { echo LAB-GATE-FAIL; tail -30 /tmp/native_integral_release_0256.log; exit 1; }
grep -q '^V0243-NATIVE-INTEGRAL-PASS$' /tmp/native_integral_release_0256.log || { echo LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE native_integral: $(grep -c '^DISCRIMINATIVE\|^SIGNIFICANCE' /tmp/native_integral_release_0256.log) checks, V0243-NATIVE-INTEGRAL-PASS"

# --- proof-state transformer lab gate (0.0244) -------------------------------
( cd experiments/proof_state_transformer_maru && SEEDS="${LEGACY_SEEDS:-5}" ./run.sh > /tmp/pst_run_0256.log 2>&1 && SEEDS="${LEGACY_SEEDS:-5}" ./verify.sh > /tmp/pst_verify_0256.log 2>&1 ) \
  || { echo PST-LAB-GATE-FAIL; tail -n 20 /tmp/pst_run_0256.log /tmp/pst_verify_0256.log; exit 1; }
grep -q '^V0256-SOUNDNESS-PASS$' /tmp/pst_verify_0256.log || { echo PST-SOUNDNESS-GATE-FAIL; exit 1; }
echo "LAB-GATE proof_state_transformer_maru: $(grep -c '^PARITY\|^GRADCHECK\|^LLVM\|^F1-\|^F4-\|^F2\|^F6\|^F5-\|^GATE-REGRESSION-PASS' /tmp/pst_verify_0256.log) checks, V0256-SOUNDNESS-PASS"

# --- 0.0260 hybrid reasoning-layer gate --------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_hybrid.sh > /tmp/pst_hybrid_run_0260.log 2>&1 \
    && ./verify_hybrid.sh > /tmp/pst_hybrid_verify_0260.log 2>&1 ) \
  || { echo HYBRID-LAB-GATE-FAIL; tail -n 20 /tmp/pst_hybrid_run_0260.log /tmp/pst_hybrid_verify_0260.log; exit 1; }
grep -q '^V0260-HYBRID-PASS$' /tmp/pst_hybrid_verify_0260.log || { echo HYBRID-LAB-GATE-FAIL; exit 1; }
# --- 0.0269 simple-loop gate (G1-G6) -----------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_simple.sh > /tmp/pst_s269_run.log 2>&1 \
    && SEEDS=5 ./verify_simple0269.sh > /tmp/pst_s269_verify.log 2>&1 ) \
  || { echo S269-LAB-GATE-FAIL; tail -n 20 /tmp/pst_s269_run.log /tmp/pst_s269_verify.log; exit 1; }
grep -q '^V0269-SIMPLE-PASS$' /tmp/pst_s269_verify.log || { echo S269-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE simple loop: $(grep -c 'PASS$' /tmp/pst_s269_verify.log) checks, V0269-SIMPLE-PASS"

# --- 0.0269 loop-cell gate (BPTT recurrence + controls) ----------------------
( cd experiments/proof_state_transformer_maru && ./run_loop0269.sh > /tmp/pst_l269_run.log 2>&1 \
    && SEEDS=5 ./verify_loop0269.sh > /tmp/pst_l269_verify.log 2>&1 ) \
  || { echo L269-LAB-GATE-FAIL; tail -n 20 /tmp/pst_l269_run.log /tmp/pst_l269_verify.log; exit 1; }
grep -q '^V0269-LOOPCELL-PASS$' /tmp/pst_l269_verify.log || { echo L269-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE loop cell: $(grep -c 'PASS' /tmp/pst_l269_verify.log) checks, V0269-LOOPCELL-PASS"

# --- 0.0268 corrected recombination gate ------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_recomb0268.sh > /tmp/pst_r268_run.log 2>&1 \
    && SEEDS=5 ./verify_recomb0268.sh > /tmp/pst_r268_verify.log 2>&1 ) \
  || { echo R268-LAB-GATE-FAIL; tail -n 20 /tmp/pst_r268_run.log /tmp/pst_r268_verify.log; exit 1; }
grep -q '^V0268-RECOMB-PASS$' /tmp/pst_r268_verify.log || { echo R268-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE corrected recombination: $(grep -c '^RECOMB-\|^LABEL-INDEPENDENT-PASS\|^HEADER-LABELFLAGS-PASS\|^BUDGET-\|^CEILING-PASS\|^CLAIMS-\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^LLVM-PASS' /tmp/pst_r268_verify.log) checks, V0268-RECOMB-PASS"

# --- 0.0267 recombination gate ----------------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_recomb.sh > /tmp/pst_recomb_run_0267.log 2>&1 \
    && SEEDS=5 ./verify_recomb.sh > /tmp/pst_recomb_verify_0267.log 2>&1 ) \
  || { echo RECOMB-LAB-GATE-FAIL; tail -n 20 /tmp/pst_recomb_run_0267.log /tmp/pst_recomb_verify_0267.log; exit 1; }
grep -q '^V0267-RECOMB-PASS$' /tmp/pst_recomb_verify_0267.log || { echo RECOMB-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE recombination: $(grep -c '^RECOMB-\|^LABEL-BUDGET-PASS\|^BUDGET-LADDER-PASS\|^BUDGET-GUARD-PASS\|^CEILING-PASS\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^WHDR-PASS\|^LLVM-PASS' /tmp/pst_recomb_verify_0267.log) checks, V0267-RECOMB-PASS"

# --- 0.0266 label-decomposition gate ----------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_decomp.sh.0266 > /tmp/pst_decomp_run_0266.log 2>&1 \
    && SEEDS=15 ./verify_decomp0266.sh > /tmp/pst_decomp_verify_0266.log 2>&1 ) \
  || { echo DECOMP-LAB-GATE-FAIL; tail -n 20 /tmp/pst_decomp_run_0266.log /tmp/pst_decomp_verify_0266.log; exit 1; }
grep -q '^V0266-LABELDECOMP-PASS$' /tmp/pst_decomp_verify_0266.log || { echo DECOMP-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE label decomposition: $(grep -c '^DECOMP-\|^CENSUS-TRAIN-PASS\|^SHUFFLE-CONTROL-PASS\|^COST-LOCALISATION-PASS\|^CEILING-PASS\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^WHDR-PASS\|^LLVM-PASS' /tmp/pst_decomp_verify_0266.log) checks, V0266-LABELDECOMP-PASS"

# --- 0.0265 deductive-label gate --------------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_onpath.sh > /tmp/pst_onpath_run_0265.log 2>&1 \
    && SEEDS=15 ./verify_onpath.sh > /tmp/pst_onpath_verify_0265.log 2>&1 ) \
  || { echo ONPATH-LAB-GATE-FAIL; tail -n 20 /tmp/pst_onpath_run_0265.log /tmp/pst_onpath_verify_0265.log; exit 1; }
grep -q '^V0265-ONPATH-PASS$' /tmp/pst_onpath_verify_0265.log || { echo ONPATH-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE deductive label: $(grep -c '^ONPATH-\|^CONSERVATION-PASS\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^WHDR-PASS\|^LLVM-PASS' /tmp/pst_onpath_verify_0265.log) checks, V0265-ONPATH-PASS ($(grep -o 'PROOF-PATH-LABEL-DEMONSTRATED' /tmp/pst_onpath_verify_0265.log | head -1))"

# --- 0.0263/0.0264 architecture gates ---------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_reg.sh > /tmp/pst_reg_run_0263.log 2>&1 \
    && ./verify_reg.sh > /tmp/pst_reg_verify_0263.log 2>&1 ) \
  || { echo REG-LAB-GATE-FAIL; tail -n 20 /tmp/pst_reg_run_0263.log /tmp/pst_reg_verify_0263.log; exit 1; }
grep -q '^V0263-MULTIREG-PASS$' /tmp/pst_reg_verify_0263.log || { echo REG-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE multi-register transformer: $(grep -c '^REG-\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^WHDR-PASS\|^LLVM-PASS' /tmp/pst_reg_verify_0263.log) checks, V0263-MULTIREG-PASS ($(grep -o 'MULTIREG-NOT-DEMONSTRATED' /tmp/pst_reg_verify_0263.log | head -1))"

( cd experiments/proof_state_transformer_maru && ./run_scale15.sh > /tmp/pst_scale_run_0264.log 2>&1 \
    && SEEDS=15 ./verify_scale.sh > /tmp/pst_scale_verify_0264.log 2>&1 ) \
  || { echo SCALE-LAB-GATE-FAIL; tail -n 20 /tmp/pst_scale_run_0264.log /tmp/pst_scale_verify_0264.log; exit 1; }
grep -q '^V0264-SCALE-PASS$' /tmp/pst_scale_verify_0264.log || { echo SCALE-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE capacity scaling: $(grep -c '^SCALE-\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^WHDR-PASS\|^LLVM-PASS' /tmp/pst_scale_verify_0264.log) checks, V0264-SCALE-PASS ($(grep -o 'SCALE-NOT-DEMONSTRATED' /tmp/pst_scale_verify_0264.log | head -1))"

# --- 0.0262 DP-value gate ----------------------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_value.sh > /tmp/pst_value_run_0262.log 2>&1 \
    && ./verify_value.sh > /tmp/pst_value_verify_0262.log 2>&1 ) \
  || { echo VALUE-LAB-GATE-FAIL; tail -n 20 /tmp/pst_value_run_0262.log /tmp/pst_value_verify_0262.log; exit 1; }
grep -q '^V0262-DPVALUE-PASS$' /tmp/pst_value_verify_0262.log || { echo VALUE-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE DP value labels: $(grep -c '^DP-\|^VAL-\|^CONSERVATION-PASS\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^WHDR-PASS\|^LLVM-PASS' /tmp/pst_value_verify_0262.log) checks, V0262-DPVALUE-PASS ($(grep -o 'DP-VALUE-NOT-DEMONSTRATED' /tmp/pst_value_verify_0262.log | head -1))"

# --- 0.0261 learned-contract gate -------------------------------------------
( cd experiments/proof_state_transformer_maru && ./run_pair.sh > /tmp/pst_pair_run_0261.log 2>&1 \
    && ./verify_pair.sh > /tmp/pst_pair_verify_0261.log 2>&1 ) \
  || { echo PAIR-LAB-GATE-FAIL; tail -n 20 /tmp/pst_pair_run_0261.log /tmp/pst_pair_verify_0261.log; exit 1; }
grep -q '^V0261-PAIRLEARN-PASS$' /tmp/pst_pair_verify_0261.log || { echo PAIR-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE learned contracts: $(grep -c '^PAIR-\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^WHDR-PASS\|^LLVM-PASS' /tmp/pst_pair_verify_0261.log) checks, V0261-PAIRLEARN-PASS ($(grep -o 'PAIR-LEARN-NOT-DEMONSTRATED' /tmp/pst_pair_verify_0261.log | head -1))"

echo "LAB-GATE hybrid (rocq/silicon/screamer): $(grep -c '^GRADCHECK-PASS\|^PC-PATH-PASS\|^CERT-PASS\|^CERT-MUTATION-PASS\|^FOCUS-\|^FOCUS-COMPLETENESS-PASS\|^LEMMA-PASS\|^HYBRID-TABLE-PASS\|^GATE-REGRESSION-PASS\|^WHDR-PASS\|^LLVM-PASS' /tmp/pst_hybrid_verify_0260.log) checks, V0260-HYBRID-PASS"

# --- relational closure lab gate (0.0253) ----------------------------------
( cd experiments/relational_closure_maru && SEEDS="${LEGACY_SEEDS:-5}" ./run.sh > /tmp/rc_run_0256.log 2>&1 && SEEDS="${LEGACY_SEEDS:-5}" ./verify.sh > /tmp/rc_verify_0256.log 2>&1 ) \
  || { echo RC-LAB-GATE-FAIL; tail -n 20 /tmp/rc_run_0256.log /tmp/rc_verify_0256.log; exit 1; }
grep -q '^V0253-CLOSURE-PRIMITIVE-NEGATIVE-PASS$' /tmp/rc_verify_0256.log || { echo RC-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE relational_closure_maru: V0253-CLOSURE-PRIMITIVE-NEGATIVE-PASS (closure primitive sound but not distinctive vs attention)"

./scripts/run.sh test
./scripts/compiler.sh verify "$ID"
echo "RELEASE-VERIFY-PASS version=$VER runtime=$ID"