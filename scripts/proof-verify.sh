#!/usr/bin/env bash
# Evidence and canonical input hash are both rechecked before acceptance.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILE="${1:?proof snapshot required}"
ACTUAL="$("$ROOT/scripts/run.sh" proof "$ROOT/experiments/proof/fingerprint.l" < "$FILE" | sha256sum | cut -d' ' -f1)"
EXPECTED="$("$ROOT/scripts/run.sh" proof "$ROOT/experiments/proof/hash.l" < "$FILE")"
[[ "$EXPECTED" =~ ^[0-9a-f]{64}$ && "$EXPECTED" == "$ACTUAL" ]] || { echo 'proof input hash mismatch' >&2; exit 1; }
"$ROOT/scripts/run.sh" proof "$ROOT/experiments/proof/report.l" < "$FILE"
