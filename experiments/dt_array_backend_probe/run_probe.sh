#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
clang -O3 -I. dt_selector_c.c -o dt_selector_c
./dt_selector_c > c_selector.out
cat c_selector.out
python3 verify_probe.py c_selector.out
