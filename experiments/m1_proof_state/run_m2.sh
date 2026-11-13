#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/miniconda3/envs/py314/bin/python3}
if [ ! -x "$PY" ]; then PY=python3; fi
if [ "$#" -gt 0 ]; then
  "$PY" train_m2.py "$@" | tee m2_train.log
  cp m2_result.json m2_last.json
else
  for S in 21 22 23; do
    "$PY" train_m2.py --train-worlds 180 --val-worlds 40 --test-worlds 40 --epochs 120 --seed "$S" > "m2_train_seed${S}.log"
    cp m2_result.json "m2_seed${S}.json"
    cp m2_ranker.pt "m2_ranker_seed${S}.pt"
  done
  "$PY" verify_m2_seeds.py | tee m2_verify.log
fi
