"""Module 19: rule induction and lemma extraction -- *verifiable* axiom acquisition.

Two ways to obtain a new rule that the kernel can trust:

1. **Lemma from a proof** (:func:`lemma_from_proof`, :func:`extract_lemmas`).  A
   rule obtained by resolving certified rules is valid *by construction*: the
   proof witnesses it.  This is the endogenous, no-oracle path.
2. **Induction checked over the finite domain** (:func:`verify_rule`).  A rule
   ``head :- body`` is valid on the KB iff **no** ground instance with a true body
   has a false head.  With finitely many constants that is a finite check, so it
   is a genuine (if bounded) validity test -- support counts witnesses,
   counterexamples are disqualifying.

Nothing here promotes an axiom; it produces candidates and the verdict that the
:class:`~dlm.axiom.AxiomStore` gate consumes.  A rule that cannot be checked
within the instance budget comes back ``complete=False`` and must not be trusted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .engine import closure
from .kb import KnowledgeBase
from .kernel import Proof
from .logic import Atom, Rule, Var
from .selfsup import compose_rules
from .unify import Subst, apply_atom, unify

__all__ = [
    "RuleCheck",
    "InducedRule",
    "ground_substitutions",
    "measure_rule",
    "verify_rule",
    "candidate_rules",
    "induce_rules",
    "lemma_from_proof",
    "extract_lemmas",
]


def _A(pred: str, *args) -> Atom:
    return Atom(pred, tuple(args))


def _index(atoms: Iterable[Atom]) -> Dict[str, Tuple[Atom, ...]]:
    out: Dict[str, List[Atom]] = {}
    for a in atoms:
        out.setdefault(a.pred, []).append(a)
    return {k: tuple(v) for k, v in out.items()}


def ground_substitutions(
    body: Sequence[Atom],
    index: Dict[str, Tuple[Atom, ...]],
    *,
    limit: int = 2000,
) -> Optional[List[Subst]]:
    """All substitutions making ``body`` true over the indexed ground atoms.

    Returns ``None`` when the join exceeds ``limit`` (indeterminate -- the caller
    must not treat it as valid).  An empty list means the body has no instance.
    """
    subs: List[Subst] = [{}]
    for atom in body:
        facts = index.get(atom.pred, ())
        nxt: List[Subst] = []
        for s in subs:
            for fact in facts:
                s2 = unify(atom, fact, s)
                if s2 is not None:
                    nxt.append(s2)
                    if len(nxt) > limit:
                        return None
        subs = nxt
        if not subs:
            return []
    return subs


@dataclass(frozen=True)
class RuleCheck:
    """The finite-domain verdict for a rule.

    ``valid`` is the soundness fact (no counterexample); ``complete`` says the
    check finished within budget; ``support`` counts true ground instances.
    """

    valid: bool
    support: int
    counterexamples: int
    complete: bool


def measure_rule(kb: KnowledgeBase, rule: Rule, *, max_instances: int = 2000) -> RuleCheck:
    """Check ``rule`` against ``kb``'s closure over the finite domain."""
    cl = closure(kb)
    index = _index(cl)
    subs = ground_substitutions(rule.body, index, limit=max_instances)
    if subs is None:
        return RuleCheck(valid=False, support=0, counterexamples=0, complete=False)
    support = 0
    counterexamples = 0
    for s in subs:
        head = apply_atom(rule.head, s)
        if not head.is_ground():
            return RuleCheck(valid=False, support=support, counterexamples=counterexamples, complete=False)
        if head in cl:
            support += 1
        else:
            counterexamples += 1
    return RuleCheck(
        valid=counterexamples == 0 and support > 0,
        support=support,
        counterexamples=counterexamples,
        complete=True,
    )


def verify_rule(kb: KnowledgeBase, rule: Rule, *, max_instances: int = 2000) -> Optional[bool]:
    """``True`` if the rule is valid on ``kb``; ``None`` if indeterminate.

    Indeterminate (budget exceeded) is *not* ``False`` and *not* ``True`` -- the
    caller must abstain, never assume.
    """
    chk = measure_rule(kb, rule, max_instances=max_instances)
    if not chk.complete:
        return None
    return chk.valid


