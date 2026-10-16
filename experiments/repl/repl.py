#!/usr/bin/env python3
"""Interactive TreeLisp shell over one persistent model-state IR-TREE."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dlm import EvalError, Store, dump, evaluate_expr, loads, new_state  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", type=Path, default=ROOT / "experiments/repl/store")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--eval", default="")
    parser.add_argument("--fuel", type=int, default=10000)
    args = parser.parse_args()
    store = Store(args.store)
    if store.exists() and not args.fresh:
        state = store.load()
    else:
        state = new_state(())
        store.create(state, overwrite=args.fresh)

    def execute(text):
        nonlocal state
        value = evaluate_expr(loads(text), state, fuel=args.fuel)
        if isinstance(value, tuple) and value and value[0] == "transition":
            state = store.append(state, value)
        print(dump(value))

    if args.eval:
        execute(args.eval)
        return 0
    print("DLM TreeLisp 0.0.65. Commands are bounded IR operations; Ctrl-D exits.")
    while True:
        try:
            text = input("ir> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        try:
            execute(text)
        except (EvalError, ValueError) as error:
            print(f"(error {dump(str(error))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
