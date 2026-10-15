"""DLM v0.0055 -- recursive self-supervised learning (untrusted).

The model's own kernel-certified output becomes the next round's input.  Each
round takes the relation it currently has (starting from the base edges),
CLOSES it through the kernel under two definitional rules

    r_{k+1}(X,Y) :- r_k(X,Y).                 -- inherit
    r_{k+1}(X,Z) :- r_k(X,Y), r_k(Y,Z).       -- compose (self-join)

and REIFIES the certified extension as a new predicate ``r_{k+1}``.  Nothing is
invented: the kernel derives the new predicate's extension, and the model feeds
its own conclusion back as the next round's only input -- recursion, with the
kernel as the sole judge and no labels.  Because each round doubles the path
length the relation can span, the model reaches the full reachability closure in
O(log diameter) rounds and then abstains (fixpoint: a round adds nothing).

The model is NOT given the relational transitive rule ``reach :- edge, reach``;
it must bootstrap depth from its own output.  :func:`one_shot` is the depth-1
control (a single composition), which provably cannot reach the closure on any
graph with a path longer than two hops -- the falsifier that recursion is needed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from . import Atom, Const, KnowledgeBase, Rule, Var, closure

__all__ = ["Round", "RecursionResult", "level_rules", "recurse", "one_shot",
           "reachability", "edges_of"]


def level_rules(cur: str, nxt: str) -> Tuple[Rule, ...]:
    """The two GIVEN definitional rules that lift one relation level up."""
    x, y, z = Var("?x"), Var("?y"), Var("?z")
    return (
        Rule(Atom(nxt, (x, y)), (Atom(cur, (x, y)),), name=f"{nxt}_inherit"),
        Rule(Atom(nxt, (x, z)), (Atom(cur, (x, y)), Atom(cur, (y, z))),
             name=f"{nxt}_compose"),
    )


def edges_of(atoms, pred: str = "edge") -> set:
    return {(a.args[0].name, a.args[1].name) for a in atoms if a.pred == pred}


def _atoms(pairs, pred: str) -> set:
    return {Atom(pred, (Const(a), Const(b))) for (a, b) in pairs}


def _one_level(pairs: set, cur: str, nxt: str) -> set:
    """Kernel-close the current relation under the two level rules."""
    kb = KnowledgeBase(_atoms(pairs, cur))
    for r in level_rules(cur, nxt):
        kb.add_rule(r)
    return edges_of(closure(kb), nxt)


@dataclass(frozen=True)
class Round:
    level: int
    pred: str
    size: int
    new: int

    def to_dict(self) -> dict:
        return {"level": self.level, "pred": self.pred, "size": self.size,
                "new": self.new}


@dataclass
class RecursionResult:
    rounds: List[Round]
    relation: set          # the fixpoint extension
    pred: str
    fixed: bool

    @property
    def depth(self) -> int:
        return len(self.rounds)

    def to_dict(self) -> dict:
        return {"depth": self.depth, "fixed": self.fixed, "pred": self.pred,
                "final_size": len(self.relation),
                "rounds": [r.to_dict() for r in self.rounds]}


def recurse(edges: Sequence[Tuple[str, str]], *, max_depth: int = 32,
            start: str = "edge") -> RecursionResult:
    """Iterate self-composition to a fixpoint (the recursive self-supervision)."""
    rel = {(a, b) for a, b in edges}
    pred = start
    rounds: List[Round] = []
    fixed = False
    for k in range(1, max_depth + 1):
        nxt = f"r{k}"
        nrel = _one_level(rel, pred, nxt)
        new = len(nrel - rel)
        rounds.append(Round(k, nxt, len(nrel), new))
        if new == 0:                       # a round added nothing -> fixpoint
            fixed = True
            rel, pred = nrel, nxt
            break
        rel, pred = nrel, nxt
    return RecursionResult(rounds, rel, pred, fixed)


def one_shot(edges: Sequence[Tuple[str, str]]) -> set:
    """Depth-1 control: ONE self-composition, no recursion."""
    rel = {(a, b) for a, b in edges}
    return _one_level(rel, "edge", "r1")


def reachability(edges: Sequence[Tuple[str, str]]) -> set:
    """Ground-truth transitive closure (evaluation only; the model never sees it)."""
    rel = {(a, b) for a, b in edges}
    changed = True
    while changed:
        changed = False
        new = {(a, c) for (a, b) in rel for (b2, c) in rel if b == b2}
        if not new <= rel:
            rel |= new
            changed = True
    return rel