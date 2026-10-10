"""Canonical concrete syntax -- a minimal, read-only S-expression reader/writer.

S-expr is only the SURFACE of the logic units defined in ``logic.py``. Three
rules keep the layers separate:

  1. The parser is general: it parses any S-expr, nesting included.
  2. The logic core stays function-free: an atom's arguments are only Const/Var,
     so nesting is rejected at ``Atom`` construction (syntax bottom, semantics
     rejects).
  3. NEVER ``eval``. ``data == code`` is a property we exploit (proof / rule /
     certificate share one notation); it is not a licence to execute untrusted
     input. Reading is total and side-effect free.

Canonical forms (the same notation for every logic unit)::

    (calls alice bob)                         ; atom
    (not (charges c1 c2))                     ; literal
    (rule (ancestor ?x ?y) (parent ?x ?y))    ; rule  (module 4+)
    (proof ...)                               ; proof (module 6+)

``parse`` returns a tuple of top-level FORMS; ``dump`` writes one form;
``dump_all`` writes a sequence. A form is a ``Sym``, a ``str`` literal, or a
tuple of forms.
"""
from __future__ import annotations

from typing import Any, Iterator, List, Tuple, Union

from .logic import Atom, Const, Literal, Rule, Var

__all__ = [
    "Sym",
    "Form",
    "SexpError",
    "parse",
    "dump",
    "dump_all",
    "atom_to_form",
    "form_to_atom",
    "literal_to_form",
    "form_to_literal",
    "rule_to_form",
    "form_to_rule",
]


class SexpError(ValueError):
    """Raised on malformed input. Reading is strict; malformed means abstain."""


class Sym(str):
    """A symbol (identifier), distinct from a quoted string literal."""

    __slots__ = ()

    def __repr__(self) -> str:  # keep Sym visible in test failures
        return f"Sym({str.__repr__(self)})"


Form = Union[Sym, str, tuple]


# -- reader ----------------------------------------------------------------
def _tokenize(text: str) -> Iterator[Any]:
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c == ";":  # Lisp comment: to end of line
            while i < n and text[i] != "\n":
                i += 1
        elif c in "()":
            yield c
            i += 1
        elif c == '"':
            i += 1
            buf: List[str] = []
            while i < n and text[i] != '"':
                if text[i] == "\\" and i + 1 < n:
                    i += 1
                    buf.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(text[i], text[i]))
                else:
                    buf.append(text[i])
                i += 1
            if i >= n:
                raise SexpError("unterminated string literal")
            i += 1
            yield ("str", "".join(buf))
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()";':
                j += 1
            yield ("sym", text[i:j])
            i = j


def parse(text: str) -> Tuple[Form, ...]:
    """Parse ``text`` into a tuple of top-level forms. Never evaluates."""
    tokens = list(_tokenize(text))
    pos = 0

    def read() -> Form:
        nonlocal pos
        if pos >= len(tokens):
            raise SexpError("unexpected end of input")
        tok = tokens[pos]
        pos += 1
        if tok == ")":
            raise SexpError("unexpected ')'")
        if tok == "(":
            items: List[Form] = []
            while True:
                if pos >= len(tokens):
                    raise SexpError("missing ')'")
                if tokens[pos] == ")":
                    pos += 1
                    return tuple(items)
                items.append(read())
        # a token tuple: ("sym", name) or ("str", value)
        kind, value = tok
        return value if kind == "str" else Sym(value)

    forms: List[Form] = []
    while pos < len(tokens):
        forms.append(read())
    return tuple(forms)


# -- writer ----------------------------------------------------------------
def dump(form: Form) -> str:
    """Write one form. Symbols are bare; string literals are quoted."""
    if isinstance(form, Sym):
        return str(form)
    if isinstance(form, str):
        return '"' + form.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(form, (tuple, list)):
        return "(" + " ".join(dump(f) for f in form) + ")"
    raise SexpError(f"cannot dump {form!r}")


def dump_all(forms: Any) -> str:
    return "\n".join(dump(f) for f in forms)


# -- logic bridge: form <-> Atom / Literal ---------------------------------
def _term_to_form(t: Any) -> Sym:
    if isinstance(t, Var):
        return Sym("?" + t.name)
    if isinstance(t, Const):
        return Sym(t.name)
    raise SexpError(f"not a term: {t!r}")


def _form_to_term(f: Form) -> Union[Const, Var]:
    if isinstance(f, Sym):
        s = str(f)
        return Var(s[1:]) if s.startswith("?") else Const(s)
    raise SexpError(f"not a term form: {f!r}")


def atom_to_form(a: Atom) -> tuple:
    return (Sym(a.pred), *(_term_to_form(t) for t in a.args))


def form_to_atom(f: Form) -> Atom:
    if not isinstance(f, tuple) or not f or not isinstance(f[0], Sym):
        raise SexpError(f"not an atom form: {f!r}")
    return Atom(str(f[0]), tuple(_form_to_term(t) for t in f[1:]))


def literal_to_form(lit: Literal) -> tuple:
    body = atom_to_form(lit.atom)
    return (Sym("not"), body) if lit.negated else body


def form_to_literal(f: Form) -> Literal:
    if isinstance(f, tuple) and len(f) == 2 and isinstance(f[0], Sym) and f[0] == "not":
        return Literal(form_to_atom(f[1]), negated=True)
    return Literal(form_to_atom(f))


def rule_to_form(r: Rule) -> tuple:
    parts: list = [Sym("rule")]
    if r.name is not None:
        parts.append(Sym(r.name))
    parts.append(atom_to_form(r.head))
    parts.extend(atom_to_form(b) for b in r.body)
    return tuple(parts)


def form_to_rule(f: Form) -> Rule:
    """Read ``(rule [name] (head) (body)...)``.

    A bare symbol right after ``rule`` is the rule name; a list is the head.
    """
    if not isinstance(f, tuple) or not f or f[0] != Sym("rule"):
        raise SexpError(f"not a rule form: {f!r}")
    rest = f[1:]
    name = None
    if rest and isinstance(rest[0], Sym):
        name = str(rest[0])
        rest = rest[1:]
    if not rest:
        raise SexpError("rule form has no head")
    return Rule(form_to_atom(rest[0]), tuple(form_to_atom(b) for b in rest[1:]), name)