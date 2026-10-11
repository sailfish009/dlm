"""Module 21: predicate lemmatisation -- one symbol for every surface form.

Why this is a *structural* module, not a data cleanup: seam B and seam E must
agree on the predicate symbol.  A declarative ``alice calls bob`` and a question
``does alice call bob?`` denote the *same* atom only if the reader canonicalises
the inflected verb to one base form.  Without this, the interrogative layer can
never address what the declarative layer stored, no matter how much data is fed
in -- which is exactly the "the deductive structure is not settled yet" symptom.

The lexer is deliberately tiny and closed-subset (stdlib only):

    call/calls/called/calling  -> call
    like/likes/liked/liking    -> like
    is/are/was/were/am/be      -> be
    study/studies/studied      -> study

``PredicateLexicon.lemma`` proposes *candidate* base forms and returns the first
one that is actually in the lexicon; if none is, the token is not a predicate
(so it is an entity, or the sentence abstains).  This is a proposer in the DLM
sense: it never invents a predicate -- membership in the declared lexicon is the
gate, exactly like :class:`~dlm.logic.SchemaRegistry`.
"""
from __future__ import annotations

from typing import Iterable, List, Optional

__all__ = ["verb_lemma", "third_person", "reducible_forms", "PredicateLexicon"]

#: Closed irregular set for the fragment.  Kept explicit (data, not code).
def third_person(base: str) -> str:
    """The 3rd-person-singular surface form of a base verb (for egress only).

    Any surface form that :class:`PredicateLexicon` maps back to ``base`` is
    acceptable, because the egress firewall re-reads the rendered sentence.
    """
    if base in _THIRD_PERSON:
        return _THIRD_PERSON[base]
    if base.endswith(("s", "x", "z", "ch", "sh")):
        return base + "es"
    if len(base) > 1 and base.endswith("y") and base[-2] not in _VOWELS:
        return base[:-1] + "ies"
    return base + "s"


_IRREGULAR = {
    "is": "be", "are": "be", "was": "be", "were": "be", "am": "be",
    "been": "be", "being": "be",
    "has": "have", "had": "have", "having": "have",
    "does": "do", "did": "do", "done": "do", "doing": "do",
    "goes": "go", "went": "go", "gone": "go",
    "says": "say", "said": "say",
    "makes": "make", "made": "make",
    "sees": "see", "saw": "see", "seen": "see",
    "knows": "know", "knew": "know", "known": "know",
    "flies": "fly", "flew": "fly", "flown": "fly",
    "runs": "run", "ran": "run",
    "eats": "eat", "ate": "eat", "eaten": "eat",
    "gives": "give", "gave": "give", "given": "give",
    "takes": "take", "took": "take", "taken": "take",
    "teaches": "teach", "taught": "teach",
    "brings": "bring", "brought": "bring",
    "thinks": "think", "thought": "think",
}

_VOWELS = frozenset("aeiou")

_THIRD_PERSON = {
    "be": "is", "have": "has", "do": "does", "go": "goes", "say": "says",
    "see": "sees", "know": "knows", "fly": "flies", "run": "runs",
    "eat": "eats", "give": "gives", "take": "takes", "teach": "teaches",
    "bring": "brings", "think": "thinks",
}


def reducible_forms(word: str) -> List[str]:
    """Candidate base forms of an inflected token, cheapest first.

    These are *proposals*; :class:`PredicateLexicon` accepts only a candidate
    that is in the lexicon, so an over-generating candidate list is harmless.
    """
    out: List[str] = []
    if len(word) > 3 and word.endswith("ies"):
        out.append(word[:-3] + "y")
    if len(word) > 2 and word.endswith("es"):
        out.append(word[:-2])
    if len(word) > 1 and word.endswith("s") and not word.endswith("ss"):
        out.append(word[:-1])
    if len(word) > 3 and word.endswith("ied"):
        out.append(word[:-3] + "y")
    if len(word) > 2 and word.endswith("ed"):
        base = word[:-2]
        out.append(base)
        out.append(word[:-1])  # e-ending stem: "liked" -> "like"
        if len(base) > 2 and base[-1] == base[-2] and base[-1] not in _VOWELS:
            out.append(base[:-1])  # doubled consonant: "stopped" -> "stop"
    if len(word) > 3 and word.endswith("ing"):
        base = word[:-3]
        out.append(base)
        out.append(base + "e")  # "making" -> "make"
        if len(base) > 2 and base[-1] == base[-2] and base[-1] not in _VOWELS:
            out.append(base[:-1])
    return out


def verb_lemma(word: str) -> str:
    """The single, guessed base form of ``word`` (irregular map + first reduction).

    Prefer :meth:`PredicateLexicon.lemma`, which checks the lexicon; this is the
    raw proposal used when no lexicon is available.
    """
    if word in _IRREGULAR:
        return _IRREGULAR[word]
    forms = reducible_forms(word)
    return forms[0] if forms else word


class PredicateLexicon:
    """Canonical predicate symbols and the surface forms that denote them.

    ``predicates`` are **base** forms (``call``, ``like``, ``happy``).  ``lemma``
    maps an inflected token to the base form iff that base form is declared;
    otherwise it returns ``None`` (not a predicate).
    """

    def __init__(self, predicates: Iterable[str] = ()) -> None:
        self.base = frozenset(predicates)

    # -- public ------------------------------------------------------------
    def lemma(self, token: str) -> Optional[str]:
        """The declared base form ``token`` denotes, or ``None``."""
        if token in self.base:
            return token
        irregular = _IRREGULAR.get(token)
        if irregular is not None and irregular in self.base:
            return irregular
        for candidate in reducible_forms(token):
            if candidate in self.base:
                return candidate
        return None

    def is_pred(self, token: str) -> bool:
        return self.lemma(token) is not None

    def canonical(self, token: str) -> str:
        """``token``'s base form if it is a predicate, else ``token`` unchanged."""
        return self.lemma(token) or token

    def add(self, pred: str) -> "PredicateLexicon":
        self.base = self.base | {pred}
        return self

    def __len__(self) -> int:
        return len(self.base)

    def __contains__(self, token: object) -> bool:
        return isinstance(token, str) and self.is_pred(token)

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"PredicateLexicon({sorted(self.base)!r})"