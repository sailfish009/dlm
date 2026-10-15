"""Equivalence + scaling checks for the semi-naive kernel closure (v0.0039).

The kernel rewrite must be *semantics-preserving*: the semi-naive fixpoint has to
produce exactly the same set as the old naive fixpoint on arbitrary function-free
Horn programs.  These tests assert that over random KBs and a transitive chain.
"""
import random

from dlm import Atom, Const, KnowledgeBase, Rule, Var, _join, _subst, closure

PREDS = [("p", 2), ("q", 2), ("r", 2), ("s", 1)]
VARS = [Var("?x"), Var("?y"), Var("?z")]


def naive(kb: KnowledgeBase) -> set:
    """The pre-v0.0039 reference closure (rebuild index + all joins each pass)."""
    facts = set(kb.facts)
    changed = True
    while changed:
        changed = False
        by: dict = {}
        for f in facts:
            by.setdefault(f.pred, []).append(f)
        for r in kb.rules:
            for s in _join(r.body, by):
                h = _subst(r.head, s)
                if h.is_ground() and h not in facts:
                    facts.add(h)
                    changed = True
    return facts


def rand_kb(rng: random.Random, nfacts: int, nrules: int) -> KnowledgeBase:
    consts = [Const(f"c{i}") for i in range(6)]
    facts = set()
    for _ in range(nfacts):
        pred, ar = rng.choice(PREDS)
        facts.add(Atom(pred, tuple(rng.choice(consts) for _ in range(ar))))
    rules = []
    for i in range(nrules):
        pred, ar = rng.choice(PREDS)
        head = Atom(pred, tuple(rng.choice(VARS) for _ in range(ar)))
        body = []
        for _ in range(rng.randint(1, 2)):
            bp, bar = rng.choice(PREDS)
            body.append(Atom(bp, tuple(rng.choice(VARS) for _ in range(bar))))
        rules.append(Rule(head, tuple(body), name=f"r{i}"))
    return KnowledgeBase(facts, tuple(rules))


def test_seminaive_matches_naive_on_random_kbs():
    for seed in range(300):
        rng = random.Random(seed)
        kb = rand_kb(rng, rng.randint(0, 12), rng.randint(0, 4))
        assert closure(kb) == naive(kb), f"mismatch at seed {seed}"


def test_transitive_chain_full_closure():
    n = 60
    facts = {Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))) for i in range(n)}
    x, y, z = Var("?x"), Var("?y"), Var("?z")
    trans = Rule(Atom("e", (x, z)), (Atom("e", (x, y)), Atom("e", (y, z))), "t")
    cl = closure(KnowledgeBase(facts, (trans,)))
    expected = {Atom("e", (Const(f"n{i}"), Const(f"n{j}")))
                for i in range(n + 1) for j in range(n + 1) if i < j}
    assert cl == expected
    assert len(cl) == n * (n + 1) // 2


def test_random_kb_is_deterministic():
    kb = rand_kb(random.Random(7), 20, 3)
    assert closure(kb) == closure(kb)