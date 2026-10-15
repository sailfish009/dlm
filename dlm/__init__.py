"""DLM v0.0047 -- trusted kernel (function-free Horn substrate).

Fresh minimal rebuild around one question: what is the learning signal for
deduction?  The answer this version encodes: a general (pronominal,
non-referential) rule is a promise over an open universe, so every new referent
is a fresh, non-self-referential test.  The kernel asserts truth (closure);
everything else proposes.  v0.0047 adds stratified negation: a body literal may
be negated (closed-world over a GIVEN universe), the theory is stratified and
rejected if a negative cycle exists, and the closure becomes NON-MONOTONIC -- one
new fact can retract a derived negative -- while staying sound.  Function-free;
no weights, no softmax.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

__version__ = "0.0.47"
__all__ = [
    "Const", "Var", "Term", "Atom", "NegAtom", "Rule", "KnowledgeBase",
    "closure", "entails", "unify", "strata", "description_length",
]


class Term:
    pass


@dataclass(frozen=True)
class Const(Term):
    name: str


@dataclass(frozen=True)
class Var(Term):
    name: str


@dataclass(frozen=True)
class Atom:
    pred: str
    args: Tuple[Term, ...] = ()

    def is_ground(self) -> bool:
        return all(isinstance(a, Const) for a in self.args)


@dataclass(frozen=True)
class NegAtom:
    """A negated body literal ``not atom`` (closed-world, stratified)."""
    atom: Atom


@dataclass(frozen=True)
class Rule:
    head: Atom
    body: Tuple[Atom, ...] = ()
    name: str = ""


def _bind(pat: Term, ground: Term, s: Dict[str, Term]) -> bool:
    if isinstance(pat, Var):
        if pat.name in s:
            return s[pat.name] == ground
        s[pat.name] = ground
        return True
    return pat == ground


def unify(pattern: Atom, ground: Atom, s: Optional[Dict[str, Term]] = None):
    """Match a body pattern against a ground atom; return bindings or ``None``."""
    if pattern.pred != ground.pred or len(pattern.args) != len(ground.args):
        return None
    out = dict(s) if s else {}
    for p, g in zip(pattern.args, ground.args):
        if not _bind(p, g, out):
            return None
    return out


def _subst(atom: Atom, s: Dict[str, Term]) -> Atom:
    return Atom(atom.pred, tuple(s.get(t.name, t) if isinstance(t, Var) else t for t in atom.args))


@dataclass
class KnowledgeBase:
    facts: set = field(default_factory=set)
    rules: Tuple[Rule, ...] = ()

    def add_fact(self, a: Atom) -> None:
        self.facts.add(a)

    def add_facts(self, fs: Iterable[Atom]) -> None:
        self.facts.update(fs)

    def add_rule(self, r: Rule) -> None:
        self.rules = self.rules + (r,)

    def copy(self) -> "KnowledgeBase":
        return KnowledgeBase(set(self.facts), tuple(self.rules))


def _join(body: Tuple[Atom, ...], by_pred: dict, i: int = 0, s=None):
    if s is None:
        s = {}
    if i == len(body):
        yield s
        return
    for f in by_pred.get(body[i].pred, ()):
        ns = unify(body[i], f, s)
        if ns is not None:
            yield from _join(body, by_pred, i + 1, ns)


def _join_delta(body: Tuple[Atom, ...], by_pred: dict, delta_by: dict, di: int,
                i: int = 0, s=None):
    """Join ``body`` where literal ``di`` ranges over the delta facts only."""
    if s is None:
        s = {}
    if i == len(body):
        yield s
        return
    src = delta_by if i == di else by_pred
    for f in src.get(body[i].pred, ()):
        ns = unify(body[i], f, s)
        if ns is not None:
            yield from _join_delta(body, by_pred, delta_by, di, i + 1, ns)


def closure(kb: KnowledgeBase) -> set:
    """Least fixpoint of the rules over the facts (the kernel asserts this).

    Pure Horn rules use semi-naive evaluation: the first round joins over all
    facts; every later round only re-joins using the facts derived in the
    previous round, so a derivation is never recomputed.  The predicate index is
    maintained incrementally instead of being rebuilt each round.  Identical
    result to the naive fixpoint; see tests/test_closure_perf.py for the
    equivalence check.

    If any rule body contains a :class:`NegAtom`, evaluation is *stratified*
    (see :func:`strata`): negation is sound only when the negated predicate is
    defined in a strictly lower stratum, so the facts it ranges over are already
    complete.  A negative dependency cycle is rejected with ``ValueError``.
    """
    for rule in kb.rules:
        for lit in rule.body:
            if isinstance(lit, NegAtom):
                return _stratified_closure(kb)
    return _horn_closure(kb)


def _horn_closure(kb: KnowledgeBase) -> set:
    facts = set(kb.facts)
    by_pred: dict = {}
    for f in facts:
        by_pred.setdefault(f.pred, []).append(f)

    delta = set(facts)
    first = True
    while delta:
        delta_by: dict = {}
        for f in delta:
            delta_by.setdefault(f.pred, []).append(f)
        new: set = set()
        for rule in kb.rules:
            body = rule.body
            if not body:
                h = rule.head
                if h.is_ground() and h not in facts and h not in new:
                    new.add(h)
                continue
            if first:
                for s in _join(body, by_pred):
                    h = _subst(rule.head, s)
                    if h.is_ground() and h not in facts and h not in new:
                        new.add(h)
            else:
                for di in range(len(body)):
                    for s in _join_delta(body, by_pred, delta_by, di):
                        h = _subst(rule.head, s)
                        if h.is_ground() and h not in facts and h not in new:
                            new.add(h)
        first = False
        if not new:
            break
        for f in new:
            facts.add(f)
            by_pred.setdefault(f.pred, []).append(f)
        delta = new
    return facts


def entails(kb: KnowledgeBase, atom: Atom) -> bool:
    return atom in closure(kb)


def strata(kb: KnowledgeBase) -> Dict[str, int]:
    """Assign each predicate a stratum so negation is well-founded.

    ``stratum(head) = max(stratum(positive body preds), 1 + stratum(negated
    body preds))``.  A rule that depends negatively on a predicate of its own
    stratum (a negative cycle) makes this divergence; it is detected and raises
    ``ValueError`` -- the kernel refuses to guess a non-stratified theory.
    """
    preds = set()
    for r in kb.rules:
        preds.add(r.head.pred)
        for lit in r.body:
            preds.add(lit.pred if isinstance(lit, Atom) else lit.atom.pred)
    st = {p: 0 for p in preds}
    for _ in range(len(preds) + 2):
        changed = False
        for r in kb.rules:
            req = st[r.head.pred]
            for lit in r.body:
                if isinstance(lit, Atom):
                    req = max(req, st[lit.pred])
                else:
                    req = max(req, st[lit.atom.pred] + 1)
            if req > st[r.head.pred]:
                st[r.head.pred] = req
                changed = True
        if not changed:
            return st
    raise ValueError("not stratifiable: negative dependency cycle")


def _eval_rule(rule: Rule, by_pred: dict, known: set):
    """Yield ground heads; positive literals are joined, negations are checked.

    Safety: a negated literal whose atom is not ground under the positive
    bindings cannot be concluded, so the derivation is pruned (never guessed).
    """
    pos = tuple(l for l in rule.body if isinstance(l, Atom))
    neg = tuple(l for l in rule.body if isinstance(l, NegAtom))
    for s in _join(pos, by_pred):
        h = _subst(rule.head, s)
        if not h.is_ground():
            continue
        for lit in neg:
            ga = _subst(lit.atom, s)
            if not ga.is_ground() or ga in known:
                break
        else:
            yield h


def _stratified_closure(kb: KnowledgeBase) -> set:
    st = strata(kb)
    facts = set(kb.facts)
    by_pred: dict = {}
    for f in facts:
        by_pred.setdefault(f.pred, []).append(f)
    for k in sorted(set(st.values())):
        rules_k = [r for r in kb.rules if st[r.head.pred] == k]
        changed = True
        while changed:
            changed = False
            for r in rules_k:
                cands = _eval_rule(r, by_pred, facts) if r.body else ((r.head,)
                        if r.head.is_ground() else ())
                for h in cands:
                    if h not in facts:
                        facts.add(h)
                        by_pred.setdefault(h.pred, []).append(h)
                        changed = True
    return facts


def description_length(rules: Iterable[Rule]) -> int:
    """Each rule costs its head plus each body literal (facts are free input)."""
    return sum(1 + len(r.body) for r in rules)