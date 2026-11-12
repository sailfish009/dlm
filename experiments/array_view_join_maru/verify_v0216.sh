#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run_file.sh src/array_join.l > array_join.out
python3 verify_v0216.py array_join.out
./run_file.sh src/ref_only.l > ref_only.out
./run_file.sh src/join_only.l > join_only.out
./c/bench_join > c/bench_join.out
echo V0216-ALL-PASS
