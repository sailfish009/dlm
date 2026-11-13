#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/miniconda3/envs/py314/bin/python3}
if [ ! -x "$PY" ]; then PY=python3; fi
for S in 31 32 33; do
  "$PY" propose_m5.py --test-worlds 80 --seed "$S" > "m5_seed${S}.log"
  cp m5_result.json "m5_seed${S}.json"
done
"$PY" verify_m5_seeds.py | tee m5_verify.log
