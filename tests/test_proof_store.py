import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from sexp import Symbol as S, dumps, loads_many

class ProofStoreTests(unittest.TestCase):
    def call(self, store, problem, budget=100):
        return subprocess.run([str(ROOT/'scripts/proof.sh'), str(problem), str(budget)],
            env=dict(os.environ, STORE=str(store)),text=True,capture_output=True,timeout=30)
    def test_restart_strings_and_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); store = d/'store'; problem = d/'problem.sexp'
            name = 'name (spaces) "quoted" \\ slash'
            atom = [S('pred'),name,[]]
            problem.write_text(dumps([S('problem'),S('classical-prop-v1'),[[name,0]],
                [S('sequent'),S('classical-prop-v1'),[atom],[atom]]]))
            for _ in range(2):
                p = self.call(store,problem)
                self.assertEqual(p.returncode,0,p.stderr[:2000])
                self.assertIn('proved',p.stdout)
            state = store/'state.sexp'
            loaded = loads_many(state.read_text())[0]
            self.assertEqual(loaded[2][2][0][0],name)
            original = state.read_bytes()
            loaded[6] = '0'*64
            forged_hash = dumps(loaded).encode()
            for corrupt in (original.replace(b'g3c76-v1',b'g3c76-forged'),
                            original.replace(b' init ',b' fake '), forged_hash, original + b' (extra)',
                            original[:-3] + b'00)', b'(proof-store-v1 truncated)'):
                state.write_bytes(corrupt)
                before = hashlib.sha256(corrupt).hexdigest()
                p = self.call(store,problem)
                self.assertNotEqual(p.returncode,0)
                self.assertEqual(hashlib.sha256(state.read_bytes()).hexdigest(),before)
                self.assertFalse(list(store.glob('.state.*')))
            state.write_bytes(original)
            problem.write_text('(system "false")')
            p = self.call(store,problem)
            self.assertNotEqual(p.returncode,0)
            self.assertEqual(state.read_bytes(),original)
    def test_countermodel_and_budget(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); problem = d/'p.sexp'; store=d/'store'
            problem.write_text('(problem classical-prop-v1 ((p 0)) (sequent classical-prop-v1 () ((pred p ()))))')
            p = self.call(store,problem,0)
            self.assertEqual(p.returncode,0,p.stderr[:1000]); self.assertIn('incomplete',p.stdout)
            p = self.call(store,problem,10)
            self.assertEqual(p.returncode,0,p.stderr[:1000]); self.assertIn('countermodel',p.stdout)
            self.assertEqual(len(list(store.glob('*.sexp'))),3)
    def test_lock(self):
        import fcntl
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); (d/'store').mkdir()
            with (d/'store/lock').open('w') as f:
                fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
                p = self.call(d/'store', ROOT/'experiments/proof/problem.sexp')
                self.assertNotEqual(p.returncode,0); self.assertIn('in use',p.stderr)

if __name__ == '__main__': unittest.main()
