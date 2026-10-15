"""DLM v0.0048 -- the accumulating learner (untrusted).

``ground.learn`` always starts from a fresh ``Experience``: it is a *refit* over
whatever has been revealed so far, not an accumulation.  For a long run you need
the opposite: keep what you learned, accept new evidence, and -- crucially --
**retract** a rule that later evidence falsifies.

That retraction is the whole point.  A rule admitted when negatives are scarce
is sound on what has been seen; when the counterexample finally arrives it must
be dropped, not kept because it used to be right.  This is exactly the failure
the stream experiment exposes (seed 3: a ``located_in`` rule sound on the
revealed negatives but false on a later one).  ``learn`` is memoryless, so it
cannot express "this rule used to hold"; ``accumulate`` can.

Design (framework-before-primitive, COMPOSITION.md section 17):

* ``Learner`` is immutable; ``observe`` returns a new one.  It carries the
  Ground axioms, the accumulated ``Experience``, and every fact / positive /
  negative revealed so far.
* Each ``observe``:
  1. merge the new facts/positives/negatives (set union -- no duplicates);
  2. **prune**: keep only rules that stay sound against the *full* revealed
     negative complement, in insertion order (a greedy sound subset; the last
     admitted rule is the first suspect);
  3. **induce**: cover still-uncovered positives, skipping candidates that are
     structurally equal (up to variable renaming) to a rule already held;
  4. **compress** (optional): fold recurring bodies via ``abstract_theory``,
     accepting only a strict description-length drop the kernel certifies;
  5. record ``false_final`` = closure AND negatives over the FULL complement
     (never a sample), plus covered/uncovered and DL.

Only the kernel decides truth.  Nothing here asserts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from . import Atom, KnowledgeBase, Rule, Var, closure
from .abstract import abstract_theory, theory_dl
from .ground import Experience, Ground, _induce
from .lisp import atom_to_form, dump, rule_to_form
from .theory import Theory, atom_from_json, atom_to_json

__all__ = ["Learner", "rule_key"]


# --------------------------------------------------------------------------- #
# structural identity up to variable renaming
# --------------------------------------------------------------------------- #
def _ren_atom(a: Atom, m: dict) -> Atom:
    args = []
    for t in a.args:
        if isinstance(t, Var):
            args.append(m.setdefault(t.name, Var(f"?V{len(m)}")))
        else:
            args.append(t)
    return Atom(a.pred, tuple(args))


def rule_key(r: Rule) -> str:
    """Renaming-invariant key, so the same rule is never added twice."""
    m: dict = {}
    canon = Rule(_ren_atom(r.head, m), tuple(_ren_atom(b, m) for b in r.body))
    return dump(rule_to_form(canon))


# --------------------------------------------------------------------------- #
# greedy sound subset (retraction)
# --------------------------------------------------------------------------- #
def _prune(base: KnowledgeBase, rules: Sequence[Rule],
           negatives: frozenset) -> Tuple[List[Rule], List[Rule]]:
    """Keep the longest insertion-ordered prefix that derives no negative.

    A rule is kept only if adding it to the already-kept rules leaves the closure
    disjoint from the revealed negatives.  The result is sound by construction
    (not minimal): order is insertion order, so an older rule is defended before
    a newer one -- the newer rule is the one retracted when they conflict.
    """
    kept: List[Rule] = []
    dropped: List[Rule] = []
    if not negatives:
        return list(rules), dropped
    kb = base.copy()
    for r in rules:
        trial = kb.copy()
        trial.add_rule(r)
        if closure(trial) & negatives:
            dropped.append(r)
        else:
            kept.append(r)
            kb = trial
    return kept, dropped


def _safe_compress(base: KnowledgeBase, exp: Experience,
                   negatives: frozenset) -> Tuple[Experience, tuple]:
    """MDL-compress Experience, guarding soundness with the kernel.

    Ground's contribution is materialised into the seed facts first, so the
    abstraction is certified against the same closure the full theory sees.
    """
    if len(exp.rules) < 2:
        return exp, ()
    seed = closure(base)
    res = abstract_theory(exp.rules, seed)
    if res.dl_after >= res.dl_before:
        return exp, ()
    cand = Experience(tuple(res.theory))
    if closure(cand.to_kb(base)) & negatives:
        return exp, ()          # certified anyway, but never trust past the kernel
    return cand, res.abstractions


# --------------------------------------------------------------------------- #
# the learner
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Learner:
    ground: Ground = Ground()
    experience: Experience = Experience()
    facts: frozenset = frozenset()
    positives: frozenset = frozenset()
    negatives: frozenset = frozenset()
    memory: Tuple[dict, ...] = ()

    # -- introspection ----------------------------------------------------- #
    def base(self) -> KnowledgeBase:
        return self.ground.base(self.facts)

    def closure(self) -> frozenset:
        return frozenset(closure(self.experience.to_kb(self.base())))

    @property
    def dl(self) -> int:
        return theory_dl(self.ground.rules) + theory_dl(self.experience.rules)

    # -- the round --------------------------------------------------------- #
    def observe(self, *, facts: Iterable[Atom] = (), positives: Iterable[Atom] = (),
                negatives: Iterable[Atom] = (), max_body: int = 2, extra_vars: int = 2,
                max_rules: int = 8, compress: bool = True,
                retract: bool = True) -> "Learner":
        """One streaming round: merge, (retract), induce, (compress), record."""
        all_facts = self.facts | frozenset(facts)
        all_pos = self.positives | frozenset(positives)
        all_neg = self.negatives | frozenset(negatives)
        base = self.ground.base(all_facts)

        exp = self.experience
        dropped: List[Rule] = []
        if retract:
            kept, dropped = _prune(base, exp.rules, all_neg)
            exp = Experience(tuple(kept))

        have = {rule_key(r) for r in exp.rules}
        added: List[Rule] = []
        for _ in range(max_rules):
            closed = closure(exp.to_kb(base))
            uncovered = sorted((p for p in all_pos if p not in closed), key=str)
            if not uncovered:
                break
            rule = _induce(base, exp, uncovered, all_neg, max_body=max_body,
                           extra_vars=extra_vars)
            if rule is None or rule_key(rule) in have:
                break
            rule = Rule(rule.head, rule.body, name=f"acc{len(exp.rules)}")
            exp = exp.extend(rule)
            have.add(rule_key(rule))
            added.append(rule)

        abstractions: tuple = ()
        if compress:
            exp, abstractions = _safe_compress(base, exp, all_neg)

        closed = closure(exp.to_kb(base))
        false_final = sorted((n for n in all_neg if n in closed), key=str)
        covered = sum(1 for p in all_pos if p in closed)
        record = {
            "round": len(self.memory) + 1,
            "facts": len(all_facts),
            "revealed_negatives": len(all_neg),
            "positives": len(all_pos),
            "retracted": [_show(r) for r in dropped],
            "added": [_show(r) for r in added],
            "compressed": [f"{a.name} support={a.support} uses={a.uses}" for a in abstractions],
            "dl": theory_dl(exp.rules),
            "covered": covered,
            "uncovered": len(all_pos) - covered,
            "false_final": len(false_final),
            "false_atoms": [dump(atom_to_form(a)) for a in false_final],
        }
        return Learner(self.ground, exp, all_facts, all_pos, all_neg,
                       self.memory + (record,))

    # -- persistence ------------------------------------------------------- #
    def to_theory(self) -> Theory:
        meta = {
            "positives": [atom_to_json(a) for a in sorted(self.positives, key=str)],
            "negatives": [atom_to_json(a) for a in sorted(self.negatives, key=str)],
            "rounds": [dict(r) for r in self.memory],
        }
        return Theory(self.ground.rules, self.experience.rules, self.facts, meta)

    @classmethod
    def from_theory(cls, t: Theory) -> "Learner":
        meta = t.meta
        pos = frozenset(atom_from_json(a) for a in meta.get("positives", ()))
        neg = frozenset(atom_from_json(a) for a in meta.get("negatives", ()))
        return cls(Ground(t.ground), Experience(t.experience), t.facts, pos, neg,
                   tuple(meta.get("rounds", ())))


def _show(r: Rule) -> str:
    return dump(rule_to_form(r))