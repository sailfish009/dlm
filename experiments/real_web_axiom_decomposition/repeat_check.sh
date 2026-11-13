#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run.sh > /tmp/rw_repeat1.out
./run.sh > /tmp/rw_repeat2.out
cmp -s /tmp/rw_repeat1.out /tmp/rw_repeat2.out
echo DETERMINISTIC yes