def candidate_rules(kb: KnowledgeBase, *, max_body: int = 2) -> Tuple[Rule, ...]:
    """Schema-agnostic binary-rule candidates (transitivity chains + inverses).

    Only predicates that actually occur as ground facts are considered, so the
    search is bounded by the KB's vocabulary, not by an open grammar.
    """
    if max_body < 1:
        raise ValueError("max_body must be >= 1")
    binpreds = sorted({a.pred for a in kb.facts() if a.arity == 2})
    x, y, z = Var("x"), Var("y"), Var("z")
    rules: List[Rule] = []

    def add(rule: Rule) -> None:
        if rule not in rules:
            rules.append(rule)

    for p in binpreds:
        add(Rule(_A(p, x, z), (_A(p, x, y), _A(p, y, z)), f"{p}_trans"))
    if max_body >= 2:
        for p in binpreds:
            for q in binpreds:
                if p != q:
                    add(Rule(_A(p, x, z), (_A(p, x, y), _A(q, y, z)), f"{p}_via_{q}"))
                    add(Rule(_A(p, x, y), (_A(q, y, x),), f"{p}_inv_{q}"))
                else:
                    add(Rule(_A(p, x, y), (_A(p, y, x),), f"{p}_inv"))
    return tuple(rules)


@dataclass(frozen=True)
class InducedRule:
    """A candidate rule plus the evidence that judges it."""

    rule: Rule
    support: int
    counterexamples: int

    @property
    def sound(self) -> bool:
        return self.counterexamples == 0 and self.support > 0


def induce_rules(
    kb: KnowledgeBase,
    *,
    min_support: int = 1,
    max_counterexamples: Optional[int] = None,
    max_body: int = 2,
    max_instances: int = 2000,
) -> Tuple[InducedRule, ...]:
    """Generate and *check* candidate rules, ranked by support.

    A candidate is kept when its check is complete and it has at least
    ``min_support`` true ground instances.  By default no counterexample cap is
    applied: the result is a **candidate pool**.  Pass ``max_counterexamples=0``
    (or ``sound_only`` logic via :meth:`InducedRule.sound`) to keep only rules
    the kernel already entails -- those are the ones safe to promote to kernel
    tier.  Rules with counterexamples may only ever be *candidates* until an
    external channel corroborates them.
    """
    out: List[InducedRule] = []
    for rule in candidate_rules(kb, max_body=max_body):
        chk = measure_rule(kb, rule, max_instances=max_instances)
        if not chk.complete:
            continue
        if chk.support < min_support:
            continue
        if max_counterexamples is not None and chk.counterexamples > max_counterexamples:
            continue
        out.append(InducedRule(rule, chk.support, chk.counterexamples))
    return tuple(sorted(out, key=lambda ir: (-ir.support, ir.counterexamples, str(ir.rule))))


# -- lemmas: rules valid by construction from a proof ----------------------
def lemma_from_proof(proof: Proof, kb: KnowledgeBase) -> Optional[Rule]:
    """Resolve a top-of-proof rule with a premise rule to get a new, valid lemma."""
    if proof.rule is None:
        return None
    for premise in proof.premises:
        if premise.rule is None:
            continue
        for composed in compose_rules(premise.rule, proof.rule):
            if composed not in kb.rules():
                return composed
    return None


def extract_lemmas(
    kb: KnowledgeBase,
    *,
    atoms: Optional[Iterable[Atom]] = None,
    max_instances: int = 2000,
) -> Tuple[Rule, ...]:
    """Compose certified rules pairwise and keep the new, independently valid ones."""
    out: List[Rule] = []
    for r1 in kb.rules():
        for r2 in kb.rules():
            for composed in compose_rules(r1, r2):
                if composed in kb.rules() or composed in out:
                    continue
                if verify_rule(kb, composed, max_instances=max_instances) is True:
                    out.append(composed)
    return tuple(out)