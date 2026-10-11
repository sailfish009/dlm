"""Module 25: the question-answering session -- one pipeline at the NL boundary.

This is the structural fix the old ``nl_talk.py`` needed.  Instead of *two*
different behaviours for a natural-language line (``chat.py`` echoes a reading;
``nl_talk.py`` re-implements assert/ask), there is now one seam-B-to-seam-E
pipeline:

    sentence
      |  looks like a question?  (``?`` / wh-word / do-support)
      |------ yes --> QuestionReader.read --> Query --resolve(closure)--> Answer
      |                                                          | render+round-trip
      |------ no  --> Ingestor.literal --> Literal --> assert into KB
      |  neither  --> chatter script (Eliza-style, assertion-free)
      v
    natural-language reply

Trust is unchanged: the KB is grown only from a *uniquely* read declarative; a
question is answered only from kernel closure / the negative side table; every
rendered claim is round-trip checked; chatter never asserts.
"""
from __future__ import annotations

from random import Random
from typing import Optional

from .answer import render_answer, resolve
from .chat import ChatScript, DEFAULT_SCRIPT
from .convert import Ingestor
from .engine import entails
from .judge import ProofJudge
from .kb import KnowledgeBase
from .logic import Literal
from .query import Query
from .question import QuestionReader, looks_like_question
from .reader import tokenize
from .realize import Bundle, CheckedRealizer, TemplateRealizer
from .sexp import Sym


class QASession:
    """A natural-language in / natural-language out question-answering session."""

    def __init__(
        self,
        ingestor: Ingestor,
        *,
        registry=None,
        kb: Optional[KnowledgeBase] = None,
        question_reader: Optional[QuestionReader] = None,
        script: Optional[ChatScript] = None,
        judge: Optional[ProofJudge] = None,
        rng: Optional[Random] = None,
        surface=None,
    ) -> None:
        self.ingestor = ingestor
        self.registry = registry if registry is not None else ingestor.registry
        self.kb = kb if kb is not None else KnowledgeBase()
        self.template = TemplateRealizer(self.registry, surface=surface)
        self.realizer = CheckedRealizer(self.template, self.ingestor)
        self.question_reader = (
            question_reader
            if question_reader is not None
            else QuestionReader(registry=self.registry)
        )
        self.script = script if script is not None else DEFAULT_SCRIPT
        self.judge = judge if judge is not None else ProofJudge()
        self.rng = rng if rng is not None else Random()

    # -- public ------------------------------------------------------------
    def turn(self, sentence: str) -> str:
        if looks_like_question(sentence):
            queries = self.question_reader.read(sentence)
            if queries:
                return self._answer(queries[0])
        else:
            literal = self.ingestor.literal(sentence)
            if literal is not None:
                return self._assert(literal)
        chatter = self.script.respond(tuple(Sym(t) for t in tokenize(sentence)), self.rng)
        if chatter:
            return chatter
        return "Sorry, I could not understand that sentence."

    # -- logic channel -----------------------------------------------------
    def _say(self, literal: Literal, *, asserted: bool) -> Optional[str]:
        """Render one ground literal through the checked egress (or plain)."""
        if asserted:
            bundle = Bundle(verdict="asserted", abstain=False, literal=literal)
            return self.realizer.realize(bundle)
        text = self.template.render(literal)
        if text is None:
            return None
        return text if self.ingestor.literal(text) == literal else None

    def _assert(self, literal: Literal) -> str:
        if literal.negated:
            if entails(self.kb, literal.atom):
                text = self._say(Literal(literal.atom, negated=False), asserted=True)
                return f"That contradicts something I know: {text}."
            if self.kb.is_negated(literal.atom):
                return "I already knew that."
            self.kb.add_negation(literal.atom)
        else:
            if self.kb.is_negated(literal.atom):
                text = self._say(Literal(literal.atom, negated=True), asserted=True)
                return f"That contradicts something I know: {text}."
            if self.kb.has_fact(literal.atom):
                return "I already knew that."
            self.kb.add_fact(literal.atom)
        text = self._say(literal, asserted=True)
        return f"OK, I learned: {text}."

    def _round_trips(self, literals) -> bool:
        for literal in literals:
            if literal is None or not literal.is_ground():
                continue
            rendered = self.template.render(literal)
            if rendered is None or self.ingestor.literal(rendered) != literal:
                return False
        return True

    def _answer(self, query: Query) -> str:
        answer = resolve(query, self.kb, judge=self.judge)
        claims = [answer.literal] if answer.literal is not None else list(answer.facts)
        if answer.decided and not self._round_trips(claims):
            return "I cannot verify how to say that."
        text = render_answer(answer, self.template)
        if text is None:
            return "I cannot decide that."
        return text

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"QASession(kb_facts={len(self.kb.facts())})"


def default_qa_session(predicates, prepositions, schemas, *, lexicon=None) -> QASession:
    """Build a session whose declarative and interrogative readers share a lexicon.

    ``predicates`` must be **base** forms (``call``, ``like``, ``happy``) so that
    ``alice calls bob`` and ``does alice call bob?`` denote the same atom.
    """
    from .grammar import GrammarReader
    from .lexicon import PredicateLexicon, third_person
    from .logic import SchemaRegistry

    lex = lexicon if lexicon is not None else PredicateLexicon(predicates)
    registry = SchemaRegistry(schemas)
    reader = GrammarReader(prepositions=prepositions, lexicon=lex)
    ingestor = Ingestor(reader, registry)
    qreader = QuestionReader(
        predicates=predicates, registry=registry, prepositions=prepositions, lexicon=lex
    )
    return QASession(
        ingestor, registry=registry, question_reader=qreader, surface=third_person
    )