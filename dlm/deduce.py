"""DLM v0.0001 — deduction engine.

Two independent engines over the same Horn KB:

* ``forward_chain`` computes the least fixpoint (semi-naive style: only new
  facts trigger rules) and returns the full classical closure.
* ``prove`` runs SLD backward chaining and returns answers together with a
  proof trace.

Design choice: **no function symbols**. The Herbrand base is therefore finite
whenever the constants are finite, so the closure terminates without any depth
bound. ``max_depth`` guards only the backward search on left-recursive rules.

Soundness contract (checked in tests): an atom is in the forward closure iff
backward chaining can prove it (for a definite Horn KB).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple

from .kb import KnowledgeBase
from .rules import Rule
from .terms import Atom, Subst, substitute_atom, unify_atom


@dataclass(frozen=True)
class Proof:
    """A proof tree for one derived atom."""

    atom: Atom
    kind: str
    children: Tuple["Proof", ...] = ()

    def leaves(self) -> int:
        if not self.children:
            return 1
        return sum(c.leaves() for c in self.children)

    def depth(self) -> int:
        if not self.children:
            return 1
        return 1 + max(c.depth() for c in self.children)

    def render(self, indent: int = 0) -> str:
        pad = "  " * indent
        line = f"{pad}{self.atom}   [{self.kind}]"
        return "\n".join([line] + [c.render(indent + 1) for c in self.children])


@dataclass(frozen=True)
class Solution:
    subst: Subst
    proof: Proof


class Engine:
    def __init__(self, kb: KnowledgeBase, max_depth: int = 32) -> None:
        self.kb = kb
        self.max_depth = max_depth
        self._gensym = count(1)

    # -- forward chaining ---------------------------------------------------
    def forward_chain(self) -> Set[Atom]:
        """Least fixpoint of the definite Horn program."""
        derived: Set[Atom] = set(self.kb.facts())
        # body-less rules act as stated facts
        for r in self.kb.rules():
            if not r.body and r.head.is_ground():
                derived.add(r.head)
        rules = list(self.kb.rules())
        changed = True
        while changed:
            changed = False
            index = self._index(derived)
            for r in rules:
                if not r.body:
                    continue
                for s in self._match_body(r.body, index, {}):
                    h = substitute_atom(r.head, s)
                    if h.is_ground() and h not in derived:
                        derived.add(h)
                        changed = True
        return derived

    @staticmethod
    def _index(facts: Iterable[Atom]) -> Dict[str, Tuple[Atom, ...]]:
        buckets: Dict[str, List[Atom]] = {}
        for f in facts:
            buckets.setdefault(f.pred, []).append(f)
        return {k: tuple(v) for k, v in buckets.items()}

    def _match_body(
        self, body: Sequence[Atom], index: Dict[str, Tuple[Atom, ...]], s: Subst
    ) -> Iterator[Subst]:
        if not body:
            yield s
            return
        first, rest = body[0], body[1:]
        for f in index.get(first.pred, ()):
            s2 = unify_atom(first, f, s)
            if s2 is not None:
                yield from self._match_body(rest, index, s2)

    # -- backward chaining (SLD) -------------------------------------------
    def prove(
        self, goal: Atom, depth: int = 0, subst: Optional[Subst] = None
    ) -> Iterator[Solution]:
        if subst is None:
            subst = {}
        if depth > self.max_depth:
            return
        g = substitute_atom(goal, subst)
        for f in self.kb.facts_for(g.pred):
            s2 = unify_atom(g, f, subst)
            if s2 is not None:
                yield Solution(s2, Proof(substitute_atom(goal, s2), "fact"))
        for r in self.kb.rules_for(g.pred):
            tag = next(self._gensym)
            rr = r.rename(str(tag))
            s2 = unify_atom(g, rr.head, subst)
            if s2 is None:
                continue
            yield from self._prove_body(
                rr.body, s2, depth + 1, rr, goal, ()
            )

    def _prove_body(
        self,
        body: Sequence[Atom],
        subst: Subst,
        depth: int,
        rule_: Rule,
        goal: Atom,
        acc: Tuple[Proof, ...],
    ) -> Iterator[Solution]:
        if not body:
            yield Solution(
                subst,
                Proof(substitute_atom(goal, subst), rule_.name or "rule", acc),
            )
            return
        first, rest = body[0], body[1:]
        for sol in self.prove(first, depth, subst):
            yield from self._prove_body(
                rest, sol.subst, depth, rule_, goal, acc + (sol.proof,)
            )

    # -- convenience --------------------------------------------------------
    def entails(self, goal: Atom) -> bool:
        return any(True for _ in self.prove(goal))

    def answers(self, goal: Atom) -> List[Atom]:
        out: List[Atom] = []
        seen: Set[Atom] = set()
        for sol in self.prove(goal):
            g = substitute_atom(goal, sol.subst)
            if g.is_ground() and g not in seen:
                seen.add(g)
                out.append(g)
        return out