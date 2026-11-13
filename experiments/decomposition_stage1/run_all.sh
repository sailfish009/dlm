#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run.sh > stage1.out
cat stage1.out
