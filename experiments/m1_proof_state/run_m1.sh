#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/miniconda3/envs/py314/bin/python3}
if [ ! -x "$PY" ]; then PY=python3; fi
if [ "$#" -gt 0 ]; then
  "$PY" train_m1.py "$@" | tee m1_train.log
  "$PY" verify_m1.py | tee m1_verify.log
else
  for S in 11 12 13; do
    "$PY" train_m1.py --train-worlds 180 --val-worlds 40 --test-worlds 40 --epochs 120 --seed "$S" > "m1_train_seed${S}.log"
    cp m1_result.json "m1_seed${S}.json"
  done
  "$PY" verify_m1_seeds.py | tee m1_verify.log
fi
