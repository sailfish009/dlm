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
# no unapproved large files outside runtime
BAD="$(find . -path ./runtime -prune -o -type f -size +5M -print)"
if [ -n "$BAD" ]; then echo "large files outside runtime:"; echo "$BAD"; exit 1; fi
echo "tree size: ok"
./scripts/run.sh test
./scripts/compiler.sh verify "$ID"
echo "RELEASE-VERIFY-PASS version=$VER runtime=$ID"
