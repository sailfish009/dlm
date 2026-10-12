"""DLM v0.0030 -- the explanation / abstraction layer (NOTE 82).

A deductive model's beliefs, inferences and revisions are all *objects*, so its
interpretability should not be a post-hoc probe but a first-class output.  Yet a
grown theory can still become unauditable simply by getting large: a million
inspectable clauses are as opaque as a black box.  This untrusted layer adds the
missing half of "extreme interpretability" -- at-scale, kernel-verified
*self-interpretation*.

Four things, all read-only over the trusted core (it never asserts anything):

* **description length** -- an explicit, reviewable size accounting of a theory
  (clauses, literals, vocabulary, review budget);
* **proof-carrying hypotheses** -- a :class:`Provenance` registry that records
  *why* each learned clause is believed (the witnesses that support it, the
  round, its parent), so a belief answers "why?" with a term, not a scalar;
* **abstraction** -- group clauses into named modules and summarise a theory
  level by level, so a large KB is reviewed by hierarchy, not flat;
* **exact compression + explanation** -- drop clauses whose removal provably
  leaves the kernel closure unchanged, and answer a goal with a re-checkable
  proof, its clauses, their provenance, and counterfactuals.

Trust boundary: every "equivalent"/"proved"/"dropped" claim is decided by the
kernel (``closure`` / ``verify``), never by this layer.  ``compress`` drops a
clause only after re-computing the closure without it and checking equality, so
it is behaviour-preserving *on the given KB* (not a proof of logical equivalence
in all models).  This layer imports the trusted core one-way; the kernel imports
nothing from it and stays function-free.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from . import (
    Atom,
    KnowledgeBase,
    Proof,
    closure,
    prove,
    verify,
)
from .deductive import Clause, Theory

__all__ = [
    # description length
    "clause_literals",
    "TheoryProfile",
    "profile",
    "description_length",
    # proof-carrying hypotheses
    "Derivation",
    "Provenance",
    "certify",
    "certify_from_tasks",
    # abstraction
    "Module",
    "Abstraction",
    "abstract_theory",
    "summarize",
    # exact compression
    "Compression",
    "redundant",
    "compress",
    "closure_preserved",
    # explanation
    "Explanation",
    "proof_rule_names",
    "explain",
    "counterfactual",
    "minimal_explanation",
    "verify_explanation",
]


# ============================================================================
# 1. description length -- the audit cost, made explicit
# ============================================================================
def clause_literals(clause: Clause) -> int:
    """Head + body literals of one clause (its syntactic size)."""
    return 1 + len(clause.rule.body)


@dataclass(frozen=True)
class TheoryProfile:
    """A reviewable size accounting of a theory."""

    name: str
    clauses: int
    literals: int
    vocabulary: Tuple[Tuple[str, int], ...]

    @property
    def description_length(self) -> int:
        """Syntactic units a reader must scan: literals plus clause frames."""
        return self.literals + self.clauses

    @property
    def review_budget(self) -> int:
        """Description length plus the symbols of the signature."""
        return self.description_length + len(self.vocabulary)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "clauses": self.clauses,
            "literals": self.literals,
            "vocabulary": [f"{p}/{a}" for p, a in self.vocabulary],
            "description_length": self.description_length,
            "review_budget": self.review_budget,
        }


def _vocabulary(theory: Theory) -> Tuple[Tuple[str, int], ...]:
    sigs = set()
    for c in theory.clauses:
        rule = c.rule
        sigs.add((rule.head.pred, rule.head.arity))
        for lit in rule.body:
            sigs.add((lit.pred, lit.arity))
    return tuple(sorted(sigs))


def profile(theory: Theory) -> TheoryProfile:
    """Count clauses, literals and the signature of a theory."""
    clauses = len(theory.clauses)
    literals = sum(clause_literals(c) for c in theory.clauses)
    return TheoryProfile(theory.name, clauses, literals, _vocabulary(theory))


def description_length(theory: Theory) -> int:
    """The number of syntactic units a human must scan to audit the theory."""
    return profile(theory).description_length


# ============================================================================
# 2. proof-carrying hypotheses -- why each clause is believed
# ============================================================================
@dataclass(frozen=True)
class Derivation:
    """Why one clause is believed: its witnesses, round, and parent."""

    name: str
    head: str
    support: Tuple[str, ...] = ()
    negative: Tuple[str, ...] = ()
    round: int = -1
    parent: Optional[str] = None
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "head": self.head,
            "support": list(self.support),
            "negative": list(self.negative),
            "round": self.round,
            "parent": self.parent,
            "note": self.note,
        }


@dataclass
class Provenance:
    """A registry of derivations -- a proof-carrying view of a theory's beliefs."""

    table: Dict[str, Derivation] = field(default_factory=dict)

    def record(self, derivation: Derivation) -> "Provenance":
        self.table[derivation.name] = derivation
        return self

    def get(self, name: str) -> Optional[Derivation]:
        return self.table.get(name)

    def names(self) -> Tuple[str, ...]:
        return tuple(sorted(self.table))

    def missing(self, theory: Theory) -> Tuple[str, ...]:
        """Clauses of ``theory`` with no recorded derivation (an audit gap)."""
        known = set(self.table)
        return tuple(c.name for c in theory.clauses if c.name not in known)

    def of(self, theory: Theory) -> Tuple[dict, ...]:
        """The provenance of each clause, in theory order (unknown ones flagged)."""
        out = []
        for c in theory.clauses:
            d = self.table.get(c.name)
            if d is None:
                out.append({"name": c.name, "head": c.rule.head.pred, "known": False})
            else:
                out.append(d.to_dict())
        return tuple(out)

    def to_dict(self) -> dict:
        return {name: self.table[name].to_dict() for name in self.names()}


