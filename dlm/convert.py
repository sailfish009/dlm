"""Module 7: the input ingress -- text becomes logic immediately (seam B gate).

Standing decision (NOTE.md §27): natural language exists only at the input
boundary. User input and external data both arrive as text, so every textual
input is converted to logic at ingress and **no sentence is retained inside the
model**. After this module the only strings are *symbols* -- predicate, role and
constant names -- never phrases.

Two ingress paths::

    # (a) natural language -- reader proposes, normalize disposes
    sentence --> reader.read (untrusted) --> Frame(s)
             --> SchemaRegistry.normalize (trust boundary) --> Literal(s) | abstain

    # (b) already-symbolic input (e.g. the wire's S-expr) -- the reader is skipped
    form --> function-free check --> Atom | Literal | Rule

Multiple readings are preserved as a tuple. :meth:`Ingestor.literal` is the
strict single-reading gate: it abstains on zero *or* more than one reading.
Nothing textual survives an :class:`Ingestor` call: it returns logic only.

This module is stdlib-only and never evaluates text.
"""
from __future__ import annotations

from typing import List, Optional, Tuple, Union

from .logic import Atom, Literal, Rule, SchemaRegistry
from .kb import StateGrounder
from .reader import Reader
from .sexp import Form, SexpError, Sym, form_to_atom, form_to_literal, form_to_rule, parse

__all__ = [
    "Logic",
    "sentence_to_literals",
    "sentence_to_literal",
    "state_to_facts",
    "form_to_logic",
    "Ingestor",
]

#: Anything the ingress may emit. Only these leave the text boundary.
Logic = Union[Atom, Literal, Rule]


# -- path (a): text -> Literal ---------------------------------------------
def sentence_to_literals(
    reader: Reader, registry: SchemaRegistry, sentence: str
) -> Tuple[Literal, ...]:
    """All normalized readings of ``sentence`` (empty tuple = abstain).

    The reader is untrusted and proposes frames; ``normalize`` is the trust
    boundary and rejects unknown predicates / role mismatches. Ambiguity is
    preserved, not collapsed.
    """
    out: List[Literal] = []
    for frame in reader.read(sentence):
        lit = registry.normalize(frame)
        if lit is not None and lit not in out:
            out.append(lit)
    return tuple(out)


def sentence_to_literal(
    reader: Reader, registry: SchemaRegistry, sentence: str
) -> Optional[Literal]:
    """The *unique* reading of ``sentence``, or ``None`` (abstain).

    Abstains when there are zero readings (unreadable) or more than one
    (ambiguous): picking one would be guessing.
    """
    readings = sentence_to_literals(reader, registry, sentence)
    if len(readings) == 1:
        return readings[0]
    return None


# -- path (state): structured state -> facts -------------------------------
def state_to_facts(
    grounder: StateGrounder, registry: SchemaRegistry, state: object
) -> Tuple[Atom, ...]:
    """Ground a structured state into positive ground atoms (empty = abstain).

    The grounder is untrusted and proposes frames; ``normalize`` is the trust
    boundary. Negated proposals are dropped here (facts are positive); explicit
    negatives belong in the KB side table.
    """
    out: List[Atom] = []
    for frame in grounder.ground(state):
        lit = registry.normalize(frame)
        if lit is None or lit.negated:
            continue
        atom = lit.atom
        if atom.is_ground() and atom not in out:
            out.append(atom)
    return tuple(out)


# -- path (b): symbolic form -> logic --------------------------------------
def form_to_logic(form: Form) -> Logic:
    """Read one already-symbolic form as an ``Atom``, ``Literal`` or ``Rule``.

    The function-free check happens at construction (``Atom``/``Rule``); a
    nested/function argument raises instead of being silently accepted.
    """
    if isinstance(form, tuple) and form and form[0] == Sym("rule"):
        return form_to_rule(form)
    if isinstance(form, tuple) and len(form) == 2 and form[0] == Sym("not"):
        return form_to_literal(form)
    return form_to_atom(form)


class Ingestor:
    """The input firewall: bundles a reader + schema registry.

    It is the single entry point for getting data into the model. Text is
    converted here and now; nothing textual is returned.
    """

    def __init__(
        self,
        reader: Reader,
        registry: SchemaRegistry,
        grounder: Optional[StateGrounder] = None,
    ) -> None:
        self.reader = reader
        self.registry = registry
        self.grounder = grounder

    # -- natural language --------------------------------------------------
    def literals(self, sentence: str) -> Tuple[Literal, ...]:
        """All readings of a sentence (empty = abstain)."""
        return sentence_to_literals(self.reader, self.registry, sentence)

    def literal(self, sentence: str) -> Optional[Literal]:
        """The unique reading of a sentence, or ``None`` to abstain."""
        return sentence_to_literal(self.reader, self.registry, sentence)

    # -- structured state (seam A) ----------------------------------------
    def facts(self, state: object) -> Tuple[Atom, ...]:
        """Ground a structured state into facts; ``()`` = abstain.

        Returns ``()`` when no grounder was configured.
        """
        if self.grounder is None:
            return ()
        return state_to_facts(self.grounder, self.registry, state)

    # -- symbolic input ----------------------------------------------------
    def form(self, form: Form) -> Logic:
        """Convert an already-parsed form to logic."""
        return form_to_logic(form)

    def logic(self, text: str) -> Optional[Logic]:
        """Parse S-expr ``text`` and convert it to logic; ``None`` = abstain.

        Abstains when the text is not exactly one form. Malformed S-expr raises
        :class:`SexpError` (a distinct failure from a well-formed but
        unnormalizable sentence).
        """
        forms = parse(text)
        if len(forms) != 1:
            return None
        return form_to_logic(forms[0])

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"Ingestor(reader={self.reader!r}, registry={self.registry!r})"