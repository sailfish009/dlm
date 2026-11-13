#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/miniconda3/envs/py314/bin/python3}
if [ ! -x "$PY" ]; then PY=python3; fi
cp integral_seed777.json /tmp/integral_seed777_first.json
"$PY" integral_learn.py --seed 777 --out integral_seed777.json > /tmp/integral_repeat777.log
cmp -s integral_seed777.json /tmp/integral_seed777_first.json
echo DETERMINISTIC yes