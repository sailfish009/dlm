"""DLM dialogue loop: utterance -> ground -> KB/prove -> deterministic reply.

This is the missing *loop*, not a new capability. v0.0003 already had the parts;
`dialogue.py` assembles them behind one object:

    utterance -- Grounder --> Grounding(kind=query|assert)
        assert -> contradiction check -> kb.add_fact (user-tagged provenance)
        query  -> DecisionEngine.noul(atom) -> proof -> template verbalizer
        ungrounded -> abstain

There is NO text generation anywhere in this file. A reply is one of a fixed
set of templates, and the only variable part is a *rendering of a proof tree*
(`Proof.render()`), i.e. a certificate, not fluency.

Honest scope: a grounded dialogue is only as good as its grounder. On held-out
phrasing the adopted default T2 is the lexical baseline, which is imperfect
(NEGATIVE_LEDGER NL-6). A wrong atom is then affirmed with a *correct proof of
the wrong thing*. The loop never invents an atom and never guesses: if the
front-end abstains, the dialogue abstains.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List, Optional

from .decision import DecisionEngine
from .deduce import Engine, Proof
from .grounding import Grounding, Grounder
from .interpreter import parse_atom
from .kb import KnowledgeBase
from .schema import NoulQuestion
from .terms import Atom

__all__ = ["Reply", "Verbalizer", "DialogueSession"]

# reply kinds
ANSWER = "answer"    # a yes/no verdict (with optional proof)
ASSERT = "assert"    # the KB was told something
ABSTAIN = "abstain"  # the front-end could not ground the utterance
REJECT = "reject"    # grounded, but the assertion contradicts the KB


def _canon(atom: Atom) -> str:
    """Canonical key via parse_atom so 'p(a, b)' and 'p(a,b)' coincide."""
    return str(parse_atom(str(atom)))


@dataclass
class Reply:
    """One turn's result. ``bool(reply)`` is False for abstain/reject."""

    kind: str
    text: str
    utterance: str = ""
    grounding: Optional[Grounding] = None
    derivable: Optional[bool] = None
    proof: Optional[Proof] = None
    added: bool = False            # an assertion actually grew the KB
    reason: str = ""
    provenance: str = "process"    # "seed" facts vs facts the user asserted

    def __bool__(self) -> bool:
        return self.kind not in (ABSTAIN, REJECT)

    def lines(self) -> List[str]:
        return self.text.splitlines()


class Verbalizer:
    """Deterministic templates. The only dynamic part is the proof rendering.

    Subclass and override any method to change wording; the loop never needs
    new wording to work.
    """

    def render_proof(self, proof: Proof) -> str:
        return " ; ".join(ln.strip() for ln in proof.render().splitlines())

    def answer(self, *, derivable: bool, proof: Optional[Proof], grounding: Grounding) -> str:
        if not derivable:
            return "no"
        if proof is not None:
            return f"yes — {self.render_proof(proof)}"
        return "yes"

    def noted(self, atom: Atom, n_facts: int, added: bool) -> str:
        if added:
            return f"noted {atom} (KB now {n_facts} facts)"
        return f"already known: {atom}"

    def consistent(self, atom: Atom) -> str:
        return f"consistent: {atom} is not derivable"

    def contradiction(self, atom: Atom) -> str:
        return f"contradiction: {atom} is already derivable"

    def abstain(self, reason: str) -> str:
        return f"I don't understand that sentence ({reason or 'no grounding'})."


