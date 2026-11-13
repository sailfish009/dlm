#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run.sh > out.txt
./run_oracle.sh > oracle.out
./run_adversarial.sh > adversarial.out
./run_probe.sh > probe.out
./repeat_check.sh > repeat.out
./verify.sh
./stub_test.sh
