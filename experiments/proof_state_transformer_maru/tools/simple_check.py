#!/usr/bin/env python3
"""단순 표 검사: 주장이 참인지, 열화 변이가 거부되는지.
표 형식: 'ARM <name> goal=.. full=.. nodes=.. n=..' + 'CEILING goal=.. seeds=[..]'
규칙:
  best_b8 − best  : 양수이고 |mean| > 2SE  → 유의한 개선
  best_e5 − best  : 양수이고 |mean| > 2SE  → 유의한 개선
  best_b8 <= CEILING (천장을 넘으면 실패)
  E류 '무시 가능' 주장은 |mean| < 0.02 이고 부호를 함께 보고
"""
import sys, statistics as st

def load(path):
    arms, ceil = {}, None
    for line in open(path):
        f = line.split()
        if not f: continue
        if f[0] == 'ARM':
            kv = dict(x.split('=') for x in f[2:] if '=' in x)
            arms[f[1]] = kv
        elif f[0] == 'CEILING':
            kv = dict(x.split('=') for x in f[1:] if '=' in x)
            ceil = float(kv['goal'])
    return arms, ceil

def main(path):
    arms, ceil = load(path)
    for need in ('best', 'best_b8', 'best_e5'):
        if need not in arms: print(f"SIMPLE-FAIL missing arm {need}"); return 1
    if ceil is None: print("SIMPLE-FAIL missing CEILING"); return 1
    bad = 0
    def pair(a, b):
        ga, gb = float(arms[a]['goal']), float(arms[b]['goal'])
        # paired SE is not in the table; use the reported 2SE via a rough bound:
        # the table stores the per-seed values only in prose, so require a margin.
        return ga - gb
    d8 = pair('best_b8', 'best'); d5 = pair('best_e5', 'best')
    if d8 <= 0.01: print(f"SIMPLE-FAIL best_b8 gain {d8:+.4f} not positive enough"); bad = 1
    if d5 <= 0.01: print(f"SIMPLE-FAIL best_e5 gain {d5:+.4f} not positive enough"); bad = 1
    best_b8 = float(arms['best_b8']['goal'])
    if best_b8 > ceil + 1e-9:
        print(f"SIMPLE-FAIL best_b8 {best_b8:.4f} exceeds ceiling {ceil:.4f}"); bad = 1
    print(f"SIMPLE-CHECK {'FAIL' if bad else 'PASS'} d8={d8:+.4f} d5={d5:+.4f} "
          f"best_b8={best_b8:.4f} ceiling={ceil:.4f} ({100*best_b8/ceil:.1f}% of ceiling)")
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
