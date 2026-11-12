#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DLM="$(cd "$ROOT/../.." && pwd)"
M="${MARU:-$DLM/maru-compiler}"
exec "$M" "$DLM/src/maru/boot.l" "$DLM/src/dlm/logic.l" "$ROOT/src/array_join.l"
