"""Optional development check against 0066; never a runtime dependency."""
from pathlib import Path
import os
import random
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
reference = root.parent / 'dlm_v0.0066'
sys.path.insert(0, str(reference))
from dlm.kernel import Atom, Rule, closure

rng = random.Random(70)
base = Rule(Atom('reach', ('?x', '?y')), (Atom('edge', ('?x', '?y')),))
rec = Rule(Atom('reach', ('?x', '?z')),
           (Atom('reach', ('?x', '?y')), Atom('edge', ('?y', '?z'))))
program = '''(define x (dlm-var 'x))
(define y (dlm-var 'y))
(define z (dlm-var 'z))
(define rules (list
 (dlm-rule (dlm-atom 'reach x y) (dlm-atom 'edge x y))
 (dlm-rule (dlm-atom 'reach x z) (dlm-atom 'reach x y) (dlm-atom 'edge y z))))
'''
expected = []
for i in range(20):
    facts = {Atom('edge', (f'n{a}', f'n{b}')) for a in range(5)
             for b in range(5) if rng.random() < .18}
    expected.append(set(closure(facts, (base, rec))))
    forms = ' '.join(f"(dlm-atom 'edge '{a.args[0]} '{a.args[1]})" for a in sorted(facts))
    program += f'(println "CASE{i} " (dlm-closure (list {forms}) rules))\n'
p = subprocess.run([os.environ.get('MARU', str(root/'maru-compiler')), 'boot.l', str(root/'src/dlm/kernel.l'), '-'],
                   cwd=root, input=program, text=True, capture_output=True, check=True, timeout=30)
found = {}
for line in p.stdout.splitlines():
    match = re.search(r'CASE(\d+) ', line)
    if match and int(match[1]) not in found:
        found[int(match[1])] = {Atom(pred, (a, b)) for pred, a, b in re.findall(
            r'\(atom (\w+) \((\w+) (\w+)\)\)', line)}
assert len(found) == len(expected), p.stdout
for i, target in enumerate(expected):
    assert found[i] == target, (i, found[i] ^ target)
print('PASS: 20 fixed-seed closure comparisons against DLM 0066')
