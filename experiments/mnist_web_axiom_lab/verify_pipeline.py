#!/usr/bin/env python3
import re
from pathlib import Path
web=Path('mnist_web.out').read_text()
def get(k):
    m=re.search(rf'^{re.escape(k)}\s+(.*)$',web,re.M)
    if not m: raise SystemExit(f'missing {k}')
    return m.group(1)
assert 'WEB OBS 8 ACCUM1 4 ACCUM2 8' in web
assert 'FACTS 6 RULES 2 AXIOMS 2 ACTIVE 2 PROV 2' in web
assert 'GRAPH ok' in web
assert 'NEG 0 (want 0)' in web
base=re.search(r'^BASE (\d+)/(\d+) HELD (\d+)/(\d+)',web,re.M)
noweb=re.search(r'^NOWEB (\d+)/(\d+) SINGLE (\d+)/(\d+) SHUF (\d+)/(\d+)',web,re.M)
assert base and noweb
assert int(base.group(1)) >= int(noweb.group(1))
assert 'MINIMAL ' in web
inf=Path('dt_infer.out').read_text()
trn=Path('dt_train.out').read_text()
assert 'DT-FULL-INFER-C-PASS' in inf
assert 'DT-TRAIN-C-PICK-PARITY-PASS' in trn
print(f'WEB_BASE {base.group(1)}/{base.group(2)} WEB_NOWEB {noweb.group(1)}/{noweb.group(2)}')
print('DT_INFER_PASS')
print('DT_TRAIN_PASS')
print('WEB_AXIOM_DT_COUPLING none (reported explicitly)')
print('V0221-MNIST-WEB-AXIOM-PIPELINE-PASS')
