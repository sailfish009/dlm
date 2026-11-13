#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/miniconda3/envs/py314/bin/python3}
if [ ! -x "$PY" ]; then PY=python3; fi
"$PY" integrability.py | tee integrability.log
for S in 777 778 779; do
  "$PY" integral_learn.py --seed "$S" --out "integral_seed${S}.json" > "e2_seed${S}.log"
  echo "E2 seed $S done"
done
./repeat_check.sh | tee repeat.out
"$PY" verify.py | tee verify.log