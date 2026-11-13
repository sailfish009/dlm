#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/miniconda3/envs/py314/bin/python3}
if [ ! -x "$PY" ]; then PY=python3; fi
"$PY" qualify.py | tee qualify.log
for V in base a1_cross a2_pe a3_tied2 a3_indep1; do
  for S in 11 12 13; do
    "$PY" train.py --variant "$V" --seed "$S" > "train_${V}_seed${S}.log"
    echo "trained $V seed $S"
  done
done
./repeat_check.sh | tee repeat.out
"$PY" verify.py | tee verify.log