"""Judgment protocol -- seam D (module 8).

A *decision* combines two kinds of signal that must never be confused:

* the **trusted** verdict: a re-checkable proof (seam C) that a ground literal is
  entailed, or an explicit negative in the KB side table.  Only this may *assert*.
* the **untrusted** score: a number a ``Proposer`` (a learned reader, a retriever,
  strands logits, a CLM cosine) attaches to a candidate literal.  It may only
  *choose what to try* or *annotate confidence* -- never change the verdict.

The invariant is structural: ``Adjudicator`` never reads a proposer's verdict,
only its ``Literal`` and ``score``.  So a proposer that ranks a falsehood at
score 1.0 cannot make the system assert it; the proof gate just abstains.

Nothing here sees text: judges and proposers exchange ``Literal`` objects only
(the ingress firewall of ``convert.py`` already ran).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Dict, Iterable, Optional, Protocol, Tuple, runtime_checkable

from .engine import prove
from .kb import KnowledgeBase
from .kernel import Proof, verify
from .logic import Atom, Literal

__all__ = [
    "Verdict",
    "Judgement",
    "Proposal",
    "Judge",
    "Proposer",
    "ProofJudge",
    "StaticProposer",
    "KbProposer",
    "Policy",
    "Adjudicator",
]


class Verdict(str, Enum):
    """The trusted outcome for a literal.  Only proof/kernel produce these."""

    ASSERTED = "asserted"  # entailed (has a verified proof)
    REFUTED = "refuted"    # an explicit negative fact is on record
    ABSTAIN = "abstain"    # no trusted basis -- say nothing


@dataclass(frozen=True)
class Judgement:
    """A verdict on one ground literal, plus (display-only) learned annotation."""

    literal: Literal
    verdict: Verdict = Verdict.ABSTAIN
    proof: Optional[Proof] = None
    score: Optional[float] = None          # raw untrusted proposer score
    confidence: Optional[float] = None     # display only; never decides
    source: str = "proof"
    proposed_by: Optional[str] = None

    @property
    def asserted(self) -> bool:
        return self.verdict is Verdict.ASSERTED

    @property
    def refuted(self) -> bool:
        return self.verdict is Verdict.REFUTED

    @property
    def decided(self) -> bool:
        return self.verdict is not Verdict.ABSTAIN


@dataclass(frozen=True)
class Proposal:
    """An untrusted candidate: a literal to try and a score to rank it by."""

    literal: Literal
    score: float = 0.0
    source: str = "proposer"


@runtime_checkable
class Judge(Protocol):
    """Trusted decision maker.  Implementations must assert only via seam C."""

    def judge(self, kb: KnowledgeBase, literal: Literal) -> Judgement:
        ...


@runtime_checkable
class Proposer(Protocol):
    """Untrusted candidate generator (seam B/B').  Never asserts."""

    def propose(
        self, kb: KnowledgeBase, query: Optional[Literal] = None
    ) -> Tuple[Proposal, ...]:
        ...


class ProofJudge:
    """DLM's trusted judge: asserts iff the closure has a re-checkable proof.

    ``prove`` supplies a candidate certificate; ``verify`` (the kernel) is the
    component that actually blesses it, so the assertion path is
    ``prove -> verify -> ASSERTED``.  A ground negative is refuted only by the
    explicit side table (Horn cannot derive a negative).  Everything else
    abstains -- including non-ground literals ("abstain, never guess").
    """

    def judge(self, kb: KnowledgeBase, literal: Literal) -> Judgement:
        if not literal.is_ground():
            return Judgement(literal, Verdict.ABSTAIN, source="proof")
        if literal.negated:
            if kb.is_negated(literal.atom):
                return Judgement(literal, Verdict.REFUTED, confidence=1.0, source="proof")
            return Judgement(literal, Verdict.ABSTAIN, source="proof")
        proof = prove(kb, literal.atom)
        if proof is not None and verify(proof, kb):
            return Judgement(
                literal, Verdict.ASSERTED, proof=proof, confidence=1.0, source="proof"
            )
        return Judgement(literal, Verdict.ABSTAIN, source="proof")


class StaticProposer:
    """A fixed tuple of proposals -- the test/fixture arm of seam B/B'."""

    def __init__(self, proposals: Iterable[Proposal]) -> None:
        self._proposals = tuple(proposals)

    def propose(
        self, kb: KnowledgeBase, query: Optional[Literal] = None
    ) -> Tuple[Proposal, ...]:
        return self._proposals


class KbProposer:
    """Trivial retrieval baseline: propose the KB's ground facts as candidates.

    Deterministic (sorted by surface form) so experiments are reproducible; the
    score is uniform unless the caller supplies one.  This is the "B' retrieval"
    arm in its most naive form: it decides *what to try*, not what is true.
    """

    def __init__(
        self,
        *,
        negated: bool = False,
        score: float = 1.0,
        limit: Optional[int] = None,
        source: str = "kb",
    ) -> None:
        self._negated = negated
        self._score = score
        self._limit = limit
        self._source = source

    def propose(
        self, kb: KnowledgeBase, query: Optional[Literal] = None
    ) -> Tuple[Proposal, ...]:
        atoms: Tuple[Atom, ...] = tuple(sorted(kb.facts(), key=str))
        if self._limit is not None:
            atoms = atoms[: self._limit]
        return tuple(
            Proposal(Literal(a, self._negated), self._score, self._source) for a in atoms
        )


class Policy(str, Enum):
    """How learned signal is allowed to surface (NOTE.md Part I Sec.4)."""

    GATE = "gate"          # P1: proof decides; on abstain, drop learned signal
    TWO_AXIS = "two_axis"  # P3: same verdict; keep learned score as confidence


def _index_proposals(proposals: Iterable[Proposal]) -> Dict[Literal, Proposal]:
    best: Dict[Literal, Proposal] = {}
    for p in proposals:
        cur = best.get(p.literal)
        if cur is None or p.score > cur.score:
            best[p.literal] = p
    return best


@dataclass
class Adjudicator:
    """Fuse a trusted ``Judge`` with untrusted ``Proposer`` signal.

    The verdict always comes from ``judge`` (proof gate).  Proposals only supply
    a score and, when no query is given, an ordering of literals to try.
    """

    judge: Judge = field(default_factory=ProofJudge)
    policy: Policy = Policy.GATE

    def _annotate(self, judgement: Judgement, proposal: Proposal) -> Judgement:
        if judgement.decided:
            confidence = judgement.confidence if judgement.confidence is not None else 1.0
        elif self.policy is Policy.TWO_AXIS:
            confidence = proposal.score  # display only -- the verdict is still abstain
        else:  # GATE: no proof => drop the learned signal
            confidence = None
        return replace(
            judgement,
            score=proposal.score,
            confidence=confidence,
            proposed_by=proposal.source,
        )

    def judge_candidates(
        self,
        kb: KnowledgeBase,
        literals: Iterable[Literal],
        *,
        proposals: Iterable[Proposal] = (),
    ) -> Tuple[Judgement, ...]:
        """Trusted verdict for each literal, annotated by matching proposals."""
        indexed = _index_proposals(proposals)
        out = []
        for literal in literals:
            judgement = self.judge.judge(kb, literal)
            proposal = indexed.get(literal)
            if proposal is not None:
                judgement = self._annotate(judgement, proposal)
            out.append(judgement)
        return tuple(out)

    def decide(
        self,
        kb: KnowledgeBase,
        *,
        query: Optional[Literal] = None,
        proposals: Iterable[Proposal] = (),
    ) -> Judgement:
        """Decide one literal.

        With ``query``, judge exactly that literal.  Without one, the proposer
        ranks candidates and the first *decided* (proof-backed) one wins; if none
        is decided, the top-ranked candidate is returned as ``ABSTAIN``.
        """
        proposals = tuple(proposals)
        if query is not None:
            return self.judge_candidates(kb, (query,), proposals=proposals)[0]
        if not proposals:
            raise ValueError("decide() needs a query or at least one proposal")
        ranked = tuple(sorted(proposals, key=lambda p: (-p.score, str(p.literal))))
        judged = self.judge_candidates(
            kb, (p.literal for p in ranked), proposals=ranked
        )
        for judgement in judged:
            if judgement.decided:
                return judgement
        return judged[0]