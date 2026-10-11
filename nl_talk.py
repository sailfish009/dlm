#!/usr/bin/env python3
"""Natural-language in / natural-language out conversation (no S-expr visible).

This is the v0.0009 boundary: one pipeline, not two.  A line is classified at
ingress (question marker vs declarative), routed through the shared readers, and
answered from the kernel closure -- with chatter as an explicit, assertion-free
fallback.  See ``dlm/qa.py``.

Usage:
    python nl_talk.py                 # interactive
    python nl_talk.py transcript.txt  # replay a file of sentences ("?" = question)
"""
from __future__ import annotations

import sys

from dlm.lexicon import third_person
from dlm.logic import Schema, SchemaRegistry
from dlm.qa import QASession
from dlm.question import QuestionReader
from dlm.grammar import GrammarReader
from dlm.convert import Ingestor
from dlm.lexicon import PredicateLexicon
from dlm.reader import AGENT, FIGURE, GROUND, PATIENT, SUBJECT

# A small, natural closed-subset domain.  Predicates are **base forms** so that a
# declarative ("alice calls bob") and its question ("does alice call bob?") denote
# the same atom -- this is what the lemma layer (dlm/lexicon.py) guarantees.
VERBS = ("call", "like", "know", "see", "help")
ADJECTIVES = ("happy", "tall", "tired")
PREPOSITIONS = ("on", "in", "at", "under", "near", "with")

SCHEMAS = (
    *[Schema(v, (AGENT, PATIENT)) for v in VERBS],
    *[Schema(a, (SUBJECT,)) for a in ADJECTIVES],
    *[Schema(p, (FIGURE, GROUND)) for p in PREPOSITIONS],
)


def make_session() -> QASession:
    predicates = VERBS + ADJECTIVES
    lexicon = PredicateLexicon(predicates)
    registry = SchemaRegistry(SCHEMAS)
    ingestor = Ingestor(
        GrammarReader(prepositions=PREPOSITIONS, lexicon=lexicon), registry
    )
    qreader = QuestionReader(
        predicates=predicates,
        registry=registry,
        prepositions=PREPOSITIONS,
        lexicon=lexicon,
    )
    return QASession(ingestor, registry=registry, question_reader=qreader, surface=third_person)


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    session = make_session()
    if argv:
        with open(argv[0], "r", encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                print(f"> {line}")
                print(session.turn(line))
    else:
        print("natural-language chat (type a sentence; add ? to ask). :quit to leave")
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if line.strip() in (":quit", ":q", ":exit"):
                break
            if not line.strip():
                continue
            print(session.turn(line))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())