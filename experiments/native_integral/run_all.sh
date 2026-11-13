#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run.sh | tee run.log
./verify.sh | tee verify.log