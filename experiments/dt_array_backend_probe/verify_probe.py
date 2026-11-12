#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
exp=json.loads(Path('expected.json').read_text())
c=Path('c_selector.out').read_text()
m=Path('maru_case0.out').read_text()
def nums(line):
    return [float(x) for x in line.split()[1:]]
line=[l for l in c.splitlines() if l.startswith('C-SELECTOR')][0]
cs=nums(line)
line=[l for l in c.splitlines() if l.startswith('CASE ')][0]
valid=[int(x) for x in line.split()[3:]]
pick=int([l for l in c.splitlines() if l.startswith('C-PICK')][0].split()[1])
maru=[float(x)/65536.0 for x in re.findall(r'SCORES \(([^)]*)\)',m)[0].split()]
if valid != exp['valid']: raise SystemExit(f'valid {valid} != {exp["valid"]}')
if pick != exp['pick']: raise SystemExit(f'pick {pick} != {exp["pick"]}')
py_err=max(abs(a-b) for a,b in zip(cs,exp['selector']))
m_err=max(abs(a-b) for a,b in zip(cs,maru))
if py_err > 0.003: raise SystemExit(f'PyTorch selector error too large: {py_err}')
if m_err > 0.003: raise SystemExit(f'Maru selector error too large: {m_err}')
print(f'VALID {valid}')
print(f'PICK {pick}')
print(f'C_SELECTOR {cs}')
print(f'PY_SELECTOR {exp["selector"]}')
print(f'MARU_SELECTOR {maru}')
print(f'PY_MAX_ERR {py_err:.6e}')
print(f'MARU_MAX_ERR {m_err:.6e}')
print('DT-ARRAY-BACKEND-PARITY-PASS')
