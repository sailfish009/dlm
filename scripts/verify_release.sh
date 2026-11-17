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
( cd experiments/native_integral && ./run_all.sh > /tmp/native_integral_release.log 2>&1 ) \
  || { echo LAB-GATE-FAIL; tail -30 /tmp/native_integral_release.log; exit 1; }
grep -q '^V0243-NATIVE-INTEGRAL-PASS$' /tmp/native_integral_release.log || { echo LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE native_integral: $(grep -c '^DISCRIMINATIVE\|^SIGNIFICANCE' /tmp/native_integral_release.log) checks, V0243-NATIVE-INTEGRAL-PASS"

# --- proof-state transformer lab gate (0.0244) -------------------------------
( cd experiments/proof_state_transformer_maru && ./run.sh > /tmp/pst_run.log 2>&1 && ./verify.sh > /tmp/pst_verify.log 2>&1 ) \
  || { echo PST-LAB-GATE-FAIL; tail -20 /tmp/pst_run.log /tmp/pst_verify.log; exit 1; }
grep -q '^V0251-PROOF-STATE-HARNESS-REPAIR-PASS$' /tmp/pst_verify.log || { echo PST-LAB-GATE-FAIL; exit 1; }
echo "LAB-GATE proof_state_transformer_maru: $(grep -c '^PARITY\|^GRADCHECK\|^LLVM\|^F1-\|^F4-\|^F2\|^F6\|^F5-\|^GATE-REGRESSION-PASS' /tmp/pst_verify.log) checks, V0251-PROOF-STATE-HARNESS-REPAIR-PASS"

./scripts/run.sh test
./scripts/compiler.sh verify "$ID"
echo "RELEASE-VERIFY-PASS version=$VER runtime=$ID"