#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
clang -O3 -I. dt_train_c.c -o dt_train_c -lm
./dt_train_c > c_train_50.out
python3 verify_train.py
