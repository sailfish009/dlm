"""Process-level checks for the reviewed minimal core (0.0107)."""
from __future__ import annotations

import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def maru(code: str, timeout: int = 300) -> str:
    with tempfile.NamedTemporaryFile('w', suffix='.l', delete=False) as f:
        f.write(code)
        path = f.name
    p = subprocess.run([str(ROOT / 'scripts' / 'run.sh'), 'proof', path],
                       text=True, capture_output=True, timeout=timeout)
    if p.returncode:
        raise AssertionError(p.stderr[:3000] + p.stdout[:3000])
    return p.stdout


class CoreTests(unittest.TestCase):
    def test_native_core_suite(self):
        p = subprocess.run([str(ROOT / 'scripts' / 'run.sh'), 'test'], text=True,
                           capture_output=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        self.assertIn('ALL-CORE-TESTS-PASSED', p.stdout)

    def test_observation_is_durable_without_close(self):
        with tempfile.TemporaryDirectory() as d:
            store = Path(d) / 'state.sexp'
            out = maru(f'''
(dlm 'open "{store}")
(dlm 'observe 'o1 "src" "rec1" 'demo (list (p107-atom 'calls (list "a" "b"))))
(print "written=" (p107-store? *p107-store*) "\\n")''')
            self.assertIn('written=true', out)
            text = store.read_text()
            self.assertIn('obs107', text)
            self.assertIn('o1', text)

    def test_save_and_open_fresh_process_are_equal(self):
        with tempfile.TemporaryDirectory() as d:
            store = Path(d) / 'state.sexp'
            first = maru(f'''
(dlm 'open "{store}")
(dlm 'observe 'o1 "src" "rec1" 'demo (list (p107-atom 'calls (list "a" "b"))))
(dlm 'step) (dlm 'close)
(dump *p107-state*) (print "\\n")''')
            second = maru(f'''
(dlm 'open "{store}")
(dump *p107-state*) (print "\\n")
(dump (p107-read *p107-state* 'demo 20000)) (print "\\n")''')
            self.assertEqual(first.splitlines()[-1], second.splitlines()[0])
            self.assertIn('a calls b.', second)

    def test_corrupt_snapshot_is_refused_and_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            store = Path(d) / 'bad.sexp'
            original = '(not-a-snapshot 1)\n'
            store.write_text(original)
            out = maru(f'''(dump (dlm 'open "{store}")) (print "\\n")''')
            self.assertIn('rejected107', out)
            self.assertEqual(store.read_text(), original)

    def test_changed_background_rules_invalidate_a_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            store = Path(d) / 'rules.sexp'
            maru(f"""
(set *p107-edb* '(calls meaning))
(dlm 'rules (list (p107-rule (p107-atom 'h (list (p107-var 'x) (p107-var 'y)))
  (list (p107-atom 'calls (list (p107-var 'x) (p107-var 'y)))))))
(dlm 'open \"{store}\")
(dlm 'observe 'o1 \"s\" \"r\" 'demo (list (p107-atom 'calls (list \"a\" \"b\"))))
(dlm 'close)""")
            attached = maru(f"""
(set *p107-edb* '(calls meaning))
(dlm 'rules (list (p107-rule (p107-atom 'h (list (p107-var 'x) (p107-var 'y)))
  (list (p107-atom 'calls (list (p107-var 'x) (p107-var 'y)))))))
(dlm 'open \"{store}\")
(dump (dlm 'rules ())) (print \"\\n\")""")
            self.assertIn('detach-before-rules', attached)
            reordered = maru(f"""
(set *p107-edb* '(calls meaning))
(dlm 'rules (list (p107-rule (p107-atom 'h (list (p107-var 'x) (p107-var 'y)))
  (list (p107-atom 'calls (list (p107-var 'y) (p107-var 'x)))))))
(dump (dlm 'open \"{store}\")) (print \"\\n\")""")
            self.assertIn('rejected107', reordered)

    def test_same_epoch_different_content_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / 'a.sexp'
            b = Path(d) / 'b.sexp'
            mk = """
(dlm 'open \"{p}\")
(dlm 'observe 'o1 \"s\" \"r\" 'demo (list (p107-atom 'calls (list \"a\" \"b\"))))
(dlm 'retract 'o1) (dlm 'close)"""
            maru(mk.format(p=a))
            maru(mk.replace('o1', 'o2').replace('\"a\" \"b\"', '\"c\" \"d\"').format(p=b))
            # both logs have epoch 2 but different content
            a.write_text(b.read_text())
            out = maru(f"""
(dlm 'open \"{a}\")
(dump (p107-save \"{a}\" *p107-state* 12345)) (print \"\\n\")""")
            self.assertIn('rejected107 checkpoint', out)

    def test_stale_digest_save_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            store = Path(d) / 'epoch.sexp'
            out = maru(f'''
(dlm 'open "{store}")
(dlm 'observe 'o1 "src" "r" 'demo (list (p107-atom 'calls (list "a" "b"))))
(dump (p107-save "{store}" *p107-state* 999)) (print "\\n")
(dump (p107-save "{store}" *p107-state* *p107-disk-digest*)) (print "\\n")''')
            self.assertIn('rejected107 checkpoint', out)
            self.assertIn('saved107', out)

    def test_reopening_without_close_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / 'a.sexp'
            b = Path(d) / 'b.sexp'
            out = maru(f"""
(dlm 'open \"{a}\")
(dump (dlm 'open \"{b}\")) (print \"\\n\")""")
            self.assertIn('already-attached', out)

    def test_negation_oracle_agrees(self):
        p = subprocess.run(['python3', str(ROOT / 'tests' / 'oracle107.py'), '25', '105'],
                           text=True, capture_output=True, timeout=600)
        self.assertEqual(p.returncode, 0, p.stdout[-2000:] + p.stderr[-1000:])
        self.assertIn('oracle107: 25/25 agree', p.stdout)

    def test_reduce_check_detects_a_tampered_body(self):
        facts = ROOT / 'experiments' / 'northstar' / 'facts.sexp'
        original = facts.read_text()
        try:
            facts.write_text(original.replace('"main.py:L13"', '"main.py:L99"', 1))
            p = subprocess.run(['python3', str(ROOT / 'adapters' / 'reduce.py'),
                                '--source', str(ROOT / 'experiments/northstar/input/main.py'),
                                '--record', 'main.py', '--out', str(facts), '--check'],
                               text=True, capture_output=True, timeout=60)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('body does not match', p.stderr)
        finally:
            facts.write_text(original)

    def test_second_session_cannot_open_the_same_store(self):
        with tempfile.TemporaryDirectory() as d:
            store = Path(d) / 'locked.sexp'
            holder = subprocess.Popen(
                [str(ROOT / 'scripts' / 'run.sh'), 'repl'], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                holder.stdin.write(f'(dlm \'open "{store}")\n')
                holder.stdin.flush()
                deadline = time.time() + 30
                while time.time() < deadline and not store.exists():
                    time.sleep(0.1)
                self.assertTrue(store.exists(), 'holder did not attach')
                out = maru(f'''(dump (dlm 'open "{store}")) (print "\\n")''', timeout=60)
                self.assertIn('session-locked', out)
            finally:
                holder.kill()
                holder.wait(timeout=10)

    def test_malformed_input_does_not_crash_the_process(self):
        with tempfile.TemporaryDirectory() as d:
            store = Path(d) / 'm.sexp'
            code = f'''
(dlm 'open "{store}")
(dump (dlm 'observe 'x "s" "r" 'demo 'notalist)) (print "\\n")
(dump (dlm 'step "x")) (print "\\n")
(dump (dlm 'query 'demo 'notatom)) (print "\\n")
(dump (dlm)) (print "\\n")
(dump (dlm 'run . 5)) (print "\\n")
(dump (dlm 'observe 'y "s" "r" 'demo (list (p107-atom 'q (list (cons "a" "b")))))) (print "\\n")
(print "survived\\n")'''
            out = maru(code)
            self.assertIn('rejected107 observation', out)
            self.assertIn('rejected107 command-or-arity', out)
            self.assertIn('rejected107 query', out)
            self.assertIn('rejected107 command', out)
            self.assertIn('rejected107 observation', out)
            self.assertIn('survived', out)

    def test_learning_transition_keeps_data_and_answers(self):
        out = maru((ROOT / 'experiments' / 'learn' / 'run.l').read_text())
        self.assertIn('before defs=0', out)
        self.assertIn('after defs=2', out)
        self.assertIn('answers-identical=true', out)
        self.assertIn('(plan107', out)
        self.assertIn('call107 b1', out)
        self.assertIn('before rows=18 calls=0', out)
        self.assertIn('plan-calls-after=1', out)
        self.assertIn(' steps 2 ', out)
        self.assertIn('done-learn', out)

    def test_northstar_golden_slice(self):
        p = subprocess.run([str(ROOT / 'scripts' / 'run.sh'), 'northstar'], text=True,
                           capture_output=True, timeout=600)
        self.assertEqual(p.returncode, 0, p.stderr[-3000:])
        out = p.stdout
        self.assertIn('reduced facts: 209', out)
        self.assertIn('status=complete facts=231 sentences=157 skipped=0', out)
        self.assertIn('((level 1 135) (level 2 10) (level 3 12))', out)
        self.assertIn('library sentences=121', out)
        self.assertIn('done-northstar', out)
        self.assertNotIn('FAIL', out)

    def test_reduction_facts_hash_is_pinned(self):
        out = subprocess.run(['python3', str(ROOT / 'adapters' / 'reduce.py'),
                              '--source', str(ROOT / 'experiments/northstar/input/main.py'),
                              '--record', 'main.py',
                              '--out', str(ROOT / 'experiments/northstar/facts.sexp'),
                              '--check'], text=True, capture_output=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn('facts-sha256 cbe01597c8a8021e994f7b44183c1dccd5845bb3764dad8451231b1eebc1442b',
                      out.stdout)


if __name__ == '__main__':
    unittest.main()