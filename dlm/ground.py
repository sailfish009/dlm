"""DLM v0.0047 -- Ground / Experience / open entity universe (untrusted).

The architecture this module makes concrete:

* ``Ground``     -- immutable, non-referential (pronominal) domain axioms.
* ``Experience`` -- mutable rules learned on top of Ground.  Because Ground is
                    copied in as a base and rules are only added, Experience is a
                    conservative extension by construction: Ground's closure is
                    never lost.
* ``learn``      -- greedy covering driven by the *open universe*: a general rule
                    is a promise over all referents, so the signal is the positive
                    it does not yet derive (under) and the negative it would
                    derive (over).  A candidate is admitted only when the kernel
                    derives no negative with it (soundness) and it covers a
                    positive (progress).

Only the kernel (``closure``) decides truth.  Nothing here blocks software.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import Atom, Const, KnowledgeBase, Rule, Var, closure, description_length

__all__ = ["Ground", "Experience", "lgg_atoms", "variate", "learn", "LearnResult"]


@dataclass(frozen=True)
class Ground:
    """Immutable non-referential axioms."""

    rules: Tuple[Rule, ...] = ()

    @classmethod
    def from_forms(cls, forms: Sequence[tuple]) -> "Ground":
        from .lisp import form_to_rule
        return cls(tuple(form_to_rule(f) for f in forms))

    def base(self, facts: Iterable[Atom]) -> KnowledgeBase:
        kb = KnowledgeBase(set(facts))
        for r in self.rules:
            kb.add_rule(r)
        return kb


@dataclass(frozen=True)
class Experience:
    """Mutable learned rules over Ground (conservative extension by construction)."""

    rules: Tuple[Rule, ...] = ()

    def extend(self, rule: Rule) -> "Experience":
        return Experience(self.rules + (rule,))

    def to_kb(self, base: KnowledgeBase) -> KnowledgeBase:
        kb = base.copy()
        for r in self.rules:
            kb.add_rule(r)
        return kb


def lgg_atoms(examples: Sequence[Atom]) -> Atom:
    """Least general generalization (anti-unification) of ground atoms."""
    first = examples[0]
    mapping: Dict[tuple, Var] = {}
    args: List[object] = []
    for i in range(len(first.args)):
        col = tuple(a.args[i] for a in examples)
        if all(t == col[0] for t in col):
            args.append(col[0])
        else:
            args.append(mapping.setdefault(col, Var(f"G{len(mapping)}")))
    return Atom(first.pred, tuple(args))


def variate(atom: Atom) -> Atom:
    """Replace each distinct constant by a fresh variable."""
    seen: Dict[object, Var] = {}
    args: List[object] = []
    for t in atom.args:
        if isinstance(t, Var):
            args.append(t)
        else:
            args.append(seen.setdefault(t, Var(f"G{len(seen)}")))
    return Atom(atom.pred, tuple(args))


def _literals(base: KnowledgeBase, exp: Experience, pos: Sequence[Atom],
              variables: Sequence[Var]) -> List[Atom]:
    sigs = {(a.pred, len(a.args)) for a in base.facts}
    sigs |= {(r.head.pred, len(r.head.args)) for r in base.rules}
    sigs |= {(r.head.pred, len(r.head.args)) for r in exp.rules}
    sigs |= {(a.pred, len(a.args)) for a in pos}
    out: List[Atom] = []
    for pred, ar in sorted(sigs):
        if 1 <= ar <= 3:
            out.extend(Atom(pred, combo) for combo in itertools.product(variables, repeat=ar))
    return out


def _induce(base: KnowledgeBase, exp: Experience, uncovered: Sequence[Atom],
            negs: frozenset, *, max_body: int, extra_vars: int) -> Optional[Rule]:
    """Shortest kernel-sound generalization covering some uncovered positive.

    The head is induced only from uncovered positives that share the first
    one's predicate/arity: a single rule derives a single predicate, so mixing
    predicates in the LGG would be meaningless.
    """
    pos = sorted(uncovered, key=str)
    first = pos[0]
    group = [p for p in pos if p.pred == first.pred and len(p.args) == len(first.args)]
    head = lgg_atoms(group) if len(group) > 1 else variate(first)
    head_vars = [v for v in head.args if isinstance(v, Var)]
    variables = list(dict.fromkeys(head_vars)) + [Var(f"E{i}") for i in range(extra_vars)]
    universe = _literals(base, exp, group, variables)
    head_names = {v.name for v in head_vars}
    trial_base = exp.to_kb(base)
    for length in range(1, max_body + 1):
        for combo in itertools.combinations(universe, length):
            body_vars = {v.name for lit in combo for v in lit.args if isinstance(v, Var)}
            if not head_names <= body_vars:
                continue
            rule = Rule(head, combo, name=f"exp_{len(exp.rules)}")
            trial = trial_base.copy()
            trial.add_rule(rule)
            closed = closure(trial)
            if negs & closed:
                continue
            if set(group) & closed:
                return rule
    return None


@dataclass(frozen=True)
class LearnResult:
    experience: Experience
    covered: frozenset
    false_assert: frozenset
    rounds: Tuple[dict, ...]
    description_length: int

    @property
    def clauses(self) -> int:
        return len(self.experience.rules)


def learn(ground: Ground, facts: Iterable[Atom], positives: Iterable[Atom],
          negatives: Iterable[Atom], *, max_body: int = 2, extra_vars: int = 2,
          max_rules: int = 8, callback=None) -> LearnResult:
    """Greedy covering: grow Experience until positives are covered and no negative is.

    ``callback(experience, rule)`` is called after each admitted rule, so callers
    can observe the accumulated Experience round by round (e.g. held-out score).
    """
    base = ground.base(facts)
    negs = frozenset(negatives)
    pos = list(positives)
    exp = Experience()
    rounds: List[dict] = []
    for _ in range(max_rules):
        closed = closure(exp.to_kb(base))
        uncovered = [p for p in pos if p not in closed]
        if not uncovered:
            break
        rule = _induce(base, exp, uncovered, negs, max_body=max_body, extra_vars=extra_vars)
        if rule is None:
            rounds.append({"stop": "no_sound_generalization", "uncovered": len(uncovered)})
            break
        exp = exp.extend(rule)
        if callback is not None:
            callback(exp, rule)
        rounds.append({
            "added": str(rule.head) + " :- " + ", ".join(str(b) for b in rule.body),
            "uncovered_before": len(uncovered),
        })
    closed = closure(exp.to_kb(base))
    return LearnResult(
        experience=exp,
        covered=frozenset(p for p in pos if p in closed),
        false_assert=frozenset(n for n in negs if n in closed),
        rounds=tuple(rounds),
        description_length=description_length(ground.rules) + description_length(exp.rules),
    )