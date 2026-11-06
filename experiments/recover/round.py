#!/usr/bin/env python3
"""One finite native run over a checkpoint; optionally abort AFTER a checkpoint.

--fault 1 simulates a crash (the child dies), so the supervisor must restart from
the replay-verified checkpoint instead of continuing in-process.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', required=True)
    ap.add_argument('--rounds', type=int, default=2)
    ap.add_argument('--fault', type=int, default=0)
    a = ap.parse_args()
    code = f'''
(dlm 'open "{a.store}")
(dlm 'observe 'r1 "fixture" "r1" 'demo (list (p107-atom 'calls (list "m1" "open")) (p107-atom 'calls (list "m1" "read")) (p107-atom 'calls (list "m1" "close"))))
(dlm 'observe 'r2 "fixture" "r2" 'demo (list (p107-atom 'calls (list "m2" "open")) (p107-atom 'calls (list "m2" "write")) (p107-atom 'calls (list "m2" "close"))))
(dlm 'run {a.rounds} 200000)
(print "PROGRESS " (p107-epoch *p107-state*) "\\n")
'''
    if a.fault:
        code += '(print "FAULT injected\\n")\n(car 1)\n'
    else:
        code += "(dlm 'close)\n(print \"DONE\\n\")\n"
    p = subprocess.run([str(ROOT / 'scripts' / 'run.sh'), 'proof', '/dev/stdin'],
                       input=code, text=True)
    return p.returncode


if __name__ == '__main__':
    sys.exit(main())
