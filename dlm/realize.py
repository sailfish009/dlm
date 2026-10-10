"""Module 11: the output boundary -- a Realizer with a trusted round-trip check.

DLM's egress has been *template-only* (NOTE.md §28.1): the wire assembles an
answer from a proof-backed verdict and never generates prose.  This module adds
an **optional** egress boundary (seam E) that may produce natural language -- but
only from a kernel-authorized bundle, and only if the text survives a trusted
check.  It is the egress mirror of the ingress firewall (§27): NL exists at the
two boundaries, never inside the model.

The shape (NOTE.md §32.4)::

    kernel-authorized Bundle {abstain, verdict, literal, proof, reason}
       | (untrusted)
       v  Realizer (template / LM)  -> candidate text
       |  Ingestor.literal (seam B, deterministic)  -> re-parsed Literal
       v  re-parsed == bundle.literal ?
          yes -> emit ;  no -> fallback / abstain

Two invariants make generation safe:

* **The kernel still asserts.**  A realizer only *proposes* surface form.  The
  trusted gate re-parses the candidate with the *same* deterministic reader used
  at ingress and accepts it only if it round-trips to exactly the asserted
  literal.  A realizer that lies (or is fooled) cannot put a claim into the
  output that the kernel did not already assert.
* **Abstain is never verbalized.**  If ``bundle.abstain`` is true, no realizer is
  consulted at all -- the honesty fields stay authoritative and no prose is
  invented for a miss.

Everything here is stdlib-only.  A learned realizer (e.g. a MeowLLM-style decoder)
plugs in as the untrusted ``Realizer``; the check is what makes it safe.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Mapping, Optional, Protocol, Tuple, runtime_checkable

from .convert import Ingestor
from .judge import Judgement, Verdict
from .kernel import Proof
from .logic import Atom, Const, Literal, SchemaRegistry
from .reader import AGENT, FIGURE, GROUND, PATIENT, SUBJECT
from .sexp import SexpError

__all__ = [
    "Bundle",
    "Realization",
    "Realizer",
    "TemplateRealizer",
    "CheckedRealizer",
    "RealizedService",
    "bundle_from_answer",
]


# -- the kernel-authorized bundle ------------------------------------------
@dataclass(frozen=True)
class Bundle:
    """What a realizer is allowed to verbalize: a decided verdict, nothing more.

    Built from a :class:`~dlm.judge.Judgement` (the trusted verdict) or from a
    wire answer.  ``literal`` is the *only* content a realizer may express; it
    carries no license to add, drop or weaken anything.
    """

    verdict: str
    abstain: bool
    literal: Optional[Literal] = None
    proof: Optional[Proof] = None
    reason: Optional[str] = None

    @property
    def asserted(self) -> bool:
        return not self.abstain and self.verdict == Verdict.ASSERTED.value

    @property
    def refuted(self) -> bool:
        return not self.abstain and self.verdict == Verdict.REFUTED.value

    @classmethod
    def from_judgement(cls, judgement: Judgement) -> "Bundle":
        return cls(
            verdict=judgement.verdict.value,
            abstain=not judgement.decided,
            literal=judgement.literal,
            proof=judgement.proof,
            reason=None if judgement.decided else "not decided",
        )


def _literal_from_text(ingestor: Ingestor, raw: Any) -> Optional[Literal]:
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        logic = ingestor.logic(raw)
    except SexpError:
        return None
    if isinstance(logic, Literal):
        return logic
    if isinstance(logic, Atom):
        return Literal(logic, negated=False)
    return None


def bundle_from_answer(answer: Mapping[str, Any], ingestor: Ingestor) -> Bundle:
    """Reconstruct a :class:`Bundle` from one wire answer (S-expr fields).

    ``literal`` is parsed from the answer's S-expr string (path (b) of ingress);
    a ``choice`` answer uses the chosen option's literal.  The proof object cannot
    be reconstructed from its display string, so ``proof`` is left ``None``.
    """
    verdict = str(answer.get("verdict", Verdict.ABSTAIN.value))
    abstain = bool(answer.get("abstain", True))
    literal = _literal_from_text(ingestor, answer.get("literal"))
    if literal is None and answer.get("type") == "choice" and answer.get("choice") is not None:
        literals = answer.get("literals")
        if isinstance(literals, Mapping):
            literal = _literal_from_text(ingestor, literals.get(answer["choice"]))
    return Bundle(
        verdict=verdict,
        abstain=abstain,
        literal=literal,
        reason=answer.get("reason") if isinstance(answer.get("reason"), str) else None,
    )


# -- the realizer protocol (untrusted) -------------------------------------
@runtime_checkable
class Realizer(Protocol):
    """Seam E.  Untrusted: proposes surface text for a kernel-authorized bundle.

    Return ``None`` to decline.  The output is a *proposal*; a
    :class:`CheckedRealizer` is what makes it safe to emit.
    """

    def realize(self, bundle: Bundle) -> Optional[str]:  # pragma: no cover - protocol
        ...


# -- the deterministic template realizer -----------------------------------
_CANONICAL_ROLES = (
    frozenset({AGENT}),
    frozenset({AGENT, PATIENT}),
    frozenset({SUBJECT}),
    frozenset({FIGURE, GROUND}),
)


class TemplateRealizer:
    """The closed-subset inverse: a Literal rendered to a canonical sentence.

    Deterministic and stdlib-only; it renders by *role*, so the schema decides
    argument order and a copular predication keeps its copula.  Unknown predicates
    (no schema), unknown role sets, and non-ground literals return ``None`` -- the
    realizer declines rather than guess.  Negation is inserted so the reader's
    sign logic recovers it.
    """

    def __init__(self, registry: SchemaRegistry) -> None:
        self.registry = registry

    # -- public ------------------------------------------------------------
    def realize(self, bundle: Bundle) -> Optional[str]:
        if bundle.abstain or bundle.literal is None:
            return None
        return self.render(bundle.literal)

    def render(self, literal: Literal) -> Optional[str]:
        if not literal.is_ground():
            return None
        atom = literal.atom
        schema = self.registry.get(atom.pred)
        if schema is None or frozenset(schema.roles) not in _CANONICAL_ROLES:
            return None
        filled = dict(zip(schema.roles, atom.args))
        roles = frozenset(schema.roles)

        if roles == frozenset({AGENT}):
            subject = _ent(filled[AGENT])
            core = f"{subject} {atom.pred}"
            return f"{subject} not {atom.pred}" if literal.negated else core
        if roles == frozenset({AGENT, PATIENT}):
            agent, patient = _ent(filled[AGENT]), _ent(filled[PATIENT])
            core = f"{agent} {atom.pred} {patient}"
            return f"{agent} not {atom.pred} {patient}" if literal.negated else core
        if roles == frozenset({SUBJECT}):
            subject = _ent(filled[SUBJECT])
            core = f"{subject} is {atom.pred}"
            return f"{subject} is not {atom.pred}" if literal.negated else core
        # FIGURE, GROUND -- a prepositional relation; the predicate *is* the prep
        figure, ground = _ent(filled[FIGURE]), _ent(filled[GROUND])
        core = f"{figure} is {atom.pred} {ground}"
        return f"{figure} is not {atom.pred} {ground}" if literal.negated else core

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"TemplateRealizer({self.registry!r})"


def _ent(term: Any) -> str:
    return term.name if isinstance(term, Const) else str(term)


# -- the trusted gate ------------------------------------------------------
@dataclass(frozen=True)
class Realization:
    """The outcome of a checked realization (accepted text, or why it was not)."""

    text: Optional[str]
    accepted: bool
    round_trip: bool
    source: str
    reason: str


class CheckedRealizer:
    """Wrap an untrusted ``Realizer`` with the trusted round-trip gate.

    A candidate is emitted only if re-reading it through the ingress
    :class:`~dlm.convert.Ingestor` yields exactly ``bundle.literal``.  ``fallback``
    is consulted (and checked the same way) when the primary candidate fails.
    Abstain bundles are never handed to any realizer.
    """

    def __init__(
        self,
        realizer: Realizer,
        ingestor: Ingestor,
        *,
        fallback: Optional[Realizer] = None,
    ) -> None:
        self.realizer = realizer
        self.ingestor = ingestor
        self.fallback = fallback

    def _chain(self) -> Iterator[Tuple[str, Realizer]]:
        yield "realizer", self.realizer
        if self.fallback is not None:
            yield "fallback", self.fallback

    def realize_checked(self, bundle: Bundle) -> Realization:
        if bundle.abstain:
            return Realization(None, False, False, "guard", "abstain bundles are never realized")
        if bundle.literal is None:
            return Realization(None, False, False, "guard", "no asserted literal to realize")
        if not bundle.literal.is_ground():
            return Realization(None, False, False, "guard", "non-ground literal cannot be realized")

        mismatch: Optional[Tuple[str, str, Optional[Literal]]] = None
        for source, realizer in self._chain():
            text = realizer.realize(bundle)
            if text is None or not text.strip():
                continue
            text = text.strip()
            parsed = self.ingestor.literal(text)
            if parsed is not None and parsed == bundle.literal:
                return Realization(text, True, True, source, "round-trip ok")
            mismatch = (source, text, parsed)

        if mismatch is not None:
            source, text, parsed = mismatch
            detail = "unreadable" if parsed is None else f"-> {parsed}"
            return Realization(None, False, False, source, f"round-trip mismatch: {text!r} {detail}")
        return Realization(None, False, False, "check", "no candidate text")

    # -- the Realizer protocol method -------------------------------------
    def realize(self, bundle: Bundle) -> Optional[str]:
        return self.realize_checked(bundle).text

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"CheckedRealizer({self.realizer!r}, fallback={self.fallback!r})"


# -- wire integration ------------------------------------------------------
class RealizedService:
    """Wrap a wire service so each answer gets a *checked* ``text`` field.

    ``text`` is present iff the answer was decided **and** a candidate
    round-tripped to the asserted literal; an abstain (or an unchecked candidate)
    gets ``text = None``.  The original answer fields are untouched, so a consumer
    can still read the honesty fields.
    """

    def __init__(self, service: Any, realizer: Realizer, ingestor: Ingestor) -> None:
        self.service = service
        self.realizer = realizer
        self.ingestor = ingestor

    def answer(self, request: Mapping[str, Any]) -> dict:
        response = self.service.answer(request)
        answers = response.get("answers")
        if not isinstance(answers, Mapping):
            return response
        for answer in answers.values():
            if not isinstance(answer, dict):
                continue
            text = None
            if not answer.get("abstain", True):
                bundle = bundle_from_answer(answer, self.ingestor)
                text = self.realizer.realize(bundle)
            answer["text"] = text
        return response

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"RealizedService({self.service!r}, realizer={self.realizer!r})"