def certify(
    theory: Theory,
    support: Mapping[str, Sequence[Atom]],
    *,
    negatives: Optional[Mapping[str, Sequence[Atom]]] = None,
    rounds: Optional[Mapping[str, int]] = None,
    parents: Optional[Mapping[str, str]] = None,
    notes: Optional[Mapping[str, str]] = None,
) -> Provenance:
    """Attach a :class:`Derivation` to every clause of ``theory``.

    Witnesses are whatever the caller supplies; this layer never invents labels.
    Missing witnesses are recorded as an empty (not fabricated) support.
    """
    negatives = negatives or {}
    rounds = rounds or {}
    parents = parents or {}
    notes = notes or {}
    prov = Provenance()
    for c in theory.clauses:
        prov.record(
            Derivation(
                name=c.name,
                head=c.rule.head.pred,
                support=tuple(sorted(str(a) for a in support.get(c.name, ()))),
                negative=tuple(sorted(str(a) for a in negatives.get(c.name, ()))),
                round=int(rounds.get(c.name, -1)),
                parent=parents.get(c.name),
                note=notes.get(c.name, ""),
            )
        )
    return prov


def certify_from_tasks(theory: Theory, tasks: Sequence[Any]) -> Provenance:
    """Witness each clause by its *unique* contribution to the grown theory.

    For the task whose name matches a clause's head predicate, the clause's
    support is the set of that task's positives derivable with the clause but
    **not** without it (its marginal contribution in context); its negative is
    any negative the theory wrongly derives.  Truth is computed by the kernel --
    nothing is labelled by hand here, and a redundant clause gets empty support.
    """
    support: Dict[str, List[Atom]] = {c.name: [] for c in theory.clauses}
    negatives: Dict[str, List[Atom]] = {c.name: [] for c in theory.clauses}
    rounds: Dict[str, int] = {}
    for index, task in enumerate(tasks):
        name = getattr(task, "name", None)
        full = closure(theory.to_kb(task.kb))
        for c in theory.clauses:
            if c.rule.head.pred != name:
                continue
            rounds.setdefault(c.name, index)
            rest = Theory(theory.name, tuple(x for x in theory.clauses if x.name != c.name))
            without = closure(rest.to_kb(task.kb))
            for atom in task.positives:
                if atom in full and atom not in without and atom not in support[c.name]:
                    support[c.name].append(atom)
            for atom in task.negatives:
                if atom in full and atom not in negatives[c.name]:
                    negatives[c.name].append(atom)
    return certify(theory, support, negatives=negatives, rounds=rounds)


