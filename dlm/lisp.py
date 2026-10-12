"""DLM v0.0029 -- the Lisp seam: a unified evaluator over the S-expr substrate.

(Untrusted layer.  It imports :mod:`dlm` and :mod:`dlm.deductive` one-way and
never the reverse; the trusted two-file core is unchanged.)

v0.0020-v0.0028 gave the model eyes, memory, a proposer, a vector, a bounded
executor and goal-conditioned control -- but every bridge between the S-expr
*substrate* and the kernel was a named, one-directional function
(``clause_from_form``, ``theory_from_sexp``, ...).  There was no single place
where a form could be *evaluated*, no way to match a code pattern against a code
tree, no macro that writes code, no proof that could be read back, and the IR
tree (perception) and the logic (reasoning) were disjoint dialects.  This module
closes those six gaps in one layer:

1. **Unified evaluation.**  :func:`eval_form` dispatches on the head symbol of a
   form (``fact``/``rule``/``clause``/``theory``/``query``/``verify``/``quote``/
   ``defmacro``/``do``/...).  Only registered heads evaluate; an unknown head
   *abstains* (raises :class:`EvalError`) -- it never guesses.  Only ``query``
   reaches the kernel, and it only ever calls :func:`dlm.prove`.
2. **Term = form (in the code algebra).**  The kernel's term algebra stays
   function-free; but the *code* algebra here has variables (``?x``), a wildcard
   (``_``) and structural unification over nested tuples: :func:`match_form`,
   :func:`subst_form`.  That is exactly what a macro needs.  A tree can be
   *reified* into flat, ground atoms by :func:`tree_atoms` to enter the kernel.
3. **Quote, quasiquote and macros.**  :func:`quote_form` / :func:`quasiquote_form`
   / :class:`DefMacro` / :func:`macroexpand` let a form *generate* forms, which
   :func:`eval_form` then evaluates.  The model writes Lisp, not just objects.
4. **Source round-trip.**  The self-supervised loop can be re-entered through its
   own source: :func:`theory_source` / :func:`source_theory` /
   :func:`source_roundtrip` / :func:`run_source_loop`.  The grown theory is
   emitted, re-read and checked equal -- the S-expr is the medium, not only a view.
5. **Proof as data.**  :func:`proof_to_form` / :func:`form_to_proof` /
   :func:`verify_form` make a certificate a term: emitted, transported, re-read
   and *re-verified*.  Proof-carrying code closes.
6. **Perception -> proof.**  :func:`tree_atoms` / :func:`tree_kb` /
   :func:`query_tree` reify any Form tree (e.g. an :mod:`dlm.ssl` IR tree) into
   ground facts so the kernel can *prove* things about what was read.

Honest boundary: this does **not** add function symbols, lambdas or a general
``eval`` of arbitrary code to the *kernel*; the logic stays function-free and
decidable.  It adds a code-level evaluator above the kernel.  The two algebras
meet only at :func:`form_to_atom` / :func:`tree_atoms`, and that meeting is the
subject of v0.0030.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from . import (
    Atom,
    Const,
    Form,
    KnowledgeBase,
    Proof,
    Rule,
    SexpError,
    Sym,
    Var,
    atom_to_form,
    dump,
    form_to_atom,
    form_to_rule,
    parse,
    prove,
    rule_to_form,
    verify,
)
from .deductive import (
    Clause,
    Theory,
    clause_from_form,
    clause_to_form,
    theory_from_form,
    theory_to_form,
    theory_sexp,
    theory_from_sexp,
)

__all__ = [
    "EvalError",
    "Env",
    "DefMacro",
    "is_var",
    "is_wildcard",
    "form_variables",
    "match_form",
    "subst_form",
    "quote_form",
    "is_quote",
    "unquote",
    "quasiquote_form",
    "macroexpand",
    "eval_form",
    "eval_sexp",
    "read_eval",
    "proof_to_form",
    "form_to_proof",
    "verify_form",
    "theory_source",
    "source_theory",
    "source_roundtrip",
    "expand_source",
    "SourceLoopResult",
    "run_source_loop",
    "tree_atoms",
    "tree_kb",
    "query_tree",
]


class EvalError(SexpError):
    """Raised when a form cannot be evaluated.  Reading is strict; malformed or
    unknown forms abstain rather than guessing."""


# ============================================================================
# 1. the code algebra: variables and structural matching over nested forms
#    (kernel terms stay function-free; this is the *code* algebra)
# ============================================================================
def is_var(f: Any) -> bool:
    """A metavariable in a code pattern/template (``?x``)."""
    return isinstance(f, Sym) and len(str(f)) > 1 and str(f)[0] == "?"


def is_wildcard(f: Any) -> bool:
    """The anonymous pattern wildcard ``_`` (matches anything, binds nothing)."""
    return isinstance(f, Sym) and str(f) == "_"


def form_variables(form: Form) -> Tuple[str, ...]:
    """Distinct metavariable names (with the leading ``?``) in first-seen order."""
    seen: List[str] = []
    stack = [form]
    while stack:
        f = stack.pop(0)
        if is_var(f):
            name = str(f)
            if name not in seen:
                seen.append(name)
        elif isinstance(f, tuple):
            stack = list(f) + stack
    return tuple(seen)


def match_form(
    pattern: Form, form: Form, bindings: Optional[Dict[str, Form]] = None
) -> Optional[Dict[str, Form]]:
    """Structurally match ``pattern`` against ``form``; return bindings or ``None``.

    A metavariable (``?x``) binds; a repeated metavariable must be consistent; the
    wildcard ``_`` matches anything without binding.  Lists match lists of equal
    length.  This is the code-level analogue of :func:`dlm.unify`.
    """
    out: Dict[str, Form] = dict(bindings) if bindings else {}

    def go(p: Form, f: Form) -> bool:
        if is_wildcard(p):
            return True
        if is_var(p):
            name = str(p)
            if name in out:
                return out[name] == f
            out[name] = f
            return True
        if isinstance(p, tuple):
            if not isinstance(f, tuple) or len(p) != len(f):
                return False
            return all(go(pi, fi) for pi, fi in zip(p, f))
        return p == f

    return out if go(pattern, form) else None


def subst_form(form: Form, bindings: Dict[str, Form]) -> Form:
    """Replace each metavariable by its binding, recursing into the tree."""
    if is_var(form):
        return bindings.get(str(form), form)
    if isinstance(form, tuple):
        return tuple(subst_form(x, bindings) for x in form)
    return form


# ============================================================================
# 2. quote, quasiquote, macros -- forms that write forms
# ============================================================================
def quote_form(form: Form) -> tuple:
    """``(quote <form>)``: suspend evaluation, yield the form as data."""
    return (Sym("quote"), form)


def is_quote(form: Any) -> bool:
    return isinstance(form, tuple) and len(form) == 2 and form[0] == Sym("quote")


def unquote(form: Form) -> Form:
    """The payload of a ``(quote <form>)``."""
    if not is_quote(form):
        raise EvalError(f"not a quote form: {form!r}")
    return form[1]


def quasiquote_form(template: Form, bindings: Dict[str, Form]) -> Form:
    """Fill a template with ``bindings``.

    A bare metavariable ``?x`` and an explicit ``(unquote ?x)`` are substituted;
    everything else is copied literally.  Deterministic and total.
    """

    def go(f: Form) -> Form:
        if is_var(f):
            return bindings.get(str(f), f)
        if isinstance(f, tuple):
            if len(f) == 2 and f[0] == Sym("unquote"):
                arg = f[1]
                if is_var(arg):
                    return bindings.get(str(arg), arg)
                return go(arg)
            return tuple(go(x) for x in f)
        return f

    return go(template)


@dataclass(frozen=True)
class DefMacro:
    """A macro: ``(name <arg-pattern> -> <template>)``.

    ``pattern`` matches the *argument list* of a call ``(name arg ...)``; the
    bindings then fill ``template``.  The result is itself a form to evaluate --
    code that writes code.
    """

    name: str
    pattern: tuple
    template: tuple
    doc: str = ""


def macroexpand(
    form: Form, macros: Dict[str, DefMacro], *, limit: int = 16
) -> Form:
    """Expand the outermost macro call repeatedly until the head is not a macro.

    Never evaluates; expansion is bounded by ``limit`` so a self-referential macro
    aborts instead of looping.  An expansion that does not match its own pattern
    abstains with :class:`EvalError`.
    """
    out = form
    for _ in range(limit):
        if not (isinstance(out, tuple) and out and isinstance(out[0], Sym)):
            return out
        macro = macros.get(str(out[0]))
        if macro is None:
            return out
        bindings = match_form(macro.pattern, out[1:])
        if bindings is None:
            raise EvalError(f"macro {macro.name!r} pattern does not match {dump(out)}")
        nxt = quasiquote_form(macro.template, bindings)
        if nxt == out:
            return out
        out = nxt
    raise EvalError("macro expansion did not terminate (recursive macro?)")


# ============================================================================
# 3. the unified evaluator -- one place where a form means something
# ============================================================================
@dataclass
class Env:
    """The evaluation state: a knowledge base, a macro table, and the theory.

    ``events`` is an append-only, deterministic log of what each evaluation did
    (used by the experiment); it never affects a verdict.
    """

    kb: KnowledgeBase = field(default_factory=KnowledgeBase)
    macros: Dict[str, DefMacro] = field(default_factory=dict)
    theory: Optional[Theory] = None
    events: List[Tuple[str, str]] = field(default_factory=list)


# heads that evaluate to a *fact / rule / clause / theory* (structure only)
_HEADS_FACT = ("fact", "assert")
_HEADS_RULE = ("rule",)
_HEADS_QUERY = ("query", "prove", "ask")
_HEADS_VERIFY = ("verify", "check")
_HEADS_MACRO = ("defmacro", "defrule", "macro")
_HEADS_DO = ("do", "seq", "begin")


def _need(form: tuple, n: int, what: str) -> None:
    if len(form) != n:
        raise EvalError(f"({what} ...) needs {n - 1} argument(s), got {len(form) - 1}")


def _defmacro(form: tuple, env: Env) -> Sym:
    if len(form) not in (4, 5):
        raise EvalError("(defmacro <name> <arg-pattern> <template> [<doc>])")
    name = form[1]
    if not isinstance(name, Sym):
        raise EvalError(f"macro name must be a symbol, got {name!r}")
    pattern, template = form[2], form[3]
    if not isinstance(pattern, tuple):
        raise EvalError(f"macro arg-pattern must be a list, got {pattern!r}")
    doc = str(form[4]) if len(form) == 5 else ""
    env.macros[str(name)] = DefMacro(str(name), pattern, template, doc)
    env.events.append(("defmacro", str(name)))
    return name


def eval_form(form: Form, env: Optional[Env] = None) -> Any:
    """Evaluate one form.  A form is a tuple whose head symbol selects the rule.

    Non-tuple forms are self-evaluating (symbols and strings are their own value).
    Only registered heads evaluate; anything else abstains with
    :class:`EvalError`.  Only ``query`` reaches the kernel, and only through
    :func:`dlm.prove` -- so the evaluator can never assert beyond what is proved.
    """
    if env is None:
        env = Env()
    if not isinstance(form, tuple):
        return form
    if not form:
        raise EvalError("the empty form () has no head")
    head = form[0]
    if not isinstance(head, Sym):
        raise EvalError(f"a form must start with a symbol, got {form!r}")
    name = str(head)

    if name in env.macros:
        return eval_form(macroexpand(form, env.macros), env)

    if name == "quote":
        _need(form, 2, name)
        return form[1]
    if name == "quasiquote":
        _need(form, 2, name)
        return form[1]
    if name in _HEADS_FACT:
        _need(form, 2, name)
        atom = form_to_atom(form[1])
        env.kb.add_fact(atom)
        env.events.append(("fact", str(atom)))
        return atom
    if name in _HEADS_RULE:
        rule = form_to_rule(form)
        env.kb.add_rule(rule)
        env.events.append(("rule", rule.name or ""))
        return rule
    if name == "clause":
        clause = clause_from_form(form)
        base = env.theory if env.theory is not None else Theory("lisp", ())
        env.theory = Theory(base.name, base.clauses + (clause,))
        env.events.append(("clause", clause.name))
        return clause
    if name == "theory":
        theory = theory_from_form(form)
        env.theory = theory
        env.events.append(("theory", theory.name))
        return theory
    if name in _HEADS_QUERY:
        _need(form, 2, name)
        goal = form_to_atom(form[1])
        if not goal.is_ground():
            raise EvalError(f"a query goal must be ground, got {goal}")
        env.events.append(("query", str(goal)))
        return prove(env.kb, goal)
    if name in _HEADS_VERIFY:
        _need(form, 2, name)
        ok = verify(form_to_proof(form[1]), env.kb)
        env.events.append(("verify", str(ok)))
        return ok
    if name in _HEADS_MACRO:
        return _defmacro(form, env)
    if name == "expand":
        _need(form, 2, name)
        return macroexpand(form[1], env.macros)
    if name in _HEADS_DO:
        result: Any = None
        for sub in form[1:]:
            result = eval_form(sub, env)
        return result
    if name == "emit":
        if env.theory is None:
            raise EvalError("(emit) needs a theory in the environment")
        return Sym(theory_sexp(env.theory))
    raise EvalError(f"unknown form head {name!r}")


def eval_sexp(text: str, env: Optional[Env] = None) -> Tuple[Any, ...]:
    """Parse ``text`` and evaluate each top-level form in order."""
    if env is None:
        env = Env()
    return tuple(eval_form(f, env) for f in parse(text))


def read_eval(text: str, env: Optional[Env] = None) -> Tuple[Any, ...]:
    """Alias for :func:`eval_sexp` -- read a program, then evaluate it."""
    return eval_sexp(text, env)


# ============================================================================
# 4. proof as data -- a certificate is a term you can emit and re-verify
# ============================================================================
def proof_to_form(proof: Proof) -> tuple:
    """``(proof (atom) (rule ...) <premise>...)`` -- a fact uses ``nil`` for rule.

    A proof is emitted with :func:`dlm.atom_to_form` / :func:`dlm.rule_to_form`,
    so it re-reads with :func:`form_to_proof` and re-checks with :func:`verify`.
    """
    if not isinstance(proof, Proof):
        raise TypeError(f"proof_to_form needs a Proof, got {proof!r}")
    parts: list = [Sym("proof"), atom_to_form(proof.atom)]
    parts.append(Sym("nil") if proof.rule is None else rule_to_form(proof.rule))
    parts.extend(proof_to_form(p) for p in proof.premises)
    return tuple(parts)


def form_to_proof(form: Form) -> Proof:
    """Read a ``(proof ...)`` form back into a :class:`dlm.Proof`."""
    if not (isinstance(form, tuple) and len(form) >= 2 and form[0] == Sym("proof")):
        raise EvalError(f"not a proof form: {form!r}")
    atom = form_to_atom(form[1])
    rest = form[2:]
    rule_form = rest[0] if rest else Sym("nil")
    premises = tuple(form_to_proof(p) for p in rest[1:])
    if isinstance(rule_form, Sym) and str(rule_form) == "nil":
        rule: Optional[Rule] = None
    else:
        rule = form_to_rule(rule_form)
    return Proof(atom, rule, premises)


def verify_form(form: Form, kb: KnowledgeBase) -> bool:
    """Re-check a proof given as a form against ``kb`` (the kernel does the check)."""
    return verify(form_to_proof(form), kb)


# ============================================================================
# 5. source round-trip -- the loop reads and writes its own Lisp
# ============================================================================
def theory_source(theory: Theory) -> str:
    """The canonical S-expr source of a theory (structure and order in one form)."""
    return theory_sexp(theory)


def source_theory(text: str) -> Theory:
    """Read exactly one ``(theory ...)`` source form back into a theory."""
    return theory_from_sexp(text)


def source_roundtrip(theory: Theory) -> bool:
    """True iff emitting then reading a theory is the identity."""
    return source_theory(theory_source(theory)) == theory


def expand_source(text: str, macros: Dict[str, DefMacro]) -> str:
    """Rewrite macro calls in a source program, returning new source (no eval)."""
    return "\n".join(dump(macroexpand(f, macros)) for f in parse(text))


@dataclass(frozen=True)
class SourceLoopResult:
    """A self-supervised run whose grown theory was re-entered through source."""

    loop: Any
    source: str
    stable: bool

    def to_dict(self) -> dict:
        return {
            "rounds": self.loop.rounds,
            "params": self.loop.theory.params,
            "false_assert": self.loop.false_assert,
            "mean_held_coverage": round(self.loop.mean_held_coverage, 6),
            "source_roundtrip_stable": self.stable,
        }


def run_source_loop(tasks: Any, *, name: str = "source_selfsup", **kwargs: Any) -> SourceLoopResult:
    """Run the self-supervised loop, then close it through its own source.

    The loop grows a theory as objects; we emit it as S-expr, read it back and
    require the re-read theory to equal the grown one.  That is the minimal step
    that makes the source the *medium* of self-modification rather than a view.
    The import is deferred so this layer stays importable without :mod:`dlm.selfsup`.
    """
    from .selfsup import run_loop

    result = run_loop(tasks, name=name, **kwargs)
    text = theory_source(result.theory)
    stable = source_theory(text) == result.theory
    return SourceLoopResult(loop=result, source=text, stable=stable)


# ============================================================================
# 6. perception -> proof: reify a tree into ground facts the kernel can prove
# ============================================================================
def tree_atoms(tree: Form, *, root: str = "tree") -> Tuple[Atom, ...]:
    """Reify a Form tree into ground ``node``/``leaf`` atoms (deterministic).

    Each sub-form becomes ``(node <path>)`` and each non-tuple leaf becomes
    ``(leaf <path> <value>)``, where ``<path>`` is ``root`` then the child
    indexes (``tree.0.1``).  This is how an :mod:`dlm.ssl` IR tree -- a dialect
    the kernel cannot read as logic -- enters the logic: not as a term, but as a
    finite set of facts that can be *proved about*.
    """
    facts: List[Atom] = []

    def go(f: Form, path: str) -> None:
        if isinstance(f, tuple):
            facts.append(Atom("node", (Const(path),)))
            for i, child in enumerate(f):
                go(child, f"{path}.{i}")
        else:
            facts.append(Atom("leaf", (Const(path), Const(str(f)))))

    go(tree, root)
    return tuple(facts)


def tree_kb(tree: Form, base: Optional[KnowledgeBase] = None) -> KnowledgeBase:
    """A knowledge base with ``tree`` reified as facts (plus ``base`` if given)."""
    kb = base.copy() if base is not None else KnowledgeBase()
    kb.add_facts(tree_atoms(tree))
    return kb


def query_tree(tree: Form, goal: Form, *, base: Optional[KnowledgeBase] = None) -> Optional[Proof]:
    """Prove a ground ``goal`` (form or atom) about a reified ``tree``."""
    kb = tree_kb(tree, base)
    atom = goal if isinstance(goal, Atom) else form_to_atom(goal)
    if not atom.is_ground():
        raise EvalError(f"a tree query must be ground, got {atom}")
    return prove(kb, atom)
