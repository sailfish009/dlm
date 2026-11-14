#!/usr/bin/env bash
# Offline regeneration of the frozen teacher observations (requires torch).
# This is provenance tooling, NOT part of release verification.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/adapters/teacher_transformer.py"
echo "TEACHER-DATA-REGENERATED (offline; re-pin docs/release.sources.sha256)"
