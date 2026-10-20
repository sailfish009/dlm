"""Independent finite truth-table oracle; no FLD labels or successor reuse."""
import itertools
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'adapters'))
from sexp import Symbol as S, dumps, loads_many

P, Q = [S('pred'), S('p'), []], [S('pred'), S('q'), []]
SIG = [[S('p'),0],[S('q'),0]]

def evaluate(f, values):
    tag = f[0]
    if tag == 'pred': return values[f[1]]
    if tag == 'top': return True
    if tag == 'bottom': return False
    if tag == 'not': return not evaluate(f[1], values)
    a, b = evaluate(f[1],values), evaluate(f[2],values)
    return {'and':a and b,'or':a or b,'imp':not a or b}[tag]

def valid(left, right):
    return all(not all(evaluate(f,v) for f in left) or any(evaluate(f,v) for f in right)
        for v in (dict(zip(('p','q'),bits)) for bits in itertools.product((False,True),repeat=2)))

def maru(code, data=''):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.l') as f:
        f.write(code); f.flush()
        p = subprocess.run([str(ROOT/'scripts/run.sh'),'proof',f.name], input=data,
                           text=True,capture_output=True,timeout=120)
    if p.returncode: raise AssertionError(p.stderr[:4000]+p.stdout[:4000])
    return p.stdout

class OracleTests(unittest.TestCase):
    def test_exhaustive_small_sequents(self):
        base = [P,Q,[S('top')],[S('bottom')]]
        forms = base + [[S('not'),a] for a in base] + [[S(op),a,b] for op in ('and','or','imp') for a in base for b in base]
        cases = [([a],[b]) for a in forms for b in forms] + [([], [a]) for a in forms]
        rng = random.Random(76)
        def form(depth):
            if depth == 0: return rng.choice(base)
            op = rng.choice(['not','and','or','imp'])
            return [S(op),form(depth-1)] + ([] if op == 'not' else [form(depth-1)])
        cases += [([form(2) for _ in range(rng.randrange(3))], [form(2) for _ in range(rng.randrange(3))]) for _ in range(200)]
        data = [[S('problem'),S('classical-prop-v1'),SIG,[S('sequent'),S('classical-prop-v1'),l,r]] for l,r in cases]
        output = maru('''(define *oracle-input* (read *standard-input*))
(list-do p *oracle-input* (dump (sq-search p 1000 'fixed)) (print "\\n"))
''', dumps(data))
        results = loads_many(output)
        self.assertEqual(len(results),len(cases))
        for (left,right), r in zip(cases,results):
            self.assertEqual(r[1], 'proved' if valid(left,right) else 'countermodel', msg=(left,right,r))
        print(f'ORACLE {len(cases)} sequents, all 4 valuations each, zero mismatches')

    def test_checker_without_search_loaded(self):
        # Checker cannot secretly rely on the search successor path.
        code = '''(require "src/dlm/kernel.l")
(require "src/dlm/formula.l") (require "src/dlm/sequent.l")
(require "src/dlm/sequent-check.l")
(assert (= (sq-verify
 '(certificate classical-prop-v1 0 ((proof-node 0 (sequent classical-prop-v1 ((pred p ())) ((pred p ()))) init (both 0 0) () ())))
 '(sequent classical-prop-v1 ((pred p ())) ((pred p ()))) '((p 0)) 10) 'verified) "isolated checker")
(print "isolated checker passed\\n")'''
        import os
        with tempfile.NamedTemporaryFile(mode='w',suffix='.l') as f:
            f.write(code); f.flush()
            p = subprocess.run([os.environ.get('MARU',str(ROOT/'maru-compiler')),'boot.l',f.name],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr[:2000])

if __name__ == '__main__': unittest.main()
