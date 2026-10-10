"""S-expression chatbot (module 12, NOTE.md §35): the human-facing surface.

The chatbot has **two channels that are never mixed**:

* the **logic channel** (trusted) -- S-expression commands ``(assert ...)``,
  ``(ask ...)``, ``(why ...)``, ``(retract ...)``, ``(rule ...)``, ``(facts)``,
  ``(rules)`` and ``(read "...")``. Facts are learned and answers are derived
  only by the kernel; when the kernel cannot decide, the reply carries
  ``abstain``. Nothing here invents a proposition.
* the **chatter channel** (untrusted, assertion-free) -- an Eliza-style
  ``pattern -> response`` engine (Weizenbaum 1966 / Norvig). It reflects the
  human's own words without asserting anything about the world, so it does not
  violate "abstain, never guess".

Natural language exists only at the boundary: an input line is tokenized and,
if the :class:`~dlm.convert.Ingestor` can read it, echoed back as a literal
(``(read <literal>)``); otherwise the chatter engine responds; otherwise the
bot abstains. Everything the bot *says* is a valid S-expression (``sexp.dump``).

The pattern language is deliberately tiny (stdlib only): ``?x`` binds exactly
one element, ``*x`` binds zero or more, ``_`` matches one element unbound, and
nested lists match structurally. ``match`` backtracks over ``*x``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from random import Random
from typing import Dict, List, Optional, Sequence, Tuple, Union

from .convert import Ingestor
from .engine import entails, prove
from .judge import ProofJudge
from .kb import KnowledgeBase
from .reader import tokenize
from .sexp import (
    Form,
    SexpError,
    Sym,
    atom_to_form,
    dump,
    form_to_atom,
    form_to_literal,
    form_to_rule,
    literal_to_form,
    parse,
    rule_to_form,
)

__all__ = [
    "match",
    "fill",
    "swap_pronouns",
    "random_elt",
    "ChatRule",
    "ChatScript",
    "DEFAULT_RULES",
    "DEFAULT_SCRIPT",
    "ChatSession",
    "chat_once",
    "banner",
    "main",
]

Bindings = Dict[str, Form]


# ---------------------------------------------------------------------------
# S-expression pattern matching
# ---------------------------------------------------------------------------
def _bind(name: str, value: Form, bindings: Bindings) -> Optional[Bindings]:
    """Bind ``name`` to ``value``; return None on conflict. ``""`` binds nothing."""
    if name == "":
        return bindings
    if name in bindings:
        return bindings if bindings[name] == value else None
    out = dict(bindings)
    out[name] = value
    return out


def _match_seq(pattern: Sequence[Form], form: Sequence[Form], bindings: Bindings) -> Optional[Bindings]:
    if not pattern:
        return bindings if not form else None
    head = pattern[0]
    if isinstance(head, Sym) and str(head).startswith("*"):
        name = str(head)[1:]
        for k in range(len(form) + 1):
            bound = _bind(name, tuple(form[:k]), bindings)
            if bound is None:
                continue
            rest = _match_seq(pattern[1:], form[k:], bound)
            if rest is not None:
                return rest
        return None
    if not form:
        return None
    bound = _match_one(head, form[0], bindings)
    if bound is None:
        return None
    return _match_seq(pattern[1:], form[1:], bound)


def _match_one(pattern: Form, form: Form, bindings: Bindings) -> Optional[Bindings]:
    if isinstance(pattern, Sym):
        text = str(pattern)
        if text == "_":
            return bindings
        if text.startswith("?"):
            return _bind(text[1:], form, bindings)
        if text.startswith("*"):
            return _bind(text[1:], (form,), bindings)
        return bindings if form == pattern else None
    if isinstance(pattern, tuple):
        if not isinstance(form, tuple):
            return None
        return _match_seq(pattern, form, bindings)
    return bindings if form == pattern else None


def match(pattern: Form, form: Form, bindings: Optional[Bindings] = None) -> Optional[Bindings]:
    """Match ``form`` against ``pattern``; return bindings or ``None``.

    ``?x`` binds one element, ``*x`` zero or more, ``_`` one unbound. A repeated
    variable must match an equal value. Pure and deterministic; ``match(p, f)``
    returning a dict means the rule fires.
    """
    base: Bindings = dict(bindings or {})
    if isinstance(pattern, tuple):
        if not isinstance(form, tuple):
            return None
        return _match_seq(pattern, form, base)
    return _match_one(pattern, form, base)


_PLACEHOLDER = re.compile(r"\{(\w+)\}")
_PRONOUN_SWAP = {
    "i": "you", "you": "i", "me": "you", "my": "your", "mine": "yours",
    "am": "are", "myself": "yourself", "your": "my", "yours": "mine",
    "yourself": "myself", "we": "you", "us": "you", "our": "your",
    "ours": "yours", "are": "am",
}


def _as_text(value: Form) -> str:
    if isinstance(value, tuple):
        return " ".join(dump(item) for item in value)
    return dump(value)


def fill(template: str, bindings: Bindings) -> str:
    """Substitute ``{name}`` in a response template with the bound form's text.

    Only the *substituted* words are reflected (Eliza semantics): the fixed
    template keeps its own pronouns, and the human's phrase is pronoun-swapped.
    """
    def replace(m: "re.Match[str]") -> str:
        name = m.group(1)
        return swap_pronouns(_as_text(bindings[name])) if name in bindings else m.group(0)

    return _PLACEHOLDER.sub(replace, template)


def swap_pronouns(text: str) -> str:
    """Eliza-style first/second-person swap applied to reflected chatter."""
    return " ".join(_PRONOUN_SWAP.get(word, word) for word in text.split())


def random_elt(items: Sequence[Form], rng: Random) -> Form:
    seq = tuple(items)
    if not seq:
        raise ValueError("random_elt on an empty sequence")
    return seq[rng.randrange(len(seq))]


# ---------------------------------------------------------------------------
# Chatter: assertion-free pattern -> response rules
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ChatRule:
    """One Eliza rule: an S-expression ``pattern`` and response templates."""

    pattern: Form
    responses: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.responses:
            raise ValueError("a chat rule needs at least one response")


class ChatScript:
    """Ordered rules; the first match fires and one response is chosen at random."""

    def __init__(self, rules: Sequence[ChatRule] = ()) -> None:
        self.rules: Tuple[ChatRule, ...] = tuple(rules)

    def respond(self, form: Form, rng: Optional[Random] = None) -> Optional[str]:
        rng = rng if rng is not None else Random()
        for rule in self.rules:
            bindings = match(rule.pattern, form)
            if bindings is not None:
                return fill(random_elt(rule.responses, rng), bindings)
        return None

    def __len__(self) -> int:
        return len(self.rules)


DEFAULT_RULES: Tuple[ChatRule, ...] = (
    ChatRule((Sym("hello"),), ("hello. state a fact as (assert ...) or ask as (ask ...).",)),
    ChatRule((Sym("hi"),), ("hi. try (assert (parent alice bob)) then (ask (parent alice bob)).",)),
    ChatRule((Sym("i"), Sym("feel"), Sym("*x")),
             ("why do you feel {x}?", "how long have you felt {x}?")),
    ChatRule((Sym("i"), Sym("am"), Sym("*x")),
             ("why are you {x}?", "how long have you been {x}?")),
    ChatRule((Sym("you"), Sym("are"), Sym("*x")),
             ("why do you think i am {x}?", "does it please you to think i am {x}?")),
    ChatRule((Sym("i"), Sym("want"), Sym("*x")),
             ("what would it mean to you if you got {x}?",)),
    ChatRule((Sym("my"), Sym("*x")), ("tell me more about your {x}.",)),
    ChatRule((Sym("i"), Sym("*x")), ("why do you {x}?", "tell me more.")),
)
DEFAULT_SCRIPT = ChatScript(DEFAULT_RULES)


# ---------------------------------------------------------------------------
# The session: command dispatcher + chatter fallback
# ---------------------------------------------------------------------------
def _abstain(reason: str) -> tuple:
    return (Sym("abstain"), reason)


class ChatSession:
    """A grounded S-expression chatbot over one :class:`KnowledgeBase`.

    The human's S-expression commands grow/query the KB; a natural-language line
    is first offered to the ingressor and, failing that, to the chatter script.
    Only the kernel ever asserts a proposition.
    """

    def __init__(
        self,
        ingestor: Ingestor,
        kb: Optional[KnowledgeBase] = None,
        *,
        script: Optional[ChatScript] = None,
        judge: Optional[ProofJudge] = None,
        rng: Optional[Random] = None,
    ) -> None:
        self.ingestor = ingestor
        self.kb = kb if kb is not None else KnowledgeBase()
        self.script = script if script is not None else DEFAULT_SCRIPT
        self.judge = judge if judge is not None else ProofJudge()
        self.rng = rng if rng is not None else Random()

    # -- public ------------------------------------------------------------
    def respond(self, message: Union[str, Form]) -> tuple:
        """Answer an S-expression form, or a natural-language string."""
        if isinstance(message, str):
            return self._dispatch(tuple(Sym(tok) for tok in tokenize(message)))
        return self._dispatch(message)

    def say(self, text: str) -> tuple:
        """Treat ``text`` as natural language (tokenize, then dispatch)."""
        return self._dispatch(tuple(Sym(tok) for tok in tokenize(text)))

    # -- dispatch ----------------------------------------------------------
    def _dispatch(self, form: Form) -> tuple:
        if not isinstance(form, tuple):
            form = (form,)
        handlers = {
            "assert": self._cmd_assert,
            "ask": self._cmd_ask,
            "why": self._cmd_why,
            "retract": self._cmd_retract,
            "rule": self._cmd_rule,
            "facts": self._cmd_facts,
            "rules": self._cmd_rules,
            "read": self._cmd_read,
        }
        head = form[0] if form and isinstance(form[0], Sym) else None
        handler = handlers.get(str(head)) if head is not None else None
        if handler is not None:
            return handler(form)
        return self._converse(form)

    # -- logic channel -----------------------------------------------------
    def _arg_literal(self, form: Form) -> Optional[object]:
        if not isinstance(form, tuple) or len(form) != 2:
            return None
        try:
            return form_to_literal(form[1])
        except (SexpError, TypeError, ValueError):
            return None

    def _cmd_assert(self, form: Form) -> tuple:
        lit = self._arg_literal(form)
        if lit is None:
            return _abstain("assert takes exactly one function-free literal")
        if not lit.is_ground():
            return _abstain("i only learn ground facts")
        if lit.negated:
            if entails(self.kb, lit.atom):
                return (Sym("no"), "that contradicts something i can prove", literal_to_form(lit))
            self.kb.add_negation(lit.atom)
        else:
            if self.kb.is_negated(lit.atom):
                return (Sym("no"), "that contradicts a negative i already hold", literal_to_form(lit))
            self.kb.add_fact(lit.atom)
        return (Sym("ok"), "learned", literal_to_form(lit))

    def _truth(self, lit: object):
        """Truth value of a ground literal as a proposition, or ``None`` (NOTE §30).

        True iff the literal itself is established; False iff its **opposite** is
        on record (a proof for the positive, the side table for the negative).
        """
        from .logic import Literal as _Literal
        from .judge import Verdict as _Verdict

        judgement = self.judge.judge(self.kb, lit)
        if lit.negated:
            if judgement.verdict is _Verdict.REFUTED:
                return True, judgement
            opposite = self.judge.judge(self.kb, _Literal(lit.atom, negated=False))
            if opposite.verdict is _Verdict.ASSERTED:
                return False, opposite
            return None, judgement
        if judgement.verdict is _Verdict.ASSERTED:
            return True, judgement
        opposite = self.judge.judge(self.kb, _Literal(lit.atom, negated=True))
        if opposite.verdict is _Verdict.REFUTED:
            return False, opposite
        return None, judgement

    def _cmd_ask(self, form: Form) -> tuple:
        lit = self._arg_literal(form)
        if lit is None:
            return _abstain("ask takes exactly one function-free literal")
        value, judgement = self._truth(lit)
        verdict = "abstain" if value is None else ("asserted" if value else "refuted")
        reply: List[Form] = [
            Sym("answer"),
            literal_to_form(lit),
            (Sym("verdict"), Sym(verdict)),
        ]
        if value and judgement.proof is not None:
            reply.append(_proof_form(judgement.proof))
        return tuple(reply)

    def _cmd_why(self, form: Form) -> tuple:
        lit = self._arg_literal(form)
        if lit is None or lit.negated:
            return _abstain("why takes one positive literal")
        proof = prove(self.kb, lit.atom)
        if proof is None:
            return _abstain("i have no proof")
        return _proof_form(proof)

    def _cmd_retract(self, form: Form) -> tuple:
        if not isinstance(form, tuple) or len(form) != 2:
            return _abstain("retract takes exactly one atom")
        try:
            atom = form_to_atom(form[1])
        except (SexpError, TypeError, ValueError):
            return _abstain("retract takes exactly one atom")
        if not atom.is_ground():
            return _abstain("i only retract ground facts")
        self.kb.remove_fact(atom)
        self.kb.remove_negation(atom)
        return (Sym("ok"), "retracted", atom_to_form(atom))

    def _cmd_rule(self, form: Form) -> tuple:
        try:
            rule = form_to_rule(form)
        except (SexpError, TypeError, ValueError):
            return _abstain("rule form is malformed")
        self.kb.add_rule(rule)
        return (Sym("ok"), "learned rule", rule_to_form(rule))

    def _cmd_facts(self, form: Form) -> tuple:
        facts = tuple(atom_to_form(f) for f in self.kb.facts())
        return (Sym("facts"), *facts)

    def _cmd_rules(self, form: Form) -> tuple:
        rules = tuple(rule_to_form(r) for r in self.kb.rules())
        return (Sym("rules"), *rules)

    def _cmd_read(self, form: Form) -> tuple:
        if not isinstance(form, tuple) or len(form) != 2 or not isinstance(form[1], str):
            return _abstain('read takes one quoted sentence, e.g. (read "alice calls bob")')
        return self._converse(tuple(Sym(tok) for tok in tokenize(form[1])))

    # -- boundary + chatter ------------------------------------------------
    def _converse(self, form: Form) -> tuple:
        if isinstance(form, tuple):
            sentence = " ".join(str(item) for item in form)
        else:
            sentence = str(form)
        lit = self.ingestor.literal(sentence)
        if lit is not None:
            return (Sym("read"), literal_to_form(lit))
        text = self.script.respond(form, self.rng)
        if text is not None:
            return (Sym("reply"), text)
        return _abstain("i cannot read that")


def _proof_form(proof: object) -> Form:
    """Render a proof as an S-expression ``Form`` (its ``str`` is already one)."""
    try:
        forms = parse(str(proof))
    except SexpError:  # pragma: no cover - defensive
        return (Sym("proof"), str(proof))
    return forms[0] if forms else (Sym("proof"), str(proof))


# ---------------------------------------------------------------------------
# A tiny REPL
# ---------------------------------------------------------------------------
def banner() -> str:
    return (
        "dlm S-expression chatbot\n"
        "  (assert <literal>)  (ask <literal>)  (why <literal>)  (retract <atom>)\n"
        "  (rule <rule-form>)  (facts)  (rules)  (read \"<sentence>\")\n"
        "  :quit to leave"
    )


def chat_once(session: ChatSession, line: str) -> str:
    """One turn: parse ``line`` as an S-expression form, else read it as text."""
    text = line.strip()
    forms: Tuple[Form, ...] = ()
    if text.startswith("("):
        try:
            forms = parse(text)
        except SexpError:
            forms = ()
    if len(forms) == 1 and isinstance(forms[0], tuple):
        reply = session.respond(forms[0])
    else:
        reply = session.say(text)
    return dump(reply)


def default_ingestor() -> Ingestor:  # pragma: no cover - convenience for the REPL
    """A small hand-authored ingress for the interactive REPL (not the model)."""
    from .logic import Schema, SchemaRegistry
    from .reader import AGENT, PATIENT, SUBJECT, LexicalReader

    predicates = ("calls", "likes", "knows", "sees", "happy", "tall")
    schemas = (
        Schema("calls", (AGENT, PATIENT)),
        Schema("likes", (AGENT, PATIENT)),
        Schema("knows", (AGENT, PATIENT)),
        Schema("sees", (AGENT, PATIENT)),
        Schema("happy", (SUBJECT,)),
        Schema("tall", (SUBJECT,)),
    )
    return Ingestor(LexicalReader(predicates=predicates), SchemaRegistry(schemas))


def main() -> None:  # pragma: no cover - interactive loop
    session = ChatSession(default_ingestor())
    print(banner())
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if line.strip() in (":quit", ":q", ":exit"):
            break
        if line.strip() in (":help", ":h"):
            print(banner())
            continue
        print(chat_once(session, line))


if __name__ == "__main__":  # pragma: no cover
    main()