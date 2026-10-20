#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUDGET="${1:-1000}"
[[ "$BUDGET" =~ ^[0-9]+$ ]] && (( BUDGET <= 9000 )) || { echo 'budget must be 0..9000' >&2; exit 2; }
DRIVER="$(mktemp)"
trap 'rm -f "$DRIVER"' EXIT
printf '(define *fld-budget* %s)\n(require "experiments/fld/run.l")\n' "$BUDGET" > "$DRIVER"
"$ROOT/scripts/run.sh" proof "$DRIVER"
