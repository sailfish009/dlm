#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ref=json.loads(Path('expected_all.json').read_text())
exp=[x['pick'] for x in ref]
t=Path('c_train_50.out').read_text()
p=[int(re.search(r'PICK (\d+)',l).group(1)) for l in t.splitlines() if l.startswith('FOLD ') and 'PICK' in l]
if p!=exp:
    print('expected',exp); print('actual',p); sys.exit(1)
print('TRAIN_PICKS 10/10')
print('DT-TRAIN-C-PICK-PARITY-PASS')
