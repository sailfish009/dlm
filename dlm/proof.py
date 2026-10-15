"""DLM v0.0047 -- proof as data (untrusted).

``closure`` returns a *set* of atoms, but compression needs a *tree*.  A
:class:`Proof` is a certifying derivation tree: an atom, the rule that derived
it, and the premise proofs.  It is untrusted data -- believed only when
:func:`verify` re-derives it against the kernel.  Nothing here asserts truth.

A proof is the DLM analogue of the LLM's token sequence: the object a learner can
look at, measure, and shorten.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from . import Atom, KnowledgeBase, Rule, Var, unify
from .lisp import atom_to_form, form_to_atom, form_to_rule, rule_to_form

__all__ = ["Proof", "prove", "verify", "proof_size", "proof_ir", "form_to_proof"]


@dataclass(frozen=True)
class Proof:
    """A derivation: ``atom`` was derived by ``rule`` from ``premises``.

    ``rule is None`` marks a leaf fact.  Premises are the substituted body atoms
    of the rule instance, each with its own proof.
    """

    atom: Atom
    rule: Optional[Rule] = None
    premises: Tuple["Proof", ...] = ()

    @property
    def is_fact(self) -> bool:
        return self.rule is None


def _subst(atom: Atom, s: Dict[str, Any]) -> Atom:
    return Atom(atom.pred, tuple(s.get(t.name, t) if isinstance(t, Var) else t for t in atom.args))


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


def prove(kb: KnowledgeBase, atom: Atom) -> Optional[Proof]:
    """Return a proof of ``atom`` from ``kb``, or ``None`` (abstain).

    Forward chaining with provenance: every derived atom records the rule
    instance and the premise proofs that produced it.
    """
    if atom in kb.facts:
        return Proof(atom, None, ())
    facts = set(kb.facts)
    prov: Dict[Atom, Proof] = {f: Proof(f, None, ()) for f in facts}
    changed = True
    while changed:
        changed = False
        by_pred: dict = {}
        for f in facts:
            by_pred.setdefault(f.pred, []).append(f)
        for rule in kb.rules:
            for s in _join(rule.body, by_pred):
                h = _subst(rule.head, s)
                if not h.is_ground() or h in facts:
                    continue
                premises = tuple(prov[_subst(b, s)] for b in rule.body)
                facts.add(h)
                prov[h] = Proof(h, rule, premises)
                changed = True
                if h == atom:
                    return prov[h]
    return prov.get(atom)


def verify(proof: Proof, kb: KnowledgeBase) -> bool:
    """Re-check a proof against the kernel.  A proof is believed only if it holds.

    Body variables are bound by the premises, not by the head, so the rule
    instance is reconstructed premise by premise while unifying the body.
    """
    if proof.rule is None:
        return proof.atom in kb.facts
    s = unify(proof.rule.head, proof.atom)
    if s is None or len(proof.premises) != len(proof.rule.body):
        return False
    for body_atom, premise in zip(proof.rule.body, proof.premises):
        s = unify(body_atom, premise.atom, s)
        if s is None or not verify(premise, kb):
            return False
    return True


def proof_size(proof: Proof) -> int:
    """Number of derivation nodes -- the description length of a proof."""
    return 1 + sum(proof_size(p) for p in proof.premises)


def proof_ir(proof: Proof) -> Any:
    """The proof as an IR form: ``(proof <atom> <rule|fact> <premise>...)``."""
    tail = ("fact",) if proof.rule is None else rule_to_form(proof.rule)
    return ("proof", atom_to_form(proof.atom)) + tuple([tail]) + tuple(
        proof_ir(p) for p in proof.premises
    )


def form_to_proof(form: Any) -> Proof:
    """Inverse of :func:`proof_ir` -- read a proof back from its form.

    The form is untrusted data; :func:`verify` is what decides whether it holds.
    """
    atom = form_to_atom(form[1])
    tail = form[2]
    if isinstance(tail, tuple) and tail and tail[0] == "fact":
        return Proof(atom, None, ())
    rule = form_to_rule(tail)
    return Proof(atom, rule, tuple(form_to_proof(p) for p in form[3:]))