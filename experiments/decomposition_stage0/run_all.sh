#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run.sh > stage0.out
./verify.sh
