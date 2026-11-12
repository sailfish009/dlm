#!/usr/bin/env python3
from pathlib import Path
p=Path('proposer.out').read_text(); g=Path('gate.out').read_text()
for s in ['TRANSFORMER_TOP1 0/4','BASELINE_TOP1 4/4']:
    if s not in p: raise SystemExit('missing '+s)
for s in ['GATE OBS 4 FACTS 2 RULES 2 RULES-USED 2 PROOF proof','done-web-axiom-gate']:
    if s not in g: raise SystemExit('missing '+s)
print('TRANSFORMER_TOP1 0/4 (negative; insufficient held-out generalization)')
print('BASELINE_TOP1 4/4')
print('GATE PROOF proof')
print('V0224-WEB-AXIOM-TRANSFORMER-PROBE-PASS')
