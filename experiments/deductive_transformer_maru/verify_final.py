#!/usr/bin/env python3
"""E10: final taxonomy + end-to-end verification for the DT × MNIST loop."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def run(cmd, timeout=600):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, shell=True)
    if r.returncode != 0:
        print(r.stdout); print(r.stderr, file=sys.stderr)
        raise SystemExit(f'command failed: {cmd}')
    return r.stdout

checks = []
def ck(name, ok, detail=''):
    checks.append({'name': name, 'pass': bool(ok), 'detail': str(detail)})
    print(('PASS ' if ok else 'FAIL ') + name + ((' ' + str(detail)) if detail else ''))

# baseline: Maru perceptron + proof
base = run('./verify_learn.sh')
ck('baseline DT-MARU-LEARN-PASS', 'DT-MARU-LEARN-PASS' in base)
ck('baseline 8/10', 'held-out answer 8/10 8/10' in base)
ck('baseline proof 10/10', 'all cases proof-valid 10' in base)

# validated library: 150 train / 40 validation
lib = run('./run_library_split.sh', timeout=900)
m = re.search(r'K 5 LIB (\d+) ACC (\d+)/10', lib)
ck('library K5 emitted', bool(m), m.groups() if m else '')
ck('library K5 accuracy 9/10', bool(m) and m.group(2) == '9', m.group(2) if m else '')
ck('library K5 proof 10/10', 'K5-PROOF 10/10' in lib)

# taxonomy
tax = {
    'baseline_perceptron': {'correct': 8, 'proof': 10, 'semantic_wrong_proof_valid': 2},
    'validated_library': {'correct': 9, 'proof': 10, 'semantic_wrong_proof_valid': 1},
    'no_mask': {'label': 9, 'proof_valid': 1},
    'centroid': {'correct': 6, 'proof': 10},
    'label_free_gate': {'correct': 8, 'proof': 10},
}
ok = all(c['pass'] for c in checks)
(ROOT/'verification_final.json').write_text(json.dumps({
    'pass': ok, 'checks': checks, 'taxonomy': tax,
    'library_k5': {'lib': int(m.group(1)) if m else None, 'acc': int(m.group(2)) if m else None},
}, indent=2)+'\n')
print('DT-MNIST-FINAL-PASS' if ok else 'DT-MNIST-FINAL-FAIL')
raise SystemExit(0 if ok else 1)
