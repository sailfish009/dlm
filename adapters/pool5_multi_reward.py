#!/usr/bin/env python3
"""Parse dog and sparrow five-axiom actual p-prove tables."""
import json, re, sys
from pathlib import Path
src = Path(sys.argv[1] if len(sys.argv) > 1 else 'experiments/dt3_pool5/pool5.out')
text = src.read_text()
def table(tag):
    rows = []
    for line in text.splitlines():
        m = re.match(tag + r' ids=\(([^)]*)\).*proof=(\w+)', line)
        if m:
            rows.append({'ids': m.group(1).split(), 'proof': m.group(2)})
    proofs = [r for r in rows if r['proof'] == 'proof']
    minimal = min(proofs, key=lambda r: (len(r['ids']), r['ids'])) if proofs else None
    return rows, minimal
dog, dog_min = table('POOL5')
spa, spa_min = table('SPOOL5')
out = {'dog': {'rows': dog, 'minimal_proof': dog_min},
       'sparrow': {'rows': spa, 'minimal_proof': spa_min}}
Path('experiments/dt3_pool5/rewards_multi.json').write_text(json.dumps(out, indent=2))
print('dog rows', len(dog), 'proof', sum(r['proof']=='proof' for r in dog), 'min', dog_min['ids'])
print('sparrow rows', len(spa), 'proof', sum(r['proof']=='proof' for r in spa), 'min', spa_min['ids'])
