#!/usr/bin/env python3
import re
from pathlib import Path
t=Path('loop.out').read_text()
def has(s):
    if s not in t: raise SystemExit(f'missing: {s}')
for s in ['WEB 8 FACTS 6 RULES0 2','BEFORE 1/3 FAILED 2','LEARNED 1 RULES1 3',
          'AFTER 3/3 HELD0 1/2 HELD1 2/2','NEG 0 SCRAMBLE 0/3',
          'PROV-ACQ synthetic','done-transitivity-loop']:
    has(s)
print('BEFORE 1/3 -> AFTER 3/3')
print('LEARNED 1 (transitivity)')
print('HELD0 1/2 -> HELD1 2/2 (acquisition)')
print('NEG 0 SCRAMBLE 0/3')
print('V0222-CLOSED-LOOP-TRANSITIVITY-ACQUISITION-PASS')