# ============================================================================
# 3. abstraction -- review a theory level by level, not flat
# ============================================================================
@dataclass(frozen=True)
class Module:
    """A named group of clauses sharing a head predicate -- one reviewable unit."""

    name: str
    clauses: Tuple[Clause, ...]

    @property
    def size(self) -> int:
        return len(self.clauses)

    @property
    def predicates(self) -> Tuple[str, ...]:
        """Every predicate mentioned (head or body) -- the module's interface."""
        sigs = set()
        for c in self.clauses:
            sigs.add(c.rule.head.pred)
            for lit in c.rule.body:
                sigs.add(lit.pred)
        return tuple(sorted(sigs))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "size": self.size,
            "predicates": list(self.predicates),
            "clauses": [c.name for c in self.clauses],
        }


@dataclass(frozen=True)
class Abstraction:
    """A theory grouped into named modules -- self-interpretation level by level."""

    name: str
    modules: Tuple[Module, ...]

    @property
    def profile(self) -> TheoryProfile:
        clauses = tuple(c for m in self.modules for c in m.clauses)
        return profile(Theory(self.name, clauses))

    @property
    def review_budget(self) -> int:
        """Modules to open + clauses/literals to read + signature symbols."""
        return len(self.modules) + self.profile.description_length

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "modules": [m.to_dict() for m in self.modules],
            "profile": self.profile.to_dict(),
            "review_budget": self.review_budget,
        }


def abstract_theory(theory: Theory, *, by: str = "head") -> Abstraction:
    """Group clauses by head predicate (deterministic order) into modules."""
    if by != "head":
        raise ValueError("abstract_theory only supports by='head'")
    groups: Dict[str, List[Clause]] = {}
    for c in theory.clauses:
        groups.setdefault(c.rule.head.pred, []).append(c)
    modules = tuple(
        Module(pred, tuple(sorted(groups[pred], key=lambda c: c.name)))
        for pred in sorted(groups)
    )
    return Abstraction(theory.name, modules)


def summarize(theory: Theory) -> dict:
    """A compact, human/machine-readable summary of a theory."""
    abst = abstract_theory(theory)
    return {
        "profile": profile(theory).to_dict(),
        "modules": [
            {"name": m.name, "size": m.size, "predicates": list(m.predicates)}
            for m in abst.modules
        ],
        "review_budget": abst.review_budget,
    }


# ============================================================================
# 4. exact compression -- drop only what the kernel cannot notice
# ============================================================================
@dataclass(frozen=True)
class Compression:
    """The result of exact (closure-preserving) compression."""

    name: str
    theory: Theory
    dropped: Tuple[str, ...]
    before: TheoryProfile
    after: TheoryProfile

    @property
    def saved(self) -> int:
        return self.before.description_length - self.after.description_length

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "dropped": list(self.dropped),
            "kept": [c.name for c in self.theory.clauses],
            "before": self.before.to_dict(),
            "after": self.after.to_dict(),
            "saved": self.saved,
        }


def closure_preserved(old: Theory, new: Theory, kb: KnowledgeBase) -> bool:
    """Exact check: installing either theory on ``kb`` yields the same closure."""
    return closure(old.to_kb(kb)) == closure(new.to_kb(kb))


def compress(theory: Theory, kb: KnowledgeBase) -> Compression:
    """Greedily drop clauses whose removal leaves the kernel closure unchanged.

    Exact and deterministic: a clause is dropped only after re-computing the
    closure without it and finding it equal to the original closure.  This is
    behaviour-preserving on ``kb`` -- it is *not* a proof of logical equivalence
    in all models, and the report says so.
    """
    full = closure(theory.to_kb(kb))
    keep = sorted(theory.clauses, key=lambda c: (c.name,))
    dropped: List[str] = []
    i = 0
    while i < len(keep):
        trial = keep[:i] + keep[i + 1:]
        tkb = kb.copy()
        for c in trial:
            tkb.add_rule(c.rule)
        if closure(tkb) == full:
            dropped.append(keep[i].name)
            keep = trial
        else:
            i += 1
    new = Theory(theory.name, tuple(keep))
    return Compression(
        theory.name, new, tuple(sorted(dropped)), profile(theory), profile(new)
    )


