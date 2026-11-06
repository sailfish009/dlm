#!/usr/bin/env python3
"""Independent finite-closure oracle for negation, literal order and empty bodies.

Generates random range-restricted programs, evaluates them with a small Python
reference (closed-world negation over the extensional base only; literal order
irrelevant), runs the Maru core, and compares the derived atom sets.

Usage: python3 tests/oracle107.py [N] [SEED]
"""
from __future__ import annotations

import itertools
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDB = ('e0', 'e1')
IDB = ('i0', 'i1')
CONSTS = ('a', 'b', 'c')


def gen_program(rng: random.Random):
    facts = {p: set() for p in EDB}
    for p in EDB:
        for _ in range(rng.randint(0, 3)):
            facts[p].add(tuple(rng.choice(CONSTS) for _ in range(rng.choice((1, 2)))))
    rules = []
    for _ in range(rng.randint(1, 3)):
        head = rng.choice(IDB)
        arity = rng.choice((0, 1, 2))
        hvars = [f'x{i}' for i in range(arity)]
        vars_pool = hvars + ['y0', 'y1']
        pos = []
        for _ in range(rng.randint(0, 2)):
            pred = rng.choice(EDB + IDB)
            args = [rng.choice(vars_pool) for _ in range(rng.choice((1, 2)))]
            pos.append((pred, args, True))
        for v in hvars:  # range restriction: head vars occur positively
            if not any(v in a for _, a, _ in pos):
                if not pos:
                    pos.append((rng.choice(EDB), [v], True))
                else:
                    pos[0][1][0] = v
        negs = []
        if rng.random() < 0.4 and pos:
            pred = rng.choice(EDB)
            base = [v for _, a, _ in pos for v in a]
            negs.append((pred, [rng.choice(base)], False))
        body = pos + negs
        rng.shuffle(body)
        rules.append((head, hvars, body))
    return facts, rules


def reference(facts, rules):
    atoms = {(p, t) for p, ts in facts.items() for t in ts}
    edb_atoms = set(atoms)
    changed = True
    while changed:
        changed = False
        for head, hvars, body in rules:
            pos = [(p, a) for p, a, sign in body if sign]
            neg = [(p, a) for p, a, sign in body if not sign]
            bindings = [{}]
            for pred, args in pos:
                nxt = []
                for b in bindings:
                    free = [a for a in args if a not in b]
                    combos = [{}] if not free else [
                        dict(zip(free, combo)) for combo in itertools.product(CONSTS, repeat=len(free))]
                    for extra in combos:
                        nb = {**b, **extra}
                        inst = tuple(nb.get(a, a) for a in args)
                        if (pred, inst) in atoms:
                            nxt.append(nb)
                bindings = nxt
            for b in bindings:
                ok = True
                for pred, args in neg:
                    inst = tuple(b.get(a, a) for a in args)
                    if any(a not in b for a in args) or (pred, inst) in edb_atoms:
                        ok = False
                        break
                if not ok:
                    continue
                ground = tuple(b.get(v, v) for v in hvars)
                if any(g.startswith(('x', 'y')) for g in ground):
                    continue
                if (head, ground) not in atoms:
                    atoms.add((head, ground))
                    changed = True
    return atoms


def maru_program(facts, rules):
    out = ['(set *p107-edb* (list ' + ' '.join(f"'{p}" for p in EDB) + '))']
    ff = []
    for p, ts in facts.items():
        for t in ts:
            ff.append(f'(p107-given-id "g" (p107-atom \'{p} (list {" ".join(chr(34)+c+chr(34) for c in t)})))')
    rf = []
    for head, hvars, body in rules:
        hv = ' '.join(f"(p107-var '{v})" for v in hvars)
        lits = []
        for pred, args, sign in body:
            a = ' '.join(f"(p107-var '{x})" for x in args)
            atom = f"(p107-atom '{pred} (list {a}))"
            lits.append(atom if sign else f'(p107-neg {atom})')
        rf.append(f"(p107-rule (p107-atom '{head} (list {hv})) (list {' '.join(lits)}))")
    out += [f'(define facts (list {" ".join(ff)}))',
            f'(define rules (list {" ".join(rf)}))',
            '(define cl (p107-close facts rules 200000))',
            '(print "STATUS " (p107-nth cl 1) "\\n")',
            '(define-function show (f) (let ((a (p107-nth f 2)))'
            ' (print "A " (p107-str (p107-pred a)) "|" (number->string (p107-len (p107-args a))) "|"'
            ' (p107-join-strings (p107-map p107-str (p107-args a)) "|") "\\n")))',
            '(list-do f (p107-nth cl 2) (show f))']
    return '\n'.join(out)


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 105
    rng = random.Random(seed)
    bad = 0
    for i in range(n):
        facts, rules = gen_program(rng)
        with tempfile.NamedTemporaryFile('w', suffix='.l', delete=False) as f:
            f.write(maru_program(facts, rules))
            path = f.name
        p = subprocess.run([str(ROOT / 'scripts' / 'run.sh'), 'proof', path],
                           text=True, capture_output=True, timeout=120)
        if p.returncode:
            print(f'case {i}: CRASH {p.returncode} {p.stderr[:160]}')
            bad += 1
            continue
        got = set()
        status = None
        for line in p.stdout.splitlines():
            if line.startswith('STATUS '):
                status = line.split()[1]
            elif line.startswith('A '):
                parts = line[2:].split('|')
                arity = int(parts[1])
                args = tuple(parts[2:]) if arity else ()
                got.add((parts[0], args))
        exp = reference(facts, rules)
        if status != 'complete' or got != exp:
            bad += 1
            print(f'case {i}: status={status} got={sorted(got)} expected={sorted(exp)}')
            if bad <= 3:
                print(maru_program(facts, rules))
    print(f'oracle107: {n - bad}/{n} agree')
    sys.exit(0 if bad == 0 else 1)


if __name__ == '__main__':
    main()