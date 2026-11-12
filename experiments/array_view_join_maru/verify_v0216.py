#!/usr/bin/env python3
import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else 'array_join.out'
t = open(p).read()
def val(key):
    m = re.search(rf'^{re.escape(key)}\s+(-?\d+)\s*$', t, re.M)
    if not m: raise SystemExit(f'missing {key}')
    return int(m.group(1))
exp = {
    'REF': 2820,
    'REFSUM': 421590,
    'SIZE': 300,
    'JOIN1': 2820,
    'JOIN64': 180480,
    'JOIN4096': 11550720,
    'CHECK1': 421590,
    'CHECK64': 26981760,
    'AFTERFREE': -1,
}
for k, v in exp.items():
    got = val(k)
    if got != v: raise SystemExit(f'{k}: {got} != {v}')
print('V0216-ARRAY-VIEW-JOIN-PASS')
