"""DLM v0.0029 -- trusted substrate and public surface (see :mod:`dlm.deductive`).

The minimal DLM base is split into exactly two files:

* ``dlm/__init__.py`` (this file) -- the **trusted substrate** and the public
  surface: the term/atom/rule logic, canonical S-expression syntax, exact
  unification, the fact/rule store, the re-checkable proof certificate and
  sound/complete deduction.  It carries only what the fused core needs (the
  general negative-literal side table and the bulk-certificate API are gone).
* ``dlm/deductive.py`` -- the **fused core**, the single place the learning
  mechanism lives: a weighted clause is at once a Horn rule the kernel uses
  (truth) and a weighted feature the scorer uses (order); a ``Theory`` is an
  ordered clause set (the model), matching is one-way *subsumption*, LGG
  induction adds clauses and the perceptron reweights them.

The deductive model's attention analogue is that core: an exact unification
chosen by a *learned* order, then verified by the kernel::

    propose  ->  unify  ->  verify

Trust invariant (structural): the theory only *orders*; only the kernel
(``prove`` + ``verify``) *asserts*.  An unnormalisable input abstains.

Untrusted companions are imported the other way round and never from here:
:mod:`dlm.ssl` (IR self-supervision), :mod:`dlm.io` (the data boundary),
:mod:`dlm.selfsup` (the verifiable-reward self-supervised loop),
:mod:`dlm.vector` (a grounded, exactly-invertible representation vector for one
IR tree -- the coordinates are named role+token symbols the model can read) and
:mod:`dlm.execute` (a bounded, order-sensitive backward-chaining executor plus the
experience-fed proof-credit loop: the learned order finally controls *execution*,
not just a candidate list, and the kernel still asserts) and :mod:`dlm.control` (a
goal-conditioned control layer over that executor: the order is scored per
``(goal, clause)``, so the same clause is ranked first for the goal it can close
and last for the one it cannot -- learned from the execution trace, still only an
order) and :mod:`dlm.lisp` (the Lisp seam: one evaluator over forms, code-level
pattern matching, macros that write code, proofs as terms, source round-trips and
tree reification -- the S-expr substrate finally reads and writes itself, while
the kernel stays function-free)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

__version__ = "0.0.29"

__all__ = [
    # -- logic -------------------------------------------------------
    "Const", "Var", "Term", "Atom", "Rule",
    # -- sexp --------------------------------------------------------
    "Sym", "Form", "SexpError", "parse", "dump",
    "atom_to_form", "form_to_atom",
    "rule_to_form", "form_to_rule",
    # -- unify -------------------------------------------------------
    "Subst", "walk", "apply_atom", "unify",
    # -- kb ----------------------------------------------------------
    "KnowledgeBase",
    # -- kernel ------------------------------------------------------
    "Proof", "verify",
    # -- engine ------------------------------------------------------
    "closure", "entails", "prove",
    # -- deductive (dlm/deductive.py): the fused core -------------------
    "Clause", "Theory",
    "head_subsumes", "subsumes", "learn",
    "lgg_atoms", "variate", "literal_space", "covers", "induce_clauses",
    "Decision", "solve", "run_experiment",
    "clause_to_form", "clause_from_form",
    "theory_to_form", "theory_from_form", "theory_sexp", "theory_from_sexp",
    "__version__",
]


# ============================================================================
# logic
# ============================================================================
# -- terms -----------------------------------------------------------------
@dataclass(frozen=True)
class Const:
    """A constant (an individual, a named entity)."""

    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Var:
    """A logical variable. ``?`` is added only in the string form."""

    name: str

    def __str__(self) -> str:
        return "?" + self.name


Term = Union[Const, Var]


# -- atoms and literals ----------------------------------------------------
@dataclass(frozen=True)
class Atom:
    """A function-free atom: a predicate applied to ordered terms."""

    pred: str
    args: Tuple[Term, ...] = ()

    def __post_init__(self) -> None:
        for a in self.args:
            if not isinstance(a, (Const, Var)):
                raise TypeError(
                    f"function-free: an atom argument must be Const or Var, got {a!r}"
                )

    @property
    def arity(self) -> int:
        return len(self.args)

    def is_ground(self) -> bool:
        return all(isinstance(a, Const) for a in self.args)

    def variables(self) -> Tuple[Var, ...]:
        return tuple(a for a in self.args if isinstance(a, Var))

    def __str__(self) -> str:
        return "(" + " ".join((self.pred, *(str(a) for a in self.args))) + ")"


# -- rules: the general laws -----------------------------------------------
@dataclass(frozen=True)
class Rule:
    """A definite Horn rule: ``head :- body``.

    ``body`` is a conjunction of positive atoms (function-free Horn). Negation is
    not part of a rule body, and v0.0019 removed the KB negative-literal side
    table: the substrate is positive Horn. A rule is *safe*: every head variable
    must occur in a positive body atom, so forward chaining can ground the head.
    """

    head: Atom
    body: Tuple[Atom, ...] = ()
    name: Optional[str] = None

    def __post_init__(self) -> None:
        for b in self.body:
            if not isinstance(b, Atom):
                raise TypeError(f"a rule body must be atoms, got {b!r}")
        if not self.body:
            raise ValueError("a rule needs a non-empty body (use a fact instead)")
        head_vars = set(self.head.variables())
        body_vars = set()
        for b in self.body:
            body_vars.update(b.variables())
        if not head_vars <= body_vars:
            missing = head_vars - body_vars
            raise ValueError(f"unsafe rule: head variables not in body: {missing}")

    def variables(self) -> Tuple[Var, ...]:
        out = list(self.head.variables())
        for b in self.body:
            for v in b.variables():
                if v not in out:
                    out.append(v)
        return tuple(out)

    def __str__(self) -> str:
        parts = ["rule"]
        if self.name is not None:
            parts.append(self.name)
        parts.append(str(self.head))
        parts.extend(str(b) for b in self.body)
        return "(" + " ".join(parts) + ")"


# ============================================================================
# sexp
# ============================================================================
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


# -- logic bridge: form <-> Atom / Rule ------------------------------------
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


# ============================================================================
# unify
# ============================================================================
Subst = Dict[Var, Term]



def walk(t: Term, s: Subst) -> Term:
    """Follow variable bindings to a representative."""
    while isinstance(t, Var) and t in s:
        nxt = s[t]
        if nxt == t:  # defensive: a var bound to itself
            break
        t = nxt
    return t


def apply_atom(a: Atom, s: Subst) -> Atom:
    if not a.args:
        return a
    return Atom(a.pred, tuple(walk(x, s) for x in a.args))


def unify(a: Atom, b: Atom, s: Optional[Subst] = None) -> Optional[Subst]:
    """Unify two atoms under ``s``; return an extended substitution or ``None``."""
    if a.pred != b.pred or a.arity != b.arity:
        return None
    out: Subst = dict(s) if s else {}
    for x, y in zip(a.args, b.args):
        x = walk(x, out)
        y = walk(y, out)
        if x == y:
            continue
        if isinstance(x, Var):
            out[x] = y
        elif isinstance(y, Var):
            out[y] = x
        else:
            return None
    return out


# ============================================================================
# kb
# ============================================================================
class KnowledgeBase:
    def __init__(self) -> None:
        self._facts: Dict[str, set] = {}
        self._rules: List[Rule] = []
        self._rules_by_head: Dict[str, List[Rule]] = {}

    # -- construction ------------------------------------------------------
    def add_fact(self, atom: Atom) -> "KnowledgeBase":
        if not isinstance(atom, Atom):
            raise TypeError(f"fact must be an Atom, got {atom!r}")
        if not atom.is_ground():
            raise ValueError(f"a fact must be ground: {atom}")
        self._facts.setdefault(atom.pred, set()).add(atom)
        return self

    def add_rule(self, rule: Rule) -> "KnowledgeBase":
        if not isinstance(rule, Rule):
            raise TypeError(f"rule must be a Rule, got {rule!r}")
        if rule in self._rules:
            return self
        self._rules.append(rule)
        self._rules_by_head.setdefault(rule.head.pred, []).append(rule)
        return self

    def add_facts(self, atoms: Iterable[Atom]) -> "KnowledgeBase":
        """Add many ground facts at once (e.g. the output of seam A)."""
        for atom in atoms:
            self.add_fact(atom)
        return self

    def copy(self) -> "KnowledgeBase":
        """Independent duplicate (same immutable facts/rules, fresh indexes)."""
        other = KnowledgeBase()
        other._facts = {pred: set(fs) for pred, fs in self._facts.items()}
        other._rules = list(self._rules)
        other._rules_by_head = {h: list(rs) for h, rs in self._rules_by_head.items()}
        return other

    # -- queries -----------------------------------------------------------
    def facts(self) -> Tuple[Atom, ...]:
        return tuple(f for fs in self._facts.values() for f in fs)

    def facts_by_pred(self, pred: str) -> Tuple[Atom, ...]:
        return tuple(self._facts.get(pred, ()))

    def has_fact(self, atom: Atom) -> bool:
        return atom in self._facts.get(atom.pred, ())

    def rules(self) -> Tuple[Rule, ...]:
        return tuple(self._rules)

    def rules_by_head(self, pred: str) -> Tuple[Rule, ...]:
        return tuple(self._rules_by_head.get(pred, ()))

    def has_rule(self, rule: Rule) -> bool:
        return rule in self._rules

    def remove_rule(self, rule: Rule) -> "KnowledgeBase":
        """Drop ``rule`` if present (idempotent); rebuilds the head index."""
        if rule not in self._rules:
            return self
        self._rules = [r for r in self._rules if r != rule]
        self._rules_by_head = {}
        for r in self._rules:
            self._rules_by_head.setdefault(r.head.pred, []).append(r)
        return self

    def remove_fact(self, atom: Atom) -> "KnowledgeBase":
        """Drop ``atom`` if present (idempotent); prunes an empty predicate bucket."""
        bucket = self._facts.get(atom.pred)
        if bucket is None:
            return self
        bucket.discard(atom)
        if not bucket:
            del self._facts[atom.pred]
        return self

    def predicates(self) -> Tuple[str, ...]:
        return tuple(sorted(set(self._facts) | set(self._rules_by_head)))

    def __len__(self) -> int:
        return sum(len(fs) for fs in self._facts.values())


# ============================================================================
# kernel
# ============================================================================
@dataclass(frozen=True)
class Proof:
    atom: Atom
    rule: Optional[Rule] = None
    premises: Tuple["Proof", ...] = ()

    @property
    def is_fact(self) -> bool:
        return self.rule is None

    def __str__(self) -> str:
        if self.rule is None:
            return str(self.atom)
        head = self.rule.name or "rule"
        inner = f"{self.atom} {head}"
        if self.premises:
            inner += " " + " ".join(str(p) for p in self.premises)
        return f"(proof {inner})"


def verify(proof: Proof, kb: KnowledgeBase) -> bool:
    """Re-check ``proof`` against ``kb``. Returns True only if sound."""
    if not isinstance(proof, Proof) or not proof.atom.is_ground():
        return False
    if proof.rule is None:
        return kb.has_fact(proof.atom)
    rule = proof.rule
    if not kb.has_rule(rule):
        return False
    if len(proof.premises) != len(rule.body):
        return False
    s: Optional[Subst] = unify(proof.atom, rule.head)
    if s is None:
        return False
    for body_atom, premise in zip(rule.body, proof.premises):
        s = unify(body_atom, premise.atom, s)
        if s is None:
            return False
    return all(verify(p, kb) for p in proof.premises)


# ============================================================================
# engine
# ============================================================================
# -- forward chaining (shared core) ----------------------------------------
class _Store:
    """A predicate->atoms index plus an argument->atoms index for joins.

    The argument index lets a join start from the smallest bucket instead of
    scanning every atom of a predicate.  That is what keeps transitive closure
    from being quadratic in the number of edges.
    """

    __slots__ = ("by_pred", "by_arg", "size")

    def __init__(self) -> None:
        self.by_pred: Dict[str, Set[Atom]] = {}
        self.by_arg: Dict[str, Dict[int, Dict[Const, Set[Atom]]]] = {}
        self.size = 0

    def add(self, atom: Atom) -> bool:
        bucket = self.by_pred.setdefault(atom.pred, set())
        if atom in bucket:
            return False
        bucket.add(atom)
        self.size += 1
        per_pos = self.by_arg.setdefault(atom.pred, {})
        for i, arg in enumerate(atom.args):
            if isinstance(arg, Const):
                per_pos.setdefault(i, {}).setdefault(arg, set()).add(atom)
        return True

    def candidates(self, atom: Atom, subst: Subst) -> Iterable[Atom]:
        best: Optional[Set[Atom]] = None
        for i, arg in enumerate(atom.args):
            bound = walk(arg, subst)
            if isinstance(bound, Const):
                bucket = self.by_arg.get(atom.pred, {}).get(i, {}).get(bound)
                if bucket is None:
                    return ()
                if best is None or len(bucket) < len(best):
                    best = bucket
        if best is not None:
            return tuple(best)
        return tuple(self.by_pred.get(atom.pred, ()))

    def atoms(self) -> Iterable[Atom]:
        for bucket in self.by_pred.values():
            yield from bucket


def _match_sources(atoms: Tuple[Atom, ...], stores: Tuple[_Store, ...], subst: Subst):
    """Like :func:`_match`, but each atom joins against its own store.

    Semi-naive evaluation needs one body position restricted to the *delta* set
    while the rest use the full index.
    """
    if not atoms:
        yield subst
        return
    first, rest = atoms[0], atoms[1:]
    for fact in stores[0].candidates(first, subst):
        s2 = unify(first, fact, subst)
        if s2 is not None:
            yield from _match_sources(rest, stores[1:], s2)


def _derivations(kb: KnowledgeBase):
    """Forward chaining to fixpoint (semi-naive / delta rules).

    Returns ``(index, support)`` where ``index`` maps a predicate to the set of
    derivable ground atoms and ``support[atom]`` records how the atom was first
    derived: ``("fact", None, None)`` or ``("rule", rule, substitution)``.

    Everything derivable in the previous round is already in ``index``, so a rule
    instance whose body is entirely old has been fired; only instances with at
    least one body atom from the previous round's *delta* can add anything.  That
    turns the ``while changed`` full re-join into a per-delta join and keeps the
    same least fixpoint (and therefore the same atom set).
    """
    index = _Store()
    delta = _Store()
    support: Dict[Atom, Tuple] = {}
    for f in kb.facts():
        if index.add(f):
            delta.add(f)
        support[f] = ("fact", None, None)

    rules = tuple(kb.rules())
    while delta.size:
        new = _Store()
        new_support: Dict[Atom, Tuple] = {}
        for rule in rules:
            body = rule.body
            if not body:
                continue
            n = len(body)
            for j in range(n):
                stores = (index,) * n
                stores = stores[:j] + (delta,) + stores[j + 1:]
                for subst in _match_sources(body, stores, {}):
                    head = apply_atom(rule.head, subst)
                    if not head.is_ground():
                        continue
                    if head in index.by_pred.get(head.pred, ()) or head in new.by_pred.get(head.pred, ()):
                        continue
                    new.add(head)
                    new_support[head] = ("rule", rule, dict(subst))
        for atom in new.atoms():
            index.add(atom)
        support.update(new_support)
        delta = new
    return index.by_pred, support


def closure(kb: KnowledgeBase) -> Set[Atom]:
    """All ground atoms derivable from ``kb`` (facts + Horn rules)."""
    index, _ = _derivations(kb)
    return {f for fs in index.values() for f in fs}


def entails(kb: KnowledgeBase, atom: Atom) -> bool:
    return atom in closure(kb)


# -- certificates: reconstruct from the closure's support ------------------
def _build_proof(atom: Atom, support: Dict[Atom, Tuple], memo: Dict[Atom, Proof]) -> Proof:
    cached = memo.get(atom)
    if cached is not None:
        return cached
    kind, rule, subst = support[atom]
    if kind == "fact":
        proof = Proof(atom, None, ())
    else:
        body = tuple(apply_atom(b, subst) for b in rule.body)
        premises = tuple(_build_proof(b, support, memo) for b in body)
        proof = Proof(atom, rule, premises)
    memo[atom] = proof
    return proof


def prove(kb: KnowledgeBase, goal: Atom) -> Optional[Proof]:
    """Return a re-checkable certificate for a **ground** goal, or ``None``.

    Complete w.r.t. :func:`entails`: ``prove`` succeeds iff ``goal`` is in the
    closure. For a non-ground goal it returns ``None`` (abstain) -- use
    :func:`closure` / :func:`entails` for existential questions.
    """
    if not goal.is_ground():
        return None
    _, support = _derivations(kb)
    if goal not in support:
        return None
    return _build_proof(goal, support, {})


# ============================================================================
# deductive learning core -- the derivation layer (dlm/deductive.py)
# ============================================================================
# Imported *after* the substrate above is defined, so ``deductive`` may read the
# trusted names with ``from . import ...`` without a circular-import failure.
from .deductive import (  # noqa: E402
    Clause,
    Decision,
    Theory,
    clause_from_form,
    clause_to_form,
    covers,
    head_subsumes,
    induce_clauses,
    learn,
    lgg_atoms,
    literal_space,
    run_experiment,
    solve,
    subsumes,
    theory_from_form,
    theory_from_sexp,
    theory_sexp,
    theory_to_form,
    variate,
)
