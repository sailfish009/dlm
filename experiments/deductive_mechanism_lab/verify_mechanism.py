#!/usr/bin/env python3
from pathlib import Path
t=Path('mechanism.out').read_text()
for s in ['WEB 8 FACTS 6 RULES0 2 STORE 2',
          'M2 BEFORE 1/3 AFTER 3/3 LEARNED 1',
          'M2 SOURCE frontier-signature ENUMERATED false',
          'M3 FRONTIER (missing107 (atom isa (MNIST pixel-grid))) ACQ acq-frontier HELD0 1/2 HELD1 2/2',
          'RETRACT 1/3 PERMUTE 3/3 SCRAMBLE 0/3',
          'NEG 0 ACQ-TIER synthetic',
          'done-mechanism']:
    if s not in t: raise SystemExit('missing: '+s)
print('M2 BEFORE 1/3 -> AFTER 3/3')
print('M2 SOURCE frontier-signature (no fact-pair enumeration)')
print('M3 HELD 1/2 -> 2/2 via frontier missing atom')
print('RETRACT 1/3 PERMUTE 3/3 SCRAMBLE 0/3')
print('V0223-DEDUCTIVE-MECHANISM-DISCOVERY-PASS')
