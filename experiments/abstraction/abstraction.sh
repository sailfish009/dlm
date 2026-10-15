#!/usr/bin/env bash
# DLM v0.0042 abstraction ladder (L5..L9): composition, architecture, intent,
# causal "why", and transfer to the held-out real PyTorch MNIST program.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"
exec env PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 "$HERE/run.py" "$@"
