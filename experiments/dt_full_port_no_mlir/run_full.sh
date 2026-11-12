#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
clang -O3 -I. dt_full_infer.c -o dt_full_infer
./dt_full_infer > c_infer_all.out
python3 verify_full.py
