#!/usr/bin/env bash
# Variant sweep on the declared composition-requiring ("hard") fixture, plus the
# reference-fidelity fixture for the saturation report.
# 5 seeds, 180 train / 60 val / 100 entity-held-out test worlds, same search budget.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out
SEEDS="${SEEDS:-5}"
EPOCHS="${EPOCHS:-40}"
run_one () {
  local name="$1"; local fixture="$2"; shift 2
  local flags=""; [ "$fixture" = hard ] && flags="-DHARD_GOALS=1"
  clang -O2 -Iinclude -Isrc $flags "$@" -DVNAME="\"$name\"" src/pst.c -o "bin/pst_${name}_${fixture}" -lm
  "bin/pst_${name}_${fixture}" --train --seeds "$SEEDS" --epochs "$EPOCHS" \
    --train-n 180 --val-n 60 --test-n 100 > "out/${name}_${fixture}.txt"
}
for f in ref hard; do
  run_one base "$f"
  run_one utilhead  "$f" -DVAR_UTILHEAD=1
  run_one mask      "$f" -DVAR_MASK=1
  run_one goalx     "$f" -DVAR_GOALX=1
  run_one loop      "$f" -DVAR_LOOP=1
  run_one bind      "$f" -DVAR_BIND=1
done
for f in ref hard; do
  echo "== fixture $f"
  for v in base utilhead mask goalx loop bind; do grep -h '^MEAN' "out/${v}_${f}.txt"; done | sed -E 's/^MEAN //'
done
