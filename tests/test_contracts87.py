"""Finite contract semantics checked against an independent Python interpreter."""
import itertools
import json
from pathlib import Path
import random
import tempfile
import unittest
from test_sequent import maru
from test_repl import Live
from sexp import Symbol as S, dumps, loads_many

GOOD = '(contract87 setflag (flag ready) (bool 1) ((assign flag (bool 1))) (var flag) (flag))'


class Contracts87Tests(unittest.TestCase):
    def test_every_feasible_runtime_path_and_frame_old(self):
        out = maru('''(define bad '(contract87 bad (flag ready) (bool 1)
 ((if (var ready) ((assign flag (bool 1))) ())) (var flag) (flag)))
(define r (c87-verify bad (c87-empty) 1000))
(assert (= (car r) 'refuted87) "feasible else cannot be ignored")
(assert (= (dlm-nth (c87-check bad (c87-empty) (dlm-nth r 1) 1000) 1) 'refuted) "checked counterexample")
(define good '(contract87 conditional (flag ready) (var ready)
 ((if (var ready) ((assign flag (bool 1))) ())) (var flag) (flag)))
(assert (= (car (c87-verify good (c87-empty) 1000)) 'verified87) "infeasible else excluded by pre")
(define toggle '(contract87 toggle (flag ready) (bool 1)
 ((if (var flag) ((assign flag (bool 0))) ((assign flag (bool 1)))))
 (and (eq (var flag) (not (old flag))) (eq (var ready) (old ready))) (flag)))
(assert (= (car (c87-verify toggle (c87-empty) 1000)) 'verified87) "old/frame and isolated cases")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_vacuity_and_budget_are_not_success(self):
        out = maru(f'''(define c '{GOOD})
(assert (= (car (c87-verify c (c87-empty) 0)) 'unknown87) "zero budget")
(define impossible '(contract87 vacuous (x) (and (var x) (not (var x))) () (bool 0) ()))
(assert (= (car (c87-verify impossible (c87-empty) 1000)) 'inapplicable87) "vacuity not solved")
(assert (not (= (car (c87-admit (c87-empty) impossible 1000)) 'admitted87)) "no vacuous library entry")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_tampered_coverage_and_trace_rejected_by_independent_checker(self):
        out = maru(f'''(define c '{GOOD})
(define result (c87-verify c (c87-empty) 1000))
(define cert (dlm-nth result 1))
(define rows (dlm-nth cert 3))
(assert (= (dlm-nth (c87-check c (c87-empty) (s79-field cert 3 (cdr rows)) 1000) 1) 'invalid) "coverage")
(define forged (s79-field cert 3 (cons (s79-field (car rows) 3 '((assign87 flag 0))) (cdr rows))))
(assert (= (dlm-nth (c87-check c (c87-empty) forged 1000) 1) 'invalid) "bad transition")
(define original c87-execute)
(define-function disabled87 (a b c d) (error "checker must not run explorer"))
(set c87-execute disabled87)
(assert (= (dlm-nth (c87-check c (c87-empty) cert 1000) 1) 'verified) "checker independent of explorer")
(set c87-execute original)
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_checked_summary_calls_preconditions_and_dependency_versions(self):
        out = maru(f'''(define lib (dlm-nth (c87-admit (c87-empty) '{GOOD} 1000) 1))
(define caller '(contract87 caller (flag ready) (bool 1) ((call setflag)) (var flag) (flag)))
(define proof (dlm-nth (c87-verify caller lib 2000) 1))
(assert (= (dlm-nth (c87-check caller lib proof 2000) 1) 'verified) "summary reuse")
(define changed (dlm-nth (c87-admit (c87-empty)
 '(contract87 setflag (flag ready) (bool 1) ((assign flag (bool 0))) (not (var flag)) (flag)) 1000) 1))
(assert (= (dlm-nth (c87-check caller changed proof 2000) 1) 'invalid) "stale dependency rejected")
(define guarded (dlm-nth (c87-admit (c87-empty)
 '(contract87 guarded (flag ready) (var ready) ((assign flag (bool 1))) (var flag) (flag)) 1000) 1))
(assert (= (car (c87-verify '(contract87 caller (flag ready) (bool 1) ((call guarded)) (var flag) (flag))
 guarded 2000)) 'refuted87) "call precondition must hold")
(assert (= (car (c87-verify '(contract87 no_write (flag ready) (bool 1) ((call setflag)) (var flag) ())
 lib 2000)) 'invalid87) "callee writes must be permitted")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_real_generation_learning_and_verified_call_reuse(self):
        out = maru('''(define template '(contract87 first (flag ready) (bool 1) () (var flag) (flag)))
(assert (= (car (contracts 'learn template)) 'learned87) "generated program admitted")
(assert (= (car (contracts 'learn (s79-field template 1 'second))) 'learned87) "reuse admitted")
(define second (dlm-nth (dlm-nth (contracts 'library) 1) 1))
(assert (equal (dlm-nth (dlm-nth second 1) 4) '((call first))) "later generation uses checked operator")
(assert (= (dlm-length (dlm-nth (contracts 'library) 1)) 2) "no own output as observation")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_verified_modules_compose_for_a_stronger_goal(self):
        out = maru('''(contracts 'learn '(contract87 setx (x y) (bool 1) () (var x) (x)))
(contracts 'learn '(contract87 sety (x y) (bool 1) () (var y) (y)))
(define r (contracts 'learn '(contract87 both (x y) (bool 1) () (and (var x) (var y)) (x y))))
(assert (= (car r) 'learned87) "stronger goal solved")
(assert (equal (dlm-nth r 2) '((call setx) (call sety))) "composition of checked procedures")
(assert (= (dlm-nth (contracts 'check-library) 1) 'verified) "all composed certificates rechecked")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_forged_provisional_ticket_cannot_admit(self):
        out = maru('''(define-function forged87 (arg)
 (list 'verified87 (list 'certificate87 (car arg) (c87-bindings (dlm-nth arg 1)) ()) 0))
(set s87-verify forged87)
(define r (contracts 'learn '(contract87 forged (flag) (bool 1) () (var flag) (flag))))
(assert (= (car r) 'unknown87) "forged empty proof fails admission checker")
(assert (equal (contracts 'library) (c87-empty)) "no forged publication")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_native_storage_rechecks_proofs_and_rejects_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'library.sexp'
            q = json.dumps(str(path))
            out = maru(f'''(contracts 'admit '{GOOD})
(dump (contracts 'save {q}))''')
            self.assertEqual(loads_many(out)[0], ['saved87'])
            original = path.read_bytes()
            out = maru(f'''(dump (contracts 'load {q})) (print "\\n")
(dump (contracts 'verify '(contract87 caller (flag ready) (bool 1) ((call setflag)) (var flag) (flag))))''')
            rows = loads_many(out)
            self.assertEqual(rows[0], ['restored87'])
            self.assertEqual(rows[1][0], 'verified87')
            path.write_bytes(original.replace(b'(assign87 flag 1)', b'(assign87 flag 0)', 1))
            out = maru(f'''(dump (contracts 'load {q})) (print "\\n")
(dump (contracts 'save {q}))''')
            self.assertEqual(loads_many(out), [['rejected87', 'snapshot'], ['rejected87', 'checkpoint']])
            self.assertNotEqual(path.read_bytes(), original)

    def test_unsupported_or_ill_typed_programs_fail_closed(self):
        cases = [42, [S('contract87')],
                 [S('contract87'), S('bad'), [S('x')], [S('bool'), 1],
                  [[S('assign'), S('x'), [S('bool'), 1]]], [S('var'), S('x')], []],
                 [S('contract87'), S('bad'), [S('x')], [S('bool'), 1],
                  [[S('call'), S('bad')]], [S('bool'), 1], []],
                 [S('contract87'), S('bad'), [S('x')], [S('bool'), 1],
                  [[S('while'), [S('bool'), 1], []]], [S('bool'), 1], []]]
        out = maru('''(list-do c (read *standard-input*)
 (dump (car (c87-verify c (c87-empty) 1000))) (print "\\n"))''', dumps(cases))
        self.assertEqual(loads_many(out), [S('invalid87')] * len(cases))

    def test_original_repl_exposes_contract_learning(self):
        repl = Live()
        try:
            repl.exchange("(contracts 'learn '(contract87 first (x) (bool 1) () (var x) (x)))", rb'learned87 first')
            repl.exchange("(contracts 'learn '(contract87 second (x) (bool 1) () (var x) (x)))", rb'learned87 second')
            repl.exchange("(assert (= (dlm-length (dlm-nth (contracts 'library) 1)) 2) \"library\")", rb'true')
        finally:
            repl.close()

    def test_seeded_python_semantic_oracle(self):
        rng = random.Random(87)
        variables = ['x', 'y']
        def expr(depth, old=False):
            leaves = [[S('bool'), 0], [S('bool'), 1]] + [[S('var'), S(v)] for v in variables]
            if old:
                leaves += [[S('old'), S(v)] for v in variables]
            if not depth or rng.random() < .35:
                return rng.choice(leaves)
            op = rng.choice(['not', 'and', 'or', 'eq'])
            return [S(op), expr(depth-1, old)] + ([] if op == 'not' else [expr(depth-1, old)])
        def body(depth):
            result = []
            for _ in range(rng.randrange(4)):
                op = rng.choice(['assign', 'assert', 'if'] if depth else ['assign', 'assert'])
                if op == 'assign': result.append([S(op), S(rng.choice(variables)), expr(1)])
                elif op == 'assert': result.append([S(op), expr(1)])
                else: result.append([S(op), expr(1), body(depth-1), body(depth-1)])
            return result
        def ev(e, env, old):
            op = e[0]
            if op == 'bool': return bool(e[1])
            if op == 'var': return env[e[1]]
            if op == 'old': return old[e[1]]
            if op == 'not': return not ev(e[1], env, old)
            a, b = ev(e[1], env, old), ev(e[2], env, old)
            return {'and': a and b, 'or': a or b, 'eq': a == b}[op]
        def execute(stmts, env, old):
            for stmt in stmts:
                if stmt[0] == 'assign': env[stmt[1]] = ev(stmt[2], env, old)
                elif stmt[0] == 'assert':
                    if not ev(stmt[1], env, old): return False
                elif not execute(stmt[2] if ev(stmt[1], env, old) else stmt[3], env, old): return False
            return True
        cases, expected = [], []
        for i in range(200):
            pre, program, post = expr(2), body(1), expr(2, True)
            c = [S('contract87'), f'case{i}', list(map(S, variables)), pre, program, post, list(map(S, variables))]
            applicable, valid = 0, True
            for bits in itertools.product((False, True), repeat=2):
                before = dict(zip(variables, bits))
                if ev(pre, before, before):
                    applicable += 1
                    after = before.copy()
                    valid &= execute(program, after, before) and ev(post, after, before)
            expected.append('inapplicable87' if not applicable else ('verified87' if valid else 'refuted87'))
            cases.append(c)
        out = maru('''(list-do c (read *standard-input*)
 (dump (car (c87-verify c (c87-empty) 20000))) (print "\\n"))''', dumps(cases))
        self.assertEqual(loads_many(out), expected)
        print('CONTRACT87-ORACLE 200 finite programs, four input valuations each, zero mismatches')


if __name__ == '__main__':
    unittest.main()
