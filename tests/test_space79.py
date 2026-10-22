"""Operating-rule oracles, not a benchmark promotion test."""
import itertools
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from sexp import Symbol as S, dumps, loads_many
from test_sequent import maru, valid, evaluate, P, Q, SIG
from test_session77 import batch
from test_repl import Live

PROBLEM=[S('problem'),S('classical-prop-v1'),SIG,
 [S('sequent'),S('classical-prop-v1'),[P],[[S('and'),P,P]]]]

class Space79Tests(unittest.TestCase):
    def test_graph_semantics_and_slices(self):
        rng=random.Random(79); base=[P,Q,[S('top')],[S('bottom')]]
        def form(d):
            if not d:return rng.choice(base)
            op=rng.choice(['not','and','or','imp'])
            return [S(op),form(d-1)]+([] if op=='not' else [form(d-1)])
        cases=[([],[])]+[([a],[b]) for a,b in itertools.product(base,repeat=2)]
        cases += [([form(2) for _ in range(rng.randrange(3))], [form(2) for _ in range(rng.randrange(3))]) for _ in range(400)]
        data=[[S('problem'),S('classical-prop-v1'),SIG,[S('sequent'),S('classical-prop-v1'),l,r]] for l,r in cases]
        out=maru('''(list-do p (read *standard-input*)
 (let* ((start (s79-proof-job (s79-new) 'p p)) (full (s79-run start 2000))
        (sliced (s79-run (s79-run start 5) 1995)) (result (dlm-nth (s79-job full 'p) 5)))
  (assert (equal full sliced) "event slicing")
  (if (= (dlm-nth result 1) 'proved)
   (assert (= (sq-verify (dlm-nth result 2) (dlm-nth p 3) (dlm-nth p 2) 10000) 'verified) "exported DAG"))
  (dump (list (dlm-nth result 1) (dlm-nth full 10))) (print "\\n")))''',dumps(data))
        rows=loads_many(out); self.assertEqual(len(rows),len(cases))
        for (left,right),(status,ticks) in zip(cases,rows):
            self.assertEqual(status,'proved' if valid(left,right) else 'countermodel',msg=(left,right,status))
        print(f'SPACE79-ORACLE {len(cases)} sequents, zero mismatches')

    def test_proof_annotations_and_beth(self):
        forms=[P,Q,[S('not'),P],[S('not'),Q],[S('and'),P,Q],[S('or'),P,Q],
               [S('imp'),P,Q],[S('imp'),Q,P],[S('top')],[S('bottom')]]
        pairs=list(itertools.product(forms,repeat=2))
        out=maru('''(list-do pair (read *standard-input*)
 (let* ((s (s79-run (i79-interpolate (s79-new) 'i '((p 0) (q 0)) (car pair) (dlm-nth pair 1)) 10000))
        (r (dlm-nth (s79-job s 'i) 5)))
   (dump (list (dlm-nth r 1) (dlm-nth r 2))) (print "\\n")))''',dumps(pairs))
        rows=loads_many(out); self.assertEqual(len(rows),len(pairs))
        for (a,b),(status,candidate) in zip(pairs,rows):
            self.assertEqual(status,'verified' if valid([a],[b]) else 'not-entailed',msg=(a,b,status))
            if status=='verified':
                for p,q in itertools.product((False,True),repeat=2):
                    v=dict(p=p,q=q)
                    self.assertTrue(not evaluate(a,v) or evaluate(candidate,v))
                    self.assertTrue(not evaluate(candidate,v) or evaluate(b,v))
        theories=[[S('and'),[S('imp'),P,Q],[S('imp'),Q,P]],
                  [S('or'),P,Q],[S('and'),P,[S('not'),P]],P,[S('not'),P],
                  [S('and'),[S('imp'),P,[S('not'),Q]],[S('imp'),[S('not'),Q],P]]]
        out=maru('''(list-do t (read *standard-input*)
 (let* ((s (s79-run (i79-beth (s79-new) 'b '((p 0) (q 0)) t '(pred p ())) 15000))
        (r (dlm-nth (s79-job s 'b) 5)))
  (dump (list (dlm-nth r 1) (if (= (dlm-nth r 1) 'verified) (dlm-nth (dlm-nth r 2) 4) ()))) (print "\\n")))''',dumps(theories))
        for theory,(status,candidate) in zip(theories,loads_many(out)):
            models=[dict(p=p,q=q) for p,q in itertools.product((False,True),repeat=2) if evaluate(theory,dict(p=p,q=q))]
            unique=all(a['p']==b['p'] for a,b in itertools.product(models,repeat=2) if a['q']==b['q'])
            self.assertEqual(status,'rejected' if not models else ('verified' if unique else 'not-defined'))
            if status=='verified':
                for v in models:self.assertEqual(evaluate(candidate,v),v['p'])
        print('SPACE79-INTERPOLATION 100 formula pairs; BETH six theories, zero mismatches')

    def test_snapshot_async_prefix_restart_and_forgery(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'s.sexp'; q=json.dumps(str(path)); live=Live()
            try:
                live.exchange(f"(space 'open {q})",rb'space-opened empty')
                live.exchange(f"(space 'study 'a '{dumps(PROBLEM)})",rb'queued 1')
                live.exchange("(space 'step 3)",rb'ticks 3')
                live.exchange("(space 'save-async)",rb'save-pending')
                live.exchange("(space 'step 100)",rb'patterns [1-9]')
                live.exchange('(e79-save-step)',rb'validating')
                live.exchange('(e79-save-step)',rb'validating')
                live.exchange('(e79-save-step)',rb'saved .*prefix-events 2')
                snap=loads_many(path.read_text())[0]
                self.assertEqual(snap[2][10],3) # immutable prefix, not later mutated graph
                live.exchange("(space 'close)",rb'space-closed')
            finally:live.close()
            saved=path.read_bytes(); snapshot=loads_many(saved.decode())[0]
            self.assertTrue(snapshot[2][8]); self.assertTrue(snapshot[2][12])
            forged=loads_many(saved.decode())[0]; forged[2][3][0][1][4]=S('failed')
            for bad in (dumps(forged).encode(),saved.replace(b'space-session79 1',b'space-session79 9'),b'(print "PWNED")',saved+b' (extra)'):
                path.write_bytes(bad)
                out=batch(f"(space 'open {q})\n(space 'save)\n")
                self.assertIn('rejected space-snapshot',out); self.assertNotIn('PWNED',out)
                self.assertEqual(path.read_bytes(),bad)
            path.write_bytes(saved)
            out=batch(f"(space 'open {q})\n(space 'job 'a)\n(space 'close)\n")
            self.assertIn('space-opened restored',out); self.assertIn('result proved',out)
            self.assertTrue(Path(str(path)+'.previous').exists())

    def test_native_lock_changed_checkpoint_and_idle(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'s.sexp';q=json.dumps(str(path));live=Live()
            try:
                live.exchange(f"(space 'open {q})",rb'space-opened empty')
                self.assertIn('rejected locked-or-path',batch(f"(space 'open {q})\n"))
                live.exchange(f"(space 'study 'a '{dumps(PROBLEM)})",rb'queued 1')
                pid=live.p.pid
                live.exchange("(space 'start 20)",rb'Space quiescent:')
                live.exchange('(+ 20 22)',rb'42\r?\nmaru>')
                self.assertEqual(pid,live.p.pid)
                live.exchange("(space 'save)",rb'saved ')
                good=path.read_bytes();bad=good.replace(b'space-session79 1',b'space-session79 2');path.write_bytes(bad)
                live.exchange("(space 'save)",rb'rejected checkpoint-changed-or-write')
                self.assertEqual(path.read_bytes(),bad)
            finally:live.close()

    def test_scope_isolation_alternatives_and_layout(self):
        out=maru('''(define s (s79-program-job (s79-new) 'p
 '((choose (((assume (pred p ())) (fail no))
            ((ask (problem classical-prop-v1 ((p 0)) (sequent classical-prop-v1 () ((pred p ()))))) (accept leaked)))))))
(set s (s79-run s 1000))
(dump (dlm-nth (s79-job s 'p) 3)) (print "\\n")
(define a (s79-proof-job (s79-new) 'a '(problem classical-prop-v1 ((p 0)) (sequent classical-prop-v1 ((pred p ())) ((pred p ()))))))
(define b (e79-transition a '(place 0 (100 -5 2))))
(dump (equal (dlm-nth (s79-job (s79-run a 100) 'a) 5) (dlm-nth (s79-job (s79-run b 100) 'a) 5))) (print "\\n")
(define c (s79-run (s79-program-job (s79-new) 'c '((choose (((accept a)) ((accept b)))))) 100))
(dump (dlm-nth (s79-job c 'c) 5)) (print "\\n")
(set c (s79-run (s79-program-resume c 'c true) 100))
(dump (dlm-nth (s79-job c 'c) 5)) (print "\\n")''')
        rows=loads_many(out)
        self.assertEqual(rows[0],'exhausted');self.assertTrue(rows[1])
        self.assertEqual(rows[2][1],'a');self.assertEqual(rows[3][1],'b')

if __name__=='__main__':unittest.main()