@dataclass
class DialogueSession:
    """A grounded, proof-based conversation over one knowledge base.

    Learning inside a session is symbolic: new facts (KB growth). Rule
    induction (`dlm.generalize.induce_rules`) and the NL grounder are supplied
    from outside, so this class stays a thin, auditable loop.
    """

    kb: KnowledgeBase
    grounder: Grounder
    temperature: float = 0.25
    max_depth: int = 32
    verbalizer: Verbalizer = field(default_factory=Verbalizer)

    def __post_init__(self) -> None:
        self.engine = DecisionEngine(self.kb, temperature=self.temperature,
                                     max_depth=self.max_depth)
        self.prover = Engine(self.kb, max_depth=self.max_depth)
        self.user_facts: set[str] = set()
        self.history: List[Reply] = []

    # -- public API --------------------------------------------------------
    def say(self, utterance: str) -> Reply:
        """Ground an utterance and answer, assert, abstain, or reject.

        `say` trusts the grounder's `kind`. Use `ask`/`tell` when the caller
        already knows the intent, or when the same surface form is ambiguous
        (e.g. "alice is a parent of bob" as a query vs. an assertion).
        """
        return self._dispatch(utterance, force=None)

    def ask(self, utterance: str) -> Reply:
        """Force the utterance to be treated as a query."""
        return self._dispatch(utterance, force="query")

    def tell(self, utterance: str) -> Reply:
        """Force the utterance to be treated as an assertion."""
        return self._dispatch(utterance, force="assert")

    def _dispatch(self, utterance: str, force: Optional[str]) -> Reply:
        g = self.grounder.ground(utterance)
        if g.ok and force is not None and g.kind != force:
            g = replace(g, kind=force)
        if not g.ok:
            reply = self._abstain(utterance, g.reason or "no grounding", g)
        elif g.atom is None or not g.atom.is_ground():
            reply = self._abstain(utterance, "grounding produced a non-ground atom", g)
        elif g.kind == "assert":
            reply = self._tell(utterance, g)
        else:
            reply = self._ask(utterance, g)
        self.history.append(reply)
        return reply

    def transcript(self) -> str:
        out = []
        for r in self.history:
            out.append(f"user> {r.utterance}")
            out.append(f"  DLM: {r.text}")
        return "\n".join(out)

    # -- internals ---------------------------------------------------------
    def _abstain(self, utterance: str, reason: str, g: Grounding) -> Reply:
        return Reply(ABSTAIN, self.verbalizer.abstain(reason), utterance, g, reason=reason)

    def _ask(self, utterance: str, g: Grounding) -> Reply:
        statement = f"not {g.atom}" if g.negated else str(g.atom)
        ans = self.engine.noul(NoulQuestion(instructions=statement))
        if ans.abstained:
            return self._abstain(utterance, ans.reason or "uninterpretable", g)
        derivable = ans.noul > 0.5
        proof: Optional[Proof] = None
        provenance = "process"
        if derivable and not g.negated:
            sols = list(self.prover.prove(g.atom))
            if sols:
                best = min(sols, key=lambda s: s.proof.depth())
                proof = best.proof
                provenance = self._provenance(g.atom, proof)
        return Reply(ANSWER, self.verbalizer.answer(derivable=derivable, proof=proof, grounding=g),
                     utterance, g, derivable=derivable, proof=proof, provenance=provenance)

    def _tell(self, utterance: str, g: Grounding) -> Reply:
        if g.negated:
            # Closed-world: a negative assertion is consistent iff the positive
            # is not derivable. No explicit negative facts are stored.
            if self.prover.entails(g.atom):
                return Reply(REJECT, self.verbalizer.contradiction(g.atom), utterance, g,
                             reason="contradiction")
            return Reply(ASSERT, self.verbalizer.consistent(g.atom), utterance, g, added=False)
        already = self.prover.entails(g.atom)
        added = False
        if not already:
            added = bool(self.kb.add_fact(g.atom))
            if added:
                self.user_facts.add(_canon(g.atom))
        return Reply(ASSERT, self.verbalizer.noted(g.atom, self.kb.num_facts, added),
                     utterance, g, added=added, provenance="user" if added else "process")

    def _provenance(self, atom: Atom, proof: Optional[Proof] = None) -> str:
        """Label a proven atom 'user' if it *or any proof leaf* was user-asserted.

        'process' means the conclusion rests only on facts/rules that came with
        the KB; 'user' means the proof depends on something the user told us.
        """
        if _canon(atom) in self.user_facts:
            return "user"
        if proof is None:
            return "process"
        stack = [proof]
        while stack:
            p = stack.pop()
            if p.children:
                stack.extend(p.children)
            elif _canon(p.atom) in self.user_facts:
                return "user"
        return "process"