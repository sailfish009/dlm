"""Native REPL integration: one process, original parser, cooperative tasks.
Python is a developer test driver only; no Python process runs in the product.
"""
import os
from pathlib import Path
import re
import select
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
MARU = str(Path(os.environ.get('MARU', ROOT/'maru-compiler')).resolve())

class Live:
    def __init__(self, command=None, cwd=ROOT):
        self.p = subprocess.Popen(command or [str(ROOT/'scripts/run.sh'),'repl'], cwd=cwd,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0)
        self.output = b''
    def send(self, text):
        self.p.stdin.write(text.encode()); self.p.stdin.flush()
    def drain(self, seconds=.15):
        end = time.monotonic()+seconds
        while time.monotonic() < end:
            if select.select([self.p.stdout],[],[],max(0,end-time.monotonic()))[0]:
                b = os.read(self.p.stdout.fileno(),65536)
                if not b: break
                self.output += b
    def wait(self, pattern, start=0, seconds=8):
        end = time.monotonic()+seconds
        while time.monotonic() < end:
            m = re.search(pattern,self.output[start:])
            if m: return m
            self.drain(.03)
            if self.p.poll() is not None: break
        raise AssertionError(f'No {pattern!r}: {self.output[-5000:]!r}')
    def exchange(self, text, pattern):
        start=len(self.output); self.send(text+'\n'); return self.wait(pattern,start)
    def close(self):
        if not self.p.stdin.closed: self.p.stdin.close()
        self.drain(.1)
        try: self.p.wait(timeout=8)
        except subprocess.TimeoutExpired: self.p.kill(); self.p.wait(); raise
        self.output += self.p.stdout.read(); self.p.stdout.close()
        return self.output.decode(errors='replace')

class ReplTests(unittest.TestCase):
    def test_opt_in_parser_and_source_free(self):
        # Uses the embedded boot library from a directory with no source tree.
        with tempfile.TemporaryDirectory() as d:
            p=Live([MARU,'boot.l','-'],cwd=d)
            try:
                p.exchange('(+ 1 2)',rb'3\r?\nmaru>')
                p.send('(define tickcount 0)\n(define-function test-tick () (set tickcount (+ tickcount 1)) (print "TICK=" tickcount "\\n"))\n')
                p.drain(.15); self.assertNotIn(b'TICK=',p.output)
                p.exchange("(repl-idle-task '(test-tick) 30)",rb'TICK=2')
                pid=p.p.pid
                p.exchange('(let () (times-do 12000 (list 1 2 3 4 5 6)) (print "GC-DONE\\n"))',rb'GC-DONE')
                start=len(p.output)
                p.send('(list "literal ) ( ;" ; comment with (\n')
                p.wait(rb'TICK=\d+',start)  # task still runs during an unfinished form
                p.send('7)\n')
                p.wait(rb'\(literal \) \( ; 7\)',start)
                p.exchange('(+ ?( 2)',rb'42\r?\nmaru>')
                p.exchange('(repl-idle-task ())',rb'\(\)\r?\nmaru>')
                m=p.exchange('(print "COUNT=" tickcount "\\n")',rb'COUNT=(\d+)')
                count=m[1]
                p.drain(.12)
                m=p.exchange('(print "AGAIN=" tickcount "\\n")',rb'AGAIN=(\d+)')
                self.assertEqual(count,m[1]); self.assertEqual(p.p.pid,pid)
            finally: output=p.close()
            self.assertEqual(p.p.returncode,0,output[-3000:])
            self.assertNotIn('ERROR',output)

    def test_file_load_does_not_run_idle_task(self):
        with tempfile.TemporaryDirectory() as d:
            driver=Path(d)/'program.l'
            driver.write_text('(define ticks 0)\n(define-function bad-task () (set ticks (+ ticks 1)))\n'
                '(repl-idle-task (quote (bad-task)) 20)\n(print "FILE-TICKS=" ticks "\\n")\n')
            p=subprocess.run([MARU,'boot.l',str(driver)],cwd=d,text=True,capture_output=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr); self.assertIn('FILE-TICKS=0',p.stdout)
        self.assertNotIn('maru>',p.stdout)

    def test_native_recursive_learning_pause_and_reactivate(self):
        p=Live()
        try:
            p.send("(dlm 'demo)\n(dlm 'start 30)\n")
            p.wait(rb'Defined c77-2')
            p.wait(rb'waiting for evidence')
            p.exchange("(dlm 'pause)",rb'\(paused\)')
            m=p.exchange('(print "ROUND=" *dlm-round* "\\n")',rb'ROUND=(\d+)')
            before=m[1]; p.drain(.12)
            m=p.exchange('(print "ROUND2=" *dlm-round* "\\n")',rb'ROUND2=(\d+)')
            self.assertEqual(before,m[1])
            p.exchange("(dlm 'query 'demo-b '(atom \"c77-2\" (u y)))",rb'\(proved \(proof')
            p.exchange("(dlm 'query 'demo-b '(atom edge (u y)))",rb'\(not-derived\)')
            p.send("(dlm 'observe 'new '((atom link (i j)) (atom link (j k)) (atom link (p q)) (atom link (q r))))\n(dlm 'start 30)\n")
            p.wait(rb'Defined c77-3')
            p.exchange("(dlm 'stop)",rb'paused in-memory')
        finally: output=p.close()
        self.assertEqual(p.p.returncode,0,output[-3000:])
        self.assertNotIn('ERROR',output)

    def test_one_process_selfssl_launcher(self):
        with tempfile.TemporaryDirectory() as d:
            p=Live([str(ROOT/'scripts/selfssl.sh'),'--demo',str(Path(d)/'state.sexp')])
            try:
                p.wait(rb'Defined c77-0',seconds=8)
                p.exchange("(dlm 'status)",rb'dlm77 running')
                p.exchange("(dlm 'close)",rb'\(closed\)')
            finally: output=p.close()
            self.assertEqual(p.p.returncode,0,output[-3000:])
            self.assertIn('maru>',output)
            self.assertTrue((Path(d)/'state.sexp').exists())

    def test_packaging_keeps_runtime_but_not_generated_data(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); (d/'.gitignore').write_bytes((ROOT/'.gitignore').read_bytes())
            subprocess.run(['git','init','-q',str(d)],check=True)
            paths={'runtime/releases/example/maru':False,
                   'runtime/releases/example/maru.ll':True,
                   'experiments/fld/audit/train.inputs.jsonl':True,
                   'experiments/fld/validation-smoke/validation.gold.jsonl':True,
                   'experiments/repl/store/state.sexp':True}
            for path,ignored in paths.items():
                p=d/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text('fixture')
                rc=subprocess.run(['git','check-ignore','-q',path],cwd=d).returncode
                self.assertEqual(rc==0,ignored,path)

    def test_pty_existing_prompt(self):
        # Real terminal smoke, not just piped data. No alternate REPL process.
        import pty
        master,slave=pty.openpty()
        p=subprocess.Popen([str(ROOT/'scripts/run.sh'),'repl'],stdin=slave,stdout=slave,stderr=slave,cwd=ROOT)
        os.close(slave); out=b''
        try:
            os.write(master,b"(dlm 'demo)\n(dlm 'start 50)\n")
            end=time.monotonic()+6
            while time.monotonic()<end and b'Defined c77-1' not in out:
                if select.select([master],[],[],.1)[0]: out+=os.read(master,65536)
            self.assertIn(b'Defined c77-1',out)
            os.write(master,b"(dlm 'pause)\n(+ 20 22)\n")
            end=time.monotonic()+4
            while time.monotonic()<end and b'42\r\nmaru>' not in out:
                if select.select([master],[],[],.1)[0]: out+=os.read(master,65536)
            self.assertIn(b'42\r\nmaru>',out)
            os.write(master,b'\x04'); p.wait(timeout=5)
            self.assertEqual(p.returncode,0)
        finally:
            if p.poll() is None: p.kill(); p.wait()
            os.close(master)

if __name__=='__main__': unittest.main()
