#!/usr/bin/env python3
"""Verify Maru-native perceptron training of the hard-binding DT readout."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
ref = {r['case']: r for r in json.loads((ROOT/'reference_folds.json').read_text())}
r = subprocess.run(['./run_learn.sh'], cwd=ROOT, capture_output=True, text=True, timeout=600)
if r.returncode != 0:
    print(r.stdout); print(r.stderr, file=sys.stderr)
    raise SystemExit(f'run_learn.sh failed rc={r.returncode}')
rows = []
pat = re.compile(r'CASE (\d+) IMG (\d+) VALID \((.*?)\) PICK (\d+) HEAD (-?\d+) LABEL (\d+) PROOF (\d+)')
for line in r.stdout.splitlines():
    m = pat.search(line)
    if m:
        rows.append({'case': int(m.group(1)), 'img': int(m.group(2)),
                     'valid': [int(x) for x in m.group(3).split()],
                     'pick': int(m.group(4)), 'head': int(m.group(5)),
                     'label': int(m.group(6)), 'proof': int(m.group(7))})
checks = []
def ck(n, ok, d=''):
    checks.append({'name': n, 'pass': bool(ok), 'detail': str(d)})
    print(('PASS ' if ok else 'FAIL ') + n + ((' ' + str(d)) if d else ''))
ck('10 cases emitted', len(rows) == 10, len(rows))
ck('all cases proof-valid', all(x['proof'] == 1 for x in rows), sum(x['proof'] for x in rows))
correct = sum(x['head'] == x['label'] for x in rows)
ck('held-out answer 8/10', correct == 8, f'{correct}/10')
ck('picks match PyTorch reference', all(x['pick'] == ref[x['case']]['pick'] for x in rows))
ck('valid rule sets match', all(x['valid'] == ref[x['case']]['valid'] for x in rows))
ok = all(c['pass'] for c in checks)
(ROOT/'verification_learn.json').write_text(json.dumps({'pass': ok, 'checks': checks, 'rows': rows, 'correct': correct}, indent=2)+'\n')
print('DT-MARU-LEARN-PASS' if ok else 'DT-MARU-LEARN-FAIL')
raise SystemExit(0 if ok else 1)