def redundant(theory: Theory, kb: KnowledgeBase) -> Tuple[str, ...]:
    """Names of clauses an exact compression would drop (behaviour-preserving)."""
    return compress(theory, kb).dropped


# ============================================================================
# 5. explanation -- a goal answered with a re-checkable proof
# ============================================================================
@dataclass(frozen=True)
class Explanation:
    """A goal answered with a re-checkable proof, its clauses, and provenance."""

    goal: Atom
    proved: bool
    proof: Optional[Proof]
    clauses: Tuple[str, ...]
    proof_length: int
    provenance: Tuple[dict, ...] = ()

    def to_dict(self) -> dict:
        return {
            "goal": str(self.goal),
            "proved": self.proved,
            "clauses": list(self.clauses),
            "proof_length": self.proof_length,
            "proof": None if self.proof is None else str(self.proof),
            "provenance": [dict(p) for p in self.provenance],
        }


def proof_rule_names(proof: Optional[Proof]) -> Tuple[str, ...]:
    """Distinct rule names used by a proof, in first-seen (pre-order) order."""
    if proof is None:
        return ()
    seen: List[str] = []

    def walk(p: Proof) -> None:
        if p.rule is not None:
            name = p.rule.name or str(p.rule)
            if name not in seen:
                seen.append(name)
        for prem in p.premises:
            walk(prem)

    walk(proof)
    return tuple(seen)


def _proof_size(proof: Optional[Proof]) -> int:
    """Number of proof nodes (the reader's step count for one answer)."""
    if proof is None:
        return 0
    return 1 + sum(_proof_size(p) for p in proof.premises)


def explain(
    kb: KnowledgeBase,
    theory: Theory,
    goal: Atom,
    *,
    provenance: Optional[Provenance] = None,
) -> Explanation:
    """Prove ``goal`` with ``theory`` on ``kb`` and return the explanation.

    The proof comes from the kernel; this layer only *reads* it (collecting the
    rule names used and attaching their provenance) and never asserts.
    """
    proof = prove(theory.to_kb(kb), goal)
    names = proof_rule_names(proof)
    prov: Tuple[dict, ...] = ()
    if provenance is not None:
        prov = tuple(
            provenance.get(n).to_dict()
            if provenance.get(n) is not None
            else {"name": n, "known": False}
            for n in names
        )
    return Explanation(goal, proof is not None, proof, names, _proof_size(proof), prov)


def counterfactual(
    kb: KnowledgeBase,
    theory: Theory,
    goal: Atom,
    *,
    drop: Sequence[str],
) -> bool:
    """Is ``goal`` still provable after removing the named clauses? (Ablation.)"""
    d = set(drop)
    reduced = Theory(theory.name, tuple(c for c in theory.clauses if c.name not in d))
    return prove(reduced.to_kb(kb), goal) is not None


def minimal_explanation(kb: KnowledgeBase, theory: Theory, goal: Atom) -> Explanation:
    """Compress the theory *for this goal*: keep only the clauses its proof needs."""
    proof = prove(theory.to_kb(kb), goal)
    if proof is None:
        return Explanation(goal, False, None, (), 0, ())
    needed = set(proof_rule_names(proof))
    reduced = Theory(theory.name, tuple(c for c in theory.clauses if c.name in needed))
    return explain(kb, reduced, goal)


def verify_explanation(kb: KnowledgeBase, theory: Theory, explanation: Explanation) -> bool:
    """Re-check an explanation against the kernel: proof sound and clauses honest."""
    if explanation.proof is None:
        return not explanation.proved
    if not verify(explanation.proof, theory.to_kb(kb)):
        return False
    return set(explanation.clauses) == set(proof_rule_names(explanation.proof))
