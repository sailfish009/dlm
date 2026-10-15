#!/usr/bin/env bash
# DLM v0.0053 leveled final NL reading: the north-star body now emits the N1..N9
# reading itself; this harness consumes the SAME pipeline and adds the falsifiers
# (honesty ablation, D6 typed gate, D5 non-monotonicity, equality absences).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
exec env PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 "$HERE/run.py" "$@"