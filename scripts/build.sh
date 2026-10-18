#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Use the ordinary seed so embedded baseline payloads cannot hide source changes.
"$ROOT/scripts/compile-maru.sh" "${BUILD_MARU:-$ROOT/bootstrap/maru-seed}" "$ROOT/build/maru-compiler"
cp "$ROOT/build/maru-compiler" "$ROOT/maru-compiler.new"
mv "$ROOT/maru-compiler.new" "$ROOT/maru-compiler"
echo 'Built maru-compiler from current source using explicit build seed.'
