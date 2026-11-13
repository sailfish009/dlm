#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/miniconda3/envs/py314/bin/python3}
if [ ! -x "$PY" ]; then PY=python3; fi
MODEL=${MODEL:-../m1_proof_state/m2_ranker.pt}
if [ "$#" -gt 0 ]; then
  "$PY" selfssl_m3.py "$@"
  cp m3_result.json m3_last.json
else
  for S in 21 22 23; do
    "$PY" selfssl_m3.py --test-worlds 80 --seed "$S" --model "$MODEL" > "m3_seed${S}.log"
    cp m3_result.json "m3_seed${S}.json"
  done
  "$PY" verify_m3_seeds.py | tee m3_verify.log
fi
