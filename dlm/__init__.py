"""DLM v0.0038 -- trusted kernel (function-free Horn substrate).

Fresh minimal rebuild around one question: what is the learning signal for
deduction?  The answer this version encodes: a general (pronominal,
non-referential) rule is a promise over an open universe, so every new referent
is a fresh, non-self-referential test.  The kernel asserts truth (closure);
everything else proposes.  Function-free; no weights, no softmax.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

__version__ = "0.0.38"
__all__ = [
    "Const", "Var", "Term", "Atom", "Rule", "KnowledgeBase",
    "closure", "entails", "unify", "description_length",
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


def closure(kb: KnowledgeBase) -> set:
    """Least fixpoint of the rules over the facts (the kernel asserts this)."""
    facts = set(kb.facts)
    changed = True
    while changed:
        changed = False
        by_pred: dict = {}
        for f in facts:
            by_pred.setdefault(f.pred, []).append(f)
        for rule in kb.rules:
            for s in _join(rule.body, by_pred):
                h = _subst(rule.head, s)
                if h.is_ground() and h not in facts:
                    facts.add(h)
                    changed = True
    return facts


def entails(kb: KnowledgeBase, atom: Atom) -> bool:
    return atom in closure(kb)


def description_length(rules: Iterable[Rule]) -> int:
    """Each rule costs its head plus each body literal (facts are free input)."""
    return sum(1 + len(r.body) for r in rules)