#!/usr/bin/env bash
# DLM v0.0042 corpus generalization: learn concepts on a program corpus and
# transfer them to the north star (PyTorch MNIST main.py) by deduction.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
if [[ -x "$ROOT/test.sh" && ! -d "$ROOT/.venv" ]]; then :; fi
exec env PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 "$HERE/run.py" "$@"
