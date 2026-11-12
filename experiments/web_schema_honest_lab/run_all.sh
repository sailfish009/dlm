#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run.sh > lab.out
./run_noweb.sh > noweb.out
./run_oracle.sh > oracle.out
./verify.sh
