#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/miniconda3/envs/py314/bin/python3}
if [ ! -x "$PY" ]; then PY=python3; fi
cp sd_base_seed11.json /tmp/sd_base_seed11_first.json
"$PY" train.py --variant base --seed 11 > /tmp/sd_repeat_base11.log
cmp -s sd_base_seed11.json /tmp/sd_base_seed11_first.json
echo DETERMINISTIC yes