#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ref=json.loads(Path('expected_all.json').read_text())
c=Path('c_infer_all.out').read_text()
maru=Path('maru_main_10.out').read_text()
rows={}
for line in c.splitlines():
    m=re.match(r'RESULT (\d+) VALID (.*?) SEL (.*?) PICK (\d+) HEAD (-?\d+)',line)
    if not m: continue
    rows[int(m.group(1))]={'valid':[int(x) for x in m.group(2).split()],
        'selector':[float(x) for x in m.group(3).split()],
        'pick':int(m.group(4)),'head':int(m.group(5))}
if len(rows)!=10: raise SystemExit(f'rows {len(rows)}')
py_err=0; maru_err=0; picks=0
for i,r in enumerate(ref):
    x=rows[i]
    if x['valid']!=r['valid']: raise SystemExit(f'valid {i}')
    if x['pick']!=r['pick']: raise SystemExit(f'pick {i}: {x["pick"]} != {r["pick"]}')
    picks+=1
    py_err=max(py_err,max(abs(a-b) for a,b in zip(x['selector'],r['selector'])))
    mm=re.search(rf'^CASE {i} .* SCORES \(([^)]*)\)',maru,re.M)
    if not mm: raise SystemExit(f'maru row {i}')
    ms=[float(v)/65536.0 for v in mm.group(1).split()]
    maru_err=max(maru_err,max(abs(a-b) for a,b in zip(x['selector'],ms)))
if picks!=10: raise SystemExit('picks')
if py_err>0.003: raise SystemExit(f'py err {py_err}')
if maru_err>0.003: raise SystemExit(f'maru err {maru_err}')
print(f'VALID 10/10')
print(f'PICKS {picks}/10')
print(f'PY_MAX_ERR {py_err:.6e}')
print(f'MARU_MAX_ERR {maru_err:.6e}')
print('DT-FULL-INFER-C-PASS')
