#!/usr/bin/env python3
"""Parse E27 five-axiom Maru subset output into a JSON reward table."""
import json, re, sys
from pathlib import Path
src = Path(sys.argv[1] if len(sys.argv) > 1 else 'experiments/dt3_pool5/pool5.out')
rows = []
for line in src.read_text().splitlines():
    m = re.match(r'POOL5 ids=\(([^)]*)\) rules=(\d+) proof=(\w+)', line)
    if m:
        ids = tuple(m.group(1).split())
        rows.append({'ids': list(ids), 'rules': int(m.group(2)), 'proof': m.group(3)})
goals = []
for line in src.read_text().splitlines():
    m = re.match(r'GOAL5 \(atom isa \((\S+) (\S+)\)\) proof=(\w+)', line)
    if m:
        goals.append({'query': [m.group(1), m.group(2)], 'proof': m.group(3)})
proofs = [r for r in rows if r['proof'] == 'proof']
minimal = min(proofs, key=lambda r: (len(r['ids']), r['ids'])) if proofs else None
out = {'rows': rows, 'proof_count': len(proofs), 'minimal_proof': minimal, 'unseen_bindings': goals}
Path('experiments/dt3_pool5/rewards_pool5.json').write_text(json.dumps(out, indent=2))
print('rows', len(rows), 'proof', len(proofs))
print('minimal', minimal['ids'] if minimal else None)
for g in goals:
    print('unseen', g['query'], g['proof'])
