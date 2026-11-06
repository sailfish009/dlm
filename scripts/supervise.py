#!/usr/bin/env python3
"""Restart a finite native run from its last replay-verified checkpoint.

A crash is not caught and resumed in-process: the child dies, the supervisor
validates the checkpoint by replay, and starts a fresh child that continues from
that state. SIGSEGV is never swallowed.
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def maru_ok(code: str) -> tuple[int, str]:
    p = subprocess.run([str(ROOT / 'scripts' / 'run.sh'), 'proof', '-'],
                       input=code, text=True, capture_output=True, timeout=300)
    return p.returncode, p.stdout + p.stderr


def checkpoint_ok(store: Path) -> bool:
    if not store.exists():
        return False
    rc, out = maru_ok(f'(dump (dlm \'open "{store}")) (print "\\n")')
    return rc == 0 and 'rejected' not in out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', required=True)
    ap.add_argument('--driver', required=True)
    ap.add_argument('--rounds', type=int, default=4)
    ap.add_argument('--attempts', type=int, default=3)
    a = ap.parse_args()
    store = Path(a.store)
    for attempt in range(1, a.attempts + 1):
        print(f'[supervisor] attempt {attempt}: {a.driver} --rounds {a.rounds}', flush=True)
        p = subprocess.run([sys.executable, a.driver, '--store', str(store),
                            '--rounds', str(a.rounds), '--fault', '1' if attempt == 1 else '0'],
                           text=True)
        if p.returncode == 0:
            print('[supervisor] child finished normally', flush=True)
            return 0
        ok = checkpoint_ok(store)
        print(f'[supervisor] child exit {p.returncode}; checkpoint valid={ok}', flush=True)
        if not ok:
            print('[supervisor] no usable checkpoint: refusing to continue', flush=True)
            return 2
    return 1


if __name__ == '__main__':
    sys.exit(main())
