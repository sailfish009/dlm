"""DLM v0.0048 -- the Lisp seam (untrusted symbolic medium).

Lisp is the medium, not the judge: it represents ground axioms, matches their
pronouns (``?x``) against referential facts, and evaluates forms.  Only
``query`` reads truth, and only through the kernel closure.  Symbols are plain
strings; lists are tuples; a form is a nested tuple whose head is a string.

Macros (``defmacro`` / ``macroexpand``) let the medium define new notation:
a macro rewrites a form into another form (code that writes code), and the
result is evaluated by this same ``eval_form``.  Expansion is pure rewriting--
it can never assert past the kernel, so the trust boundary is untouched.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import Atom, Const, KnowledgeBase, Rule, Var, entails

__all__ = [
    "parse", "dump", "is_var", "match_form", "subst_form",
    "form_to_atom", "atom_to_form", "form_to_rule", "rule_to_form",
    "quote_form", "is_quote", "unquote", "quasiquote_form",
    "DefMacro", "macroexpand",
    "Abstain", "findall",
    "Env", "eval_form", "eval_sexp",
]


def _tokenize(text: str) -> List[str]:
    return text.replace("(", " ( ").replace(")", " ) ").split()


def _read_one(toks: List[str], i: int):
    if toks[i] == "(":
        out: List[Any] = []
        i += 1
        while toks[i] != ")":
            f, i = _read_one(toks, i)
            out.append(f)
        return tuple(out), i + 1
    return toks[i], i + 1


def parse(text: str) -> List[Any]:
    toks = _tokenize(text)
    forms, i = [], 0
    while i < len(toks):
        f, i = _read_one(toks, i)
        forms.append(f)
    return forms


def dump(form: Any) -> str:
    if isinstance(form, tuple):
        return "(" + " ".join(dump(x) for x in form) + ")"
    return str(form)


def is_var(f: Any) -> bool:
    return isinstance(f, str) and len(f) > 1 and f[0] == "?"


def match_form(pattern: Any, form: Any, bindings: Optional[Dict[str, Any]] = None):
    """Structurally match a pronominal pattern; ``_`` matches without binding."""
    out: Dict[str, Any] = dict(bindings) if bindings else {}

    def go(p, f) -> bool:
        if p == "_":
            return True
        if is_var(p):
            if p in out:
                return out[p] == f
            out[p] = f
            return True
        if isinstance(p, tuple):
            return (isinstance(f, tuple) and len(p) == len(f)
                    and all(go(a, b) for a, b in zip(p, f)))
        return p == f

    return out if go(pattern, form) else None


def subst_form(form: Any, bindings: Dict[str, Any]) -> Any:
    if is_var(form):
        return bindings.get(form, form)
    if isinstance(form, tuple):
        return tuple(subst_form(x, bindings) for x in form)
    return form


def form_to_atom(f: Any) -> Atom:
    return Atom(f[0], tuple(Var(x) if is_var(x) else Const(x) for x in f[1:]))


def atom_to_form(a: Atom) -> tuple:
    return (a.pred,) + tuple(t.name for t in a.args)


def form_to_rule(f: Any) -> Rule:
    return Rule(form_to_atom(f[1]), tuple(form_to_atom(b) for b in f[2:]))


def rule_to_form(r: Rule) -> tuple:
    return (("rule",) + (atom_to_form(r.head),) + tuple(atom_to_form(b) for b in r.body))


# ---------------------------------------------------------------------------
# quote / quasiquote / macros -- forms that write forms (never truth)
# ---------------------------------------------------------------------------
def quote_form(form: Any) -> tuple:
    """``(quote <form>)``: suspend evaluation, yield the form as data."""
    return ("quote", form)


def is_quote(form: Any) -> bool:
    return isinstance(form, tuple) and len(form) == 2 and form[0] == "quote"


def unquote(form: Any) -> Any:
    """The payload of a ``(quote <form>)``."""
    if not is_quote(form):
        raise ValueError(f"not a quote form: {form!r}")
    return form[1]


def quasiquote_form(template: Any, bindings: Dict[str, Any]) -> Any:
    """Fill a template with ``bindings``.

    A bare metavariable ``?x`` and an explicit ``(unquote ?x)`` are substituted;
    everything else is copied literally.  Deterministic and total.
    """
    def go(f: Any) -> Any:
        if is_var(f):
            return bindings.get(f, f)
        if isinstance(f, tuple):
            if len(f) == 2 and f[0] == "unquote":
                arg = f[1]
                return bindings.get(arg, arg) if is_var(arg) else go(arg)
            return tuple(go(x) for x in f)
        return f

    return go(template)


@dataclass(frozen=True)
class DefMacro:
    """A macro: ``(name <arg-pattern> <template> [<doc>])``.

    ``pattern`` matches the *argument list* of a call ``(name arg ...)``; the
    bindings then fill ``template``.  The result is itself a form to evaluate --
    code that writes code.  A macro only rewrites forms; it never asserts truth.
    """

    name: str
    pattern: tuple
    template: tuple
    doc: str = ""


def macroexpand(form: Any, macros: Dict[str, DefMacro], *, limit: int = 16) -> Any:
    """Expand the outermost macro call repeatedly until the head is not a macro.

    Never evaluates; expansion is bounded by ``limit`` so a self-referential macro
    aborts instead of looping.  A call that does not match its own macro's pattern
    abstains with :class:`ValueError`, and an expansion that makes no progress
    (a macro that rewrites to itself) also abstains.
    """
    out = form
    for _ in range(limit):
        if not (isinstance(out, tuple) and out and isinstance(out[0], str)):
            return out
        macro = macros.get(out[0])
        if macro is None:
            return out
        bindings = match_form(macro.pattern, out[1:])
        if bindings is None:
            raise ValueError(f"macro {macro.name!r} pattern does not match {dump(out)}")
        nxt = quasiquote_form(macro.template, bindings)
        if nxt == out:
            raise ValueError(f"macro {macro.name!r} made no progress")
        out = nxt
    raise ValueError("macro expansion did not terminate (recursive macro?)")


def _defmacro(form: tuple, env: "Env") -> str:
    if len(form) not in (4, 5):
        raise ValueError("(defmacro <name> <arg-pattern> <template> [<doc>])")
    name = form[1]
    if not isinstance(name, str):
        raise ValueError(f"macro name must be a symbol, got {name!r}")
    pattern, template = form[2], form[3]
    if not isinstance(pattern, tuple):
        raise ValueError(f"macro arg-pattern must be a list, got {pattern!r}")
    doc = str(form[4]) if len(form) == 5 else ""
    env.macros[name] = DefMacro(name, pattern, template, doc)
    env.events.append(("defmacro", name))
    return name


@dataclass
class Env:
    kb: KnowledgeBase = field(default_factory=KnowledgeBase)
    macros: Dict[str, DefMacro] = field(default_factory=dict)
    events: List[tuple] = field(default_factory=list)


@dataclass(frozen=True)
class Abstain:
    """Explicit "I do not know" -- a value, not an exception.

    Automation can branch on it (``isinstance(x, Abstain)``) instead of catching,
    so an underivable goal is a first-class outcome rather than a crash.
    """

    reason: str = ""


def findall(goal: Any, env: "Env") -> tuple:
    """All ground instances of a pattern form in the kernel closure.

    The pattern is matched against the *whole* closure, so it enumerates derived
    atoms, not just asserted facts.  Result forms are sorted and deterministic;
    there is no order of proof to leak.
    """
    from . import closure, unify
    pat = form_to_atom(goal)
    out = []
    for f in closure(env.kb):
        if f.pred == pat.pred and len(f.args) == len(pat.args) and unify(pat, f) is not None:
            out.append(atom_to_form(f))
    return tuple(sorted(out, key=dump))


def _prove(form: Any, env: "Env"):
    from .proof import proof_ir, prove as _p
    p = _p(env.kb, form_to_atom(form))
    return Abstain(f"no proof of {dump(form)}") if p is None else proof_ir(p)


def _verify(form: Any, env: "Env") -> bool:
    from .proof import form_to_proof, verify as _v
    return _v(form_to_proof(form), env.kb)


def eval_form(form: Any, env: Optional[Env] = None) -> Any:
    """Dispatch on the head symbol.  Unknown heads abstain (raise)."""
    if env is None:
        env = Env()
    if not isinstance(form, tuple) or not form or not isinstance(form[0], str):
        raise ValueError(f"not a form: {form!r}")
    head = form[0]
    if head in env.macros:
        return eval_form(macroexpand(form, env.macros), env)
    if head == "quote":
        return form[1]
    if head == "quasiquote":
        return form[1]
    if head == "expand":
        return macroexpand(form[1], env.macros)
    if head in ("defmacro", "macro"):
        return _defmacro(form, env)
    if head in ("fact", "assert"):
        a = form_to_atom(form[1])
        env.kb.add_fact(a)
        env.events.append(("fact", str(a)))
        return a
    if head == "rule":
        r = form_to_rule(form)
        env.kb.add_rule(r)
        env.events.append(("rule", r.name))
        return r
    if head in ("query", "ask"):
        return entails(env.kb, form_to_atom(form[1]))
    if head in ("prove", "why"):
        return _prove(form[1], env)
    if head == "findall":
        return findall(form[1], env)
    if head == "verify":
        return _verify(form[1], env)
    if head == "abstain":
        return Abstain(str(form[1]) if len(form) > 1 else "")
    raise ValueError(f"unknown form head {head!r}")


def eval_sexp(text: str, env: Optional[Env] = None):
    env = env if env is not None else Env()
    return tuple(eval_form(f, env) for f in parse(text))