import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from sexp import Symbol as S, dumps, loads_many
from test_repl import Live

def batch(code):
    p=subprocess.run([str(ROOT/'scripts/run.sh'),'repl'],input=code,text=True,capture_output=True,timeout=30)
    if p.returncode: raise AssertionError(p.stderr[:2500]+p.stdout[:2500])
    return p.stdout

class NativeStoreTests(unittest.TestCase):
    def test_restart_retract_and_strings(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'session.sexp'; q=json.dumps(str(path))
            name='source (one) "quotes" \\ slash'
            out=batch(f'(dlm (quote open) {q})\n(dlm (quote observe) {json.dumps(name)} (quote ((atom edge (a b)) (atom edge (b c)) (atom edge (d e)) (atom edge (e f)))))\n(dlm (quote step))\n(dlm (quote close))\n')
            self.assertIn('learned',out); self.assertIn('(closed)',out)
            original=path.read_bytes()
            self.assertIn(b'definition77',original)
            # Native dump/read roundtrip retains the actual source identity.
            out=batch(f'(dlm (quote open) {q})\n(dlm (quote query) {json.dumps(name)} (quote (atom "c77-0" (a c))))\n(dlm (quote retract) {json.dumps(name)})\n(dlm (quote query) {json.dumps(name)} (quote (atom "c77-0" (a c))))\n(dlm (quote close))\n')
            self.assertIn('(proved (proof',out); self.assertIn('(unknown-episode)',out)
            self.assertTrue(Path(str(path)+'.previous').exists())
            self.assertFalse(Path(str(path)+'.next').exists())
            out=batch(f'(dlm (quote open) {q})\n(dlm (quote status))\n(dlm (quote close))\n')
            self.assertIn('episodes 0 definitions 1',out)  # definition, not stale claims

    def test_corrupt_snapshot_is_not_overwritten_or_evaluated(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'s.sexp'; q=json.dumps(str(path))
            batch(f'(dlm (quote open) {q})\n(dlm (quote demo))\n(dlm (quote step))\n(dlm (quote close))\n')
            original=path.read_bytes()
            forged=loads_many(original.decode())[0]
            forged[2][3].append([S('definition77'),'unreplayed',[S('edge')]*3,
                                 [S('compose'),'c77-0',S('edge')]])
            for corrupt in (dumps(forged).encode(), original.replace(b'dlm-session77 1',b'dlm-session77 9'),
                            original.replace(b'(edge edge)',b'(edge wrong)'),
                            original+b' (extra)', b'(print "PWNED")'):
                path.write_bytes(corrupt)
                out=batch(f'(dlm (quote open) {q})\n(dlm (quote save))\n')
                self.assertIn('(rejected snapshot)',out); self.assertIn('(not-attached)',out)
                self.assertNotIn('PWNED',out); self.assertEqual(path.read_bytes(),corrupt)
            path.write_bytes(original)

    def test_admission_rolls_back_when_checkpoint_fails(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'s.sexp'; q=json.dumps(str(path)); p=Live()
            try:
                p.exchange(f'(dlm (quote open) {q})',rb'dlm77 paused')
                p.exchange("(dlm 'demo)",rb'observed demo-b')
                good=path.read_bytes(); corrupt=good.replace(b'dlm-session77 1',b'dlm-session77 2')
                path.write_bytes(corrupt)
                p.exchange("(dlm 'step)",rb'rejected checkpoint')
                p.exchange("(dlm 'status)",rb'definitions 0')
                self.assertEqual(path.read_bytes(),corrupt)
            finally: p.close()

    def test_attach_in_memory_learning_without_reset(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'new.sexp'; q=json.dumps(str(path))
            out=batch(f'(dlm (quote demo))\n(dlm (quote step))\n(dlm (quote open) {q})\n(dlm (quote close))\n')
            self.assertIn('episodes 2 definitions 1',out)
            out=batch(f'(dlm (quote open) {q})\n(dlm (quote query) (quote demo-b) (quote (atom "c77-0" (u w))))\n(dlm (quote close))\n')
            self.assertIn('(proved (proof',out)

    def test_native_lock(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'s.sexp'; q=json.dumps(str(path)); p=Live()
            try:
                p.exchange(f'(dlm (quote open) {q})',rb'dlm77 paused')
                out=batch(f'(dlm (quote open) {q})\n')
                self.assertIn('locked-or-path-unavailable',out)
            finally: p.close()
            self.assertIn('dlm77 paused',batch(f'(dlm (quote open) {q})\n(dlm (quote close))\n'))

    @unittest.skipIf(os.geteuid()==0,'root can read mode-000 files')
    def test_unreadable_is_not_missing(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'s.sexp'; path.write_text('do not replace'); path.chmod(0)
            try:
                out=batch(f'(dlm (quote open) {json.dumps(str(path))})\n')
                self.assertIn('rejected file-access',out)
            finally: path.chmod(0o600)
            self.assertEqual(path.read_text(),'do not replace')

class DefinitionOracleTests(unittest.TestCase):
    def test_primitive_path_semantics(self):
        rng=random.Random(77); cases=[]
        for _ in range(8):
            facts=[]
            for _ in range(9):
                f=[S('atom'),S(rng.choice(['r','s'])),[rng.randrange(5),rng.randrange(5)]]
                if f not in facts: facts.append(f)
            cases.append(facts)
        code='(define *oracle77* (read *standard-input*))\n'
        code+='''(list-do facts *oracle77*
 (let ((s (dlm-nth (a77-observe (a77-new) 'case facts) 1)) (cursor 0))
  (times-do 6 (let ((r (a77-step s cursor 1000))) (set s (dlm-nth r 1)) (set cursor (dlm-nth r 2))))
  (dump (list 'oracle77 s (dlm-conclusions (dlm-nth (a77-close s facts) 2)))) (print "\\n")))\n'''
        with tempfile.NamedTemporaryFile(mode='w',suffix='.l') as f:
            f.write(code); f.flush()
            p=subprocess.run([str(ROOT/'scripts/run.sh'),'proof',f.name],input=dumps(cases),text=True,capture_output=True,timeout=120)
        self.assertEqual(p.returncode,0,p.stderr[:2500]); results=loads_many(p.stdout)
        self.assertEqual(len(results),len(cases))
        count=0
        for facts,(_,state,closure) in zip(cases,results):
            for _,name,word,op in state[3]:
                expected={tuple(a[2]) for a in facts if a[1]==word[0]}
                for label in word[1:]:
                    expected={(x,z) for x,y in expected for _,pred,(u,z) in facts if pred==label and y==u}
                actual={tuple(a[2]) for a in closure if a[1]==name}
                self.assertEqual(expected,actual); count+=1
            # No primitive predicate gets new facts through a definition.
            primitive={dumps(a) for a in facts}
            self.assertEqual({dumps(a) for a in closure if a[1] in ('r','s')},primitive)
        self.assertGreater(count,0)
        print(f'DEFINITION-ORACLE {len(cases)} graphs, {count} definitions, zero mismatches')

if __name__=='__main__': unittest.main()
