"""Independent truth tables, native replay, and live branch control."""
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'adapters'))
from sexp import Symbol as S, dumps, loads_many
from test_sequent import maru, valid, evaluate, P, Q, SIG
from test_session77 import batch
from test_repl import Live

PROBLEM = [S('problem'),S('classical-prop-v1'),SIG,
    [S('sequent'),S('classical-prop-v1'),[[S('imp'),P,Q],P],[Q]]]

class Reasoning78Tests(unittest.TestCase):
    def test_truth_tables_and_tick_slicing(self):
        rng=random.Random(78)
        base=[P,Q,[S('top')],[S('bottom')]]
        def form(depth):
            if not depth: return rng.choice(base)
            op=rng.choice(['not','and','or','imp'])
            return [S(op),form(depth-1)]+([] if op=='not' else [form(depth-1)])
        cases=[([],[])] + [([a],[b]) for a,b in itertools.product(base,repeat=2)]
        cases += [([form(2) for _ in range(rng.randrange(3))],
                    [form(2) for _ in range(rng.randrange(3))]) for _ in range(400)]
        data=[[S('problem'),S('classical-prop-v1'),SIG,
               [S('sequent'),S('classical-prop-v1'),l,r]] for l,r in cases]
        out=maru('''(list-do p (read *standard-input*)
 (let* ((fresh (n78-proof p ())) (full (n78-run fresh 1000))
        (sliced (n78-run (n78-run fresh 3) 997)) (a (car (dlm-nth full 4))))
   (assert (equal full sliced) "slicing")
   (dump (list (dlm-nth a 2) (dlm-nth full 6))) (print "\\n")))''',dumps(data))
        rows=loads_many(out); self.assertEqual(len(rows),len(cases))
        for (left,right), (kind,ticks) in zip(cases,rows):
            self.assertEqual(kind,'proof' if valid(left,right) else 'countermodel',msg=(left,right))
        print(f'ND78-ORACLE {len(cases)} sequents, four valuations each, zero mismatches')

    def test_beth_craig_against_model_enumeration(self):
        valuations=list(itertools.product((False,True),repeat=2))
        def dnf(mask):
            cubes=[[S('and'), P if p else [S('not'),P], Q if q else [S('not'),Q]]
                   for i,(p,q) in enumerate(valuations) if mask & (1<<i)]
            if not cubes: return [S('bottom')]
            out=cubes[0]
            for c in cubes[1:]: out=[S('or'),out,c]
            return out
        theories=[dnf(m) for m in range(16)]
        out=maru('''(list-do theory (read *standard-input*)
 (let ((b (b78-beth '((p 0) (q 0)) theory '(pred p ()) 2000)))
  (dump (list (dlm-nth b 1) (if (= (dlm-nth b 1) 'verified) (dlm-nth b 3) ()))) (print "\\n")))''',dumps(theories))
        for mask,(status,candidate) in enumerate(loads_many(out)):
            unique=all(not ((mask & (1<<j)) and (mask & (1<<k)))
                       for j,(p,q) in enumerate(valuations)
                       for k,(r,s) in enumerate(valuations) if q==s and p!=r)
            expected='rejected' if mask==0 else ('verified' if unique else 'not-certified')
            self.assertEqual(status,expected,msg=mask)
            if status=='verified':
                for i,(p,q) in enumerate(valuations):
                    if mask & (1<<i): self.assertEqual(evaluate(candidate,dict(p=p,q=q)),p)
                self.assertNotIn('p',dumps(candidate).split())
        pairs=[(i,j) for i in range(16) for j in range(16)]
        out=maru('''(list-do pair (read *standard-input*)
 (let ((c (b78-craig '((p 0) (q 0)) (car pair) (dlm-nth pair 1) 2000)))
  (dump (list (dlm-nth c 1) (dlm-nth c 2))) (print "\\n")))''',
                 dumps([[theories[i],theories[j]] for i,j in pairs]))
        for (a,b),(status,candidate) in zip(pairs,loads_many(out)):
            self.assertEqual(status,'verified' if a & ~b == 0 else 'not-certified',msg=(a,b))
            if status=='verified':
                for k,(p,q) in enumerate(valuations):
                    v=evaluate(candidate,dict(p=p,q=q))
                    if a & (1<<k): self.assertTrue(v)
                    if v: self.assertTrue(b & (1<<k))
        print('DEFINABILITY-ORACLE 16 Beth theories, 256 Craig pairs, zero mismatches')

    def test_native_snapshot_restores_continuation_and_rejects_forgery(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'reasoning.sexp'; q=json.dumps(str(path))
            out=batch(f"(dlm 'nd-open {q})\n(dlm 'think '{dumps(PROBLEM)})\n(dlm 'advance 3)\n(dlm 'nd-close)\n")
            self.assertIn('incomplete ticks 3',out)
            saved=path.read_bytes()
            snapshot=loads_many(saved.decode())[0]
            self.assertEqual(snapshot[0],'reasoning-session78')
            self.assertTrue(snapshot[2][2][3])  # saved live queue
            # Runtime frames are checked against event replay, never trusted directly.
            forged=loads_many(saved.decode())[0]; forged[2][2][3][0][3]=[]
            for bad in (dumps(forged).encode(), saved.replace(b'reasoning-session78 1',b'reasoning-session78 2'),
                        b'(print "PWNED")', saved+b' (extra)'):
                path.write_bytes(bad)
                out=batch(f"(dlm 'nd-open {q})\n(dlm 'nd-save)\n")
                self.assertIn('rejected snapshot',out); self.assertIn('not-attached',out)
                self.assertNotIn('PWNED',out); self.assertEqual(path.read_bytes(),bad)
            path.write_bytes(saved)
            out=batch(f"(dlm 'nd-open {q})\n(dlm 'advance 100)\n(dlm 'learn-proof)\n(dlm 'proof-library)\n(dlm 'nd-close)\n")
            self.assertIn('answered',out); self.assertIn('pattern78',out)
            final=loads_many(path.read_text())[0]
            self.assertEqual(final[2][2][6],14)
            self.assertTrue(Path(str(path)+'.previous').exists())
            out=batch(f"(dlm 'nd-open {q})\n(dlm 'proof-library)\n(dlm 'nd-close)\n")
            self.assertIn('pattern78',out)

    def test_branch_suspension_restart_and_alternative(self):
        program="'((choose (((assume local-only) (bind x a) (suspend need-evidence) (accept first)) ((bind x b) (fail rejected)))))"
        with tempfile.TemporaryDirectory() as d:
            q=json.dumps(str(Path(d)/'p.sexp'))
            out=batch(f"(dlm 'nd-open {q})\n(dlm 'choose-program {program})\n(dlm 'advance 50)\n(dlm 'nd-close)\n")
            self.assertIn('suspended',out); self.assertIn('failed 1',out)
            out=batch(f"(dlm 'nd-open {q})\n(dlm 'resume-branches)\n(dlm 'advance 50)\n(dlm 'branches)\n(dlm 'nd-close)\n")
            self.assertIn('provisional first (context78 ((x a)) (local-only)',out)
        out=maru("""(define m (n78-run (n78-program '((choose (((accept a)) ((accept b)))))) 10))
(dump (list (dlm-nth (car (dlm-nth m 4)) 3)
 (dlm-nth (car (dlm-nth (n78-run (n78-next m) 10) 4)) 3)))""")
        self.assertEqual(loads_many(out),[[S('a'),S('b')]])

    def test_lock_and_atomic_failed_admission(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'p.sexp'; q=json.dumps(str(path)); live=Live()
            try:
                live.exchange(f"(dlm 'nd-open {q})",rb'reasoning-opened missing')
                live.exchange(f"(dlm 'think '{dumps(PROBLEM)})",rb'incomplete ticks 0')
                self.assertIn('rejected lock-or-path',batch(f"(dlm 'nd-open {q})\n"))
                good=path.read_bytes(); bad=good.replace(b'reasoning-session78 1',b'reasoning-session78 9')
                path.write_bytes(bad)
                live.exchange("(dlm 'advance 3)",rb'rejected checkpoint')
                live.exchange("(print (n78-summary (dlm-nth *r78-state* 2)))",rb'incomplete ticks 0')
                self.assertEqual(path.read_bytes(),bad)
            finally: live.close()

    def test_idle_reasoning_same_repl(self):
        live=Live()
        try:
            pid=live.p.pid
            live.exchange(f"(dlm 'think '{dumps(PROBLEM)})",rb'incomplete ticks 0')
            live.exchange("(dlm 'nd-start 30)",rb'Reasoning answer checked; new proof patterns: 1')
            live.exchange("(dlm 'proof-library)",rb'pattern78')
            live.exchange('(+ 20 22)',rb'42\r?\nmaru>')
            self.assertEqual(pid,live.p.pid)
        finally: out=live.close()
        self.assertEqual(live.p.returncode,0,out[-3000:])

if __name__=='__main__': unittest.main()
