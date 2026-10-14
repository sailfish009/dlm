"""DLM v0.0038 -- the Lisp seam (untrusted symbolic medium).

Lisp is the medium, not the judge: it represents ground axioms, matches their
pronouns (``?x``) against referential facts, and evaluates forms.  Only
``query`` reads truth, and only through the kernel closure.  Symbols are plain
strings; lists are tuples; a form is a nested tuple whose head is a string.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import Atom, Const, KnowledgeBase, Rule, Var, entails

__all__ = [
    "parse", "dump", "is_var", "match_form", "subst_form",
    "form_to_atom", "atom_to_form", "form_to_rule", "rule_to_form",
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


@dataclass
class Env:
    kb: KnowledgeBase = field(default_factory=KnowledgeBase)
    events: List[tuple] = field(default_factory=list)


def eval_form(form: Any, env: Optional[Env] = None) -> Any:
    """Dispatch on the head symbol.  Unknown heads abstain (raise)."""
    if env is None:
        env = Env()
    if not isinstance(form, tuple) or not form or not isinstance(form[0], str):
        raise ValueError(f"not a form: {form!r}")
    head = form[0]
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
    if head in ("query", "prove", "ask"):
        return entails(env.kb, form_to_atom(form[1]))
    raise ValueError(f"unknown form head {head!r}")


def eval_sexp(text: str, env: Optional[Env] = None):
    env = env if env is not None else Env()
    return tuple(eval_form(f, env) for f in parse(text))