#!/usr/bin/env python3
"""Verify the native Maru deductive-transformer inference against PyTorch exports."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
Q = 65536
ref = json.loads((ROOT/'reference_folds.json').read_text())
r = subprocess.run(['./run.sh'], cwd=ROOT, capture_output=True, text=True, timeout=600)
if r.returncode != 0:
    print(r.stdout); print(r.stderr, file=sys.stderr)
    raise SystemExit(f"run.sh failed rc={r.returncode}")

rows = []
pat = re.compile(r'CASE (\d+) VALID \((.*?)\) PICK (\d+) HEAD (-?\d+) LABEL (\d+) PROOF (\d+) SCORES \((.*?)\)')
for line in r.stdout.splitlines():
    m = pat.search(line)
    if m:
        rows.append({
            'case': int(m.group(1)),
            'valid': [int(x) for x in m.group(2).split()],
            'pick': int(m.group(3)),
            'head': int(m.group(4)),
            'label': int(m.group(5)),
            'proof': int(m.group(6)),
            'scores': [int(x)/Q for x in m.group(7).split()],
        })

checks = []
def ck(name, ok, detail=''):
    checks.append({'name': name, 'pass': bool(ok), 'detail': str(detail)})
    print(('PASS ' if ok else 'FAIL ') + name + ((' ' + str(detail)) if detail else ''))

ck('10 cases emitted', len(rows) == 10, len(rows))
ck('case ids 0..9', [x['case'] for x in rows] == list(range(10)))
ck('valid rule sets match PyTorch', all(x['valid'] == ref[x['case']]['valid'] for x in rows))
ck('selected rules match PyTorch', all(x['pick'] == ref[x['case']]['pick'] for x in rows))
ck('selected heads match PyTorch', all(x['head'] == ref[x['case']]['head'] for x in rows))
mx = max(max(abs(a-b) for a, b in zip(x['scores'], ref[x['case']]['selector'])) for x in rows)
ck('selector max abs error < 0.01', mx < 0.01, f'{mx:.6f}')
ck('proof gate 10/10', all(x['proof'] == 1 for x in rows), sum(x['proof'] for x in rows))
correct = sum(ref[x['case']]['correct'] for x in rows)
ck('held-out answer 8/10', correct == 8, f'{correct}/10')
ck('failures are cases 0 and 6', [x['case'] for x in rows if ref[x['case']]['correct'] == 0] == [0, 6])

ok = all(c['pass'] for c in checks)
(ROOT/'verification.json').write_text(json.dumps({
    'pass': ok, 'checks': checks, 'rows': rows,
    'correct': correct, 'selector_max_abs_error': mx,
}, indent=2) + '\n')
print('DT-MARU-VERIFY-PASS' if ok else 'DT-MARU-VERIFY-FAIL')
raise SystemExit(0 if ok else 1)
