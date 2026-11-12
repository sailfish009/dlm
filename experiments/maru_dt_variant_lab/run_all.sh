#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for v in baseline loops1 loops3 prior0 prior8; do
  ./run_variant.sh "$v" > "$v.out"
done
./verify.sh
