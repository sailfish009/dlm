"""DLM v0.0057 -- trusted kernel (function-free Horn substrate), plus the layers.

Fresh minimal rebuild around one question: what is the learning signal for
deduction?  The answer this version encodes: a general (pronominal,
non-referential) rule is a promise over an open universe, so every new referent
is a fresh, non-self-referential test.  The kernel asserts truth (closure);
everything else proposes.  v0.0047 added stratified negation (closed-world over a
GIVEN universe; non-monotonic closure that retracts; non-stratified rejected).
v0.0048 added TYPED/MODED signatures (:class:`Signature`): a theory is checked
statically for type soundness, range restriction and mode anability, so an
inadmissible rule is rejected before it can assert anything -- typing gates
admission, never truth.  v0.0049 adds the two UNTRUSTED integrators that make the
question "does deduction need a loss?" precise: :mod:`dlm.integral` (the forward
integral = the closure and its kernel-decided debt; the evidence integral
``Z = sum_T exp(-E(T))`` over candidate theories, a measure not an objective) and
:mod:`dlm.connection` (order-sensitive credit under a bounded search, whose
discrete circulation is a nonzero HOLONOMY -- so credit is a connection and
learning it is a path integral, not a descent).  v0.0050 makes the deduction
ladder VISIBLE in the final natural-language reading: N9 realizes a certified
NEGATIVE (a closed-world absence, non-monotonic) and the reader is closed under
a GIVEN typed/moded :class:`Signature`, so an ill-typed theory makes it ABSTAIN
before deriving anything.  v0.0051 adds EQUALITY as a FINITE congruence (D7a,
:mod:`dlm.equality`): the first D7 rung, letting the kernel conclude that two
different symbols denote the SAME layer kind.  It is a conservative extension --
over a given symbol set the alias relation ``same_kind`` is a finite ground
relation and ``uses_layer`` lifts it from definition/method-call evidence -- so a
false closed-world negative (v0.0050 certified ``absent(net, maxpool2d)`` though
the program CALLS ``F.max_pool2d``) is now blocked without adding any positive
Horn conclusion.  Function-free; no weights, no softmax.  v0.0052 MEASURES the
integrators instead of only defining them: :mod:`dlm.effective` (untrusted) turns
the evidence integral into a held-out PREDICTOR and the order/credit integral into
a CONTROLLER, and `experiments/effective` falsifies them at equal budget against
MAP / static / random controls -- the evidence marginal never loses to MAP here
and strictly beats it when two theories are energy-tied, while integrated credit
proves 12/12 goals where static and random prove 2/12.  Well-posedness is not
effectiveness; this version measures the second.  v0.0053 INTEGRATES the leveled
reading into the north-star BODY: ``experiments/mnist/run.py`` and the falsifier
``experiments/reading`` now share ONE pipeline (``mnist.run.pipeline``), and the
body's own final natural-language output IS the N1..N9 reading -- structure +
acquired ``meaning`` + SEARCHED ``dataset_of`` + acquired ``api_effect`` + the
D5/D7a closed-world absence layer.  Before, the body used a private flat realizer
and the purpose sentence ("...to recognize handwritten digits") lived only in a
side experiment; now the body emits it (``northstar_purpose``).  No kernel change.
v0.0054 makes the MODEL the SUBJECT, not the harness: the automation that lets a
deductive model improve without a human -- web access (:mod:`dlm.web`), generic
search providers (:mod:`dlm.search`), the acquisition subject
(:mod:`dlm.acquire`), and the autonomous reader/loop (:mod:`dlm.agent`) -- moves
out of ``experiments/`` and INTO the model.  :class:`dlm.agent.Reader` owns
perceive -> acquire -> search -> induce -> close -> read, and ``run_loop`` repeats
that cycle over a sequence of sources, stopping on a named policy reason
(``saturated`` / ``max_rounds``) with the kernel as the only judge.  The web,
the search and the acquisition are still UNTRUSTED proposals -- the kernel
consumes every acquired fact like any other and re-checks what it concludes -- but
they are now the model's own senses, not the experiment's.  Experiments keep only
the GIVEN, domain-specific pieces (a reducer, bridge/gist rules, cue lexicons, a
signature builder) and the falsifier harnesses.  The measured north-star output
is unchanged (239 facts / 87 closure / 615 atoms / 42 certified sentences / level
N9).  v0.0055 adds RECURSIVE SELF-SUPERVISED LEARNING (:mod:`dlm.recursive`): the
model feeds its own kernel-certified output back as the next round's input.  Each
round closes the relation it currently has under two definitional level rules
(inherit + self-join) and reifies the certified extension as a new predicate, so
reachability is bootstrapped to arbitrary depth in O(log diameter) rounds with no
labels and the kernel as the only judge; a round that adds nothing is the
fixpoint and the model abstains.  It is NOT given the relational transitive rule --
a single composition provably cannot reach the closure, which is the falsifier
that recursion is required (``experiments/recursive``).  v0.0056 closes the loop
with SELF-EVALUATION and a WEAKNESS-TARGETED CURRICULUM (:mod:`dlm.ability`,
:mod:`dlm.curriculum`): the model reads its own ability off the kernel closure
(the deduction targets its rules PROMISE but cannot yet conclude), identifies the
missing premise only acquired knowledge can supply, asks the web for exactly that
premise, re-closes through the kernel, re-assesses, and stops on a named reason
(``saturated`` / ``no_actionable`` / ``acquire_empty`` / ``no_progress`` /
``max_rounds``).  Targets are DISCOVERED from the theory, not a fixed goal list;
improvement is scored at the TARGET level, so a scrambled fact improves nothing
and a removed web abstains.  ``Reader.assess`` / ``Reader.self_improve`` own it.
v0.0057 turns self-supervision on the model's OWN SOURCE (:mod:`dlm.selflearn`):
the model perceives its own call graph, INDUCES the governing composition law
from examples it generated by walking its own edges (no human supplies the
transitive rule), then feeds that law back through the kernel and reifies each
certified extension as the next relation -- recursively doubling the depth it can
span.  On its own 325-node graph one composition recovers 31% of the reachable
pairs; four recursive rounds recover 100% with zero false derivations -- a
measured gain in deductive power on facts it never observed.  It also GROWS its
hypothesis vocabulary (reifying certified concepts as new predicates so the next
round can quantify over them), which removes the fixed-alphabet plateau a
v0.0056-style loop hits -- a definitional, conservative extension reported
separately from the relational reach gain.  The model's induction is a small
generic rule space, not yet the open-ended induction of an LLM; the honest gap is
``experiments/selflearn``'s subject.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

__version__ = "0.0.57"
__all__ = [
    "Const", "Var", "Term", "Atom", "NegAtom", "Rule", "KnowledgeBase",
    "closure", "entails", "unify", "strata", "description_length",
    "Arg", "Signature", "type_errors", "fact_type_errors",
]


class Term:
    pass


@dataclass(frozen=True)
class Const(Term):
    name: str


@dataclass(frozen=True)
class Var(Term):
    name: str


@dataclass(frozen=True)
class Atom:
    pred: str
    args: Tuple[Term, ...] = ()

    def is_ground(self) -> bool:
        return all(isinstance(a, Const) for a in self.args)


@dataclass(frozen=True)
class NegAtom:
    """A negated body literal ``not atom`` (closed-world, stratified)."""
    atom: Atom


@dataclass(frozen=True)
class Rule:
    head: Atom
    body: Tuple[Atom, ...] = ()
    name: str = ""


@dataclass(frozen=True)
class Arg:
    """One typed, moded position of a predicate (an ILP-style signature slot).

    ``type``  the name of the required type.
    ``mode``  ``"in"`` (must be bound before use), ``"out"`` (may be produced)
              or ``"any"`` (neither required nor producing).
    """
    type: str
    mode: str = "any"

    def __post_init__(self):
        if self.mode not in ("in", "out", "any"):
            raise ValueError(f"unknown mode: {self.mode!r}")


@dataclass(frozen=True)
class Signature:
    """A GIVEN typed/moded signature for a predicate vocabulary (standard ILP).

    ``args``     predicate -> per-position :class:`Arg`.
    ``types``    type name -> the constants that inhabit it (empty = open; then
                 only the subtype relation, not membership, is checked).
    ``parents``  type name -> its supertypes (a small, transitive lattice).

    Types gate rule ADMISSION, never truth: a signature only *rejects* a theory
    that is ill-typed, structurally unsafe or not mode-anable.  It cannot make a
    sound rule unsound, and it asserts nothing by itself.
    """
    args: Dict[str, Tuple[Arg, ...]] = field(default_factory=dict)
    types: Dict[str, frozenset] = field(default_factory=dict)
    parents: Dict[str, Tuple[str, ...]] = field(default_factory=dict)

    def has(self, pred: str) -> bool:
        return pred in self.args

    def arity(self, pred: str) -> int:
        return len(self.args[pred])

    def ancestors(self, t: str) -> set:
        """``t`` plus every transitive supertype."""
        seen, stack = {t}, [t]
        while stack:
            for p in self.parents.get(stack.pop(), ()):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        return seen

    def compatible(self, a: str, b: str) -> bool:
        # Unifiable iff one type is a subtype of the other (disjoint branches
        # never meet).  A variable has exactly ONE type, so ``module`` and
        # ``symbol`` clash even though both sit under ``callable``.
        return a in self.ancestors(b) or b in self.ancestors(a)

    def constants(self, t: str) -> set:
        out: set = set()
        for c in self.ancestors(t):
            out |= set(self.types.get(c, ()))
        return out


def _vars(atom: Atom) -> set:
    return {t.name for t in atom.args if isinstance(t, Var)}


def type_errors(rule: Rule, sig: Signature) -> Tuple[str, ...]:
    """Every static reason ``rule`` is inadmissible under ``sig`` (empty = OK).

    Checks, in order: (a) known predicate + arity, (b) type soundness -- a
    variable has one type and a constant inhabits its slot's type, (c) range
    restriction -- every head/negated variable occurs in a POSITIVE body literal,
    and (d) mode anability -- every ``in`` position is bound by the head's own
    ``in`` positions or produced by some positive literal.  Anything it flags
    would otherwise be silently pruned at run time; here it is rejected up front.
    """
    errs: list = []
    atoms = [(rule.head, False)] + [(l, isinstance(l, NegAtom)) for l in rule.body]
    for lit, isneg in atoms:
        a = lit.atom if isneg else lit
        if a.pred not in sig.args:
            errs.append(f"unknown predicate {a.pred!r}")
            continue
        if len(a.args) != sig.arity(a.pred):
            errs.append(f"arity {a.pred}/{len(a.args)} != declared {sig.arity(a.pred)}")
            continue
        for term, arg in zip(a.args, sig.args[a.pred]):
            if isinstance(term, Const):
                consts = sig.constants(arg.type)
                if consts and term.name not in consts:
                    errs.append(f"constant {term.name!r} is not of type {arg.type}")
    vt: Dict[str, str] = {}
    for lit, isneg in atoms:
        a = lit.atom if isneg else lit
        if a.pred not in sig.args or len(a.args) != sig.arity(a.pred):
            continue
        for term, arg in zip(a.args, sig.args[a.pred]):
            if not isinstance(term, Var):
                continue
            prev = vt.get(term.name)
            if prev is None:
                vt[term.name] = arg.type
            elif not sig.compatible(prev, arg.type):
                errs.append(f"type clash on ?{term.name}: {prev} vs {arg.type}")
            elif prev in sig.ancestors(arg.type):
                vt[term.name] = arg.type  # keep the more specific type
    pos = [l for l in rule.body if isinstance(l, Atom)]
    pos_vars = set().union(*[_vars(l) for l in pos]) if pos else set()
    for v in _vars(rule.head):
        if v not in pos_vars:
            errs.append(f"unsafe: head variable ?{v} is bound by no positive body literal")
    for lit, isneg in atoms:
        if isneg:
            for v in _vars(lit.atom):
                if v not in pos_vars:
                    errs.append(f"unsafe: negated variable ?{v} is bound by no positive body literal")
    bound = set()
    for term, arg in zip(rule.head.args, sig.args[rule.head.pred]) \
            if rule.head.pred in sig.args else ():
        if isinstance(term, Var) and arg.mode == "in":
            bound.add(term.name)
        if isinstance(term, Const):
            bound.add("\0" + term.name)  # constants are always bound
    produced = {t.name for lit in pos if lit.pred in sig.args
                for term, arg in zip(lit.args, sig.args[lit.pred])
                if arg.mode in ("out", "any") for t in ([term] if isinstance(term, Var) else [])}
    produced |= {term.name for lit in pos for term in lit.args if isinstance(term, Const)}
    for lit in pos:
        if lit.pred not in sig.args or len(lit.args) != sig.arity(lit.pred):
            continue
        for term, arg in zip(lit.args, sig.args[lit.pred]):
            if arg.mode == "in" and isinstance(term, Var) and term.name not in bound and term.name not in produced:
                errs.append(f"mode: input ?{term.name} of {lit.pred} is never produced")
    return tuple(dict.fromkeys(errs))


def fact_type_errors(atom: Atom, sig: Signature) -> Tuple[str, ...]:
    """Static reasons a ground fact is ill-typed under ``sig`` (empty = OK)."""
    if atom.pred not in sig.args:
        return (f"unknown predicate {atom.pred!r}",)
    if len(atom.args) != sig.arity(atom.pred):
        return (f"arity {atom.pred}/{len(atom.args)} != declared {sig.arity(atom.pred)}",)
    errs: list = []
    for term, arg in zip(atom.args, sig.args[atom.pred]):
        if isinstance(term, Const):
            consts = sig.constants(arg.type)
            if consts and term.name not in consts:
                errs.append(f"constant {term.name!r} is not of type {arg.type}")
    return tuple(errs)


def _bind(pat: Term, ground: Term, s: Dict[str, Term]) -> bool:
    if isinstance(pat, Var):
        if pat.name in s:
            return s[pat.name] == ground
        s[pat.name] = ground
        return True
    return pat == ground


def unify(pattern: Atom, ground: Atom, s: Optional[Dict[str, Term]] = None):
    """Match a body pattern against a ground atom; return bindings or ``None``."""
    if pattern.pred != ground.pred or len(pattern.args) != len(ground.args):
        return None
    out = dict(s) if s else {}
    for p, g in zip(pattern.args, ground.args):
        if not _bind(p, g, out):
            return None
    return out


def _subst(atom: Atom, s: Dict[str, Term]) -> Atom:
    return Atom(atom.pred, tuple(s.get(t.name, t) if isinstance(t, Var) else t for t in atom.args))


@dataclass
class KnowledgeBase:
    facts: set = field(default_factory=set)
    rules: Tuple[Rule, ...] = ()

    def add_fact(self, a: Atom) -> None:
        self.facts.add(a)

    def add_facts(self, fs: Iterable[Atom]) -> None:
        self.facts.update(fs)

    def add_rule(self, r: Rule) -> None:
        self.rules = self.rules + (r,)

    def copy(self) -> "KnowledgeBase":
        return KnowledgeBase(set(self.facts), tuple(self.rules))


def _join(body: Tuple[Atom, ...], by_pred: dict, i: int = 0, s=None):
    if s is None:
        s = {}
    if i == len(body):
        yield s
        return
    for f in by_pred.get(body[i].pred, ()):
        ns = unify(body[i], f, s)
        if ns is not None:
            yield from _join(body, by_pred, i + 1, ns)


def _join_delta(body: Tuple[Atom, ...], by_pred: dict, delta_by: dict, di: int,
                i: int = 0, s=None):
    """Join ``body`` where literal ``di`` ranges over the delta facts only."""
    if s is None:
        s = {}
    if i == len(body):
        yield s
        return
    src = delta_by if i == di else by_pred
    for f in src.get(body[i].pred, ()):
        ns = unify(body[i], f, s)
        if ns is not None:
            yield from _join_delta(body, by_pred, delta_by, di, i + 1, ns)


def closure(kb: KnowledgeBase, sig: Optional[Signature] = None) -> set:
    """Least fixpoint of the rules over the facts (the kernel asserts this).

    Pure Horn rules use semi-naive evaluation: the first round joins over all
    facts; every later round only re-joins using the facts derived in the
    previous round, so a derivation is never recomputed.  The predicate index is
    maintained incrementally instead of being rebuilt each round.  Identical
    result to the naive fixpoint; see tests/test_closure_perf.py for the
    equivalence check.

    If any rule body contains a :class:`NegAtom`, evaluation is *stratified*
    (see :func:`strata`): negation is sound only when the negated predicate is
    defined in a strictly lower stratum, so the facts it ranges over are already
    complete.  A negative dependency cycle is rejected with ``ValueError``.

    If a typed/moded :class:`Signature` is supplied, the facts and rules are
    checked *statically* first (see :func:`type_errors`) and an ill-typed theory
    is rejected with ``TypeError`` before any derivation happens -- truth can
    never be polluted by a rule that typing makes inadmissible.
    """
    if sig is not None:
        bad = [f"fact {a.pred}: {e}" for a in kb.facts
               for e in fact_type_errors(a, sig)]
        for r in kb.rules:
            bad += [f"rule {r.name or r.head.pred}: {e}" for e in type_errors(r, sig)]
        if bad:
            raise TypeError("ill-typed theory: " + "; ".join(bad))
    for rule in kb.rules:
        for lit in rule.body:
            if isinstance(lit, NegAtom):
                return _stratified_closure(kb)
    return _horn_closure(kb)


def _horn_closure(kb: KnowledgeBase) -> set:
    facts = set(kb.facts)
    by_pred: dict = {}
    for f in facts:
        by_pred.setdefault(f.pred, []).append(f)

    delta = set(facts)
    first = True
    while delta:
        delta_by: dict = {}
        for f in delta:
            delta_by.setdefault(f.pred, []).append(f)
        new: set = set()
        for rule in kb.rules:
            body = rule.body
            if not body:
                h = rule.head
                if h.is_ground() and h not in facts and h not in new:
                    new.add(h)
                continue
            if first:
                for s in _join(body, by_pred):
                    h = _subst(rule.head, s)
                    if h.is_ground() and h not in facts and h not in new:
                        new.add(h)
            else:
                for di in range(len(body)):
                    for s in _join_delta(body, by_pred, delta_by, di):
                        h = _subst(rule.head, s)
                        if h.is_ground() and h not in facts and h not in new:
                            new.add(h)
        first = False
        if not new:
            break
        for f in new:
            facts.add(f)
            by_pred.setdefault(f.pred, []).append(f)
        delta = new
    return facts


def entails(kb: KnowledgeBase, atom: Atom) -> bool:
    return atom in closure(kb)


def strata(kb: KnowledgeBase) -> Dict[str, int]:
    """Assign each predicate a stratum so negation is well-founded.

    ``stratum(head) = max(stratum(positive body preds), 1 + stratum(negated
    body preds))``.  A rule that depends negatively on a predicate of its own
    stratum (a negative cycle) makes this divergence; it is detected and raises
    ``ValueError`` -- the kernel refuses to guess a non-stratified theory.
    """
    preds = set()
    for r in kb.rules:
        preds.add(r.head.pred)
        for lit in r.body:
            preds.add(lit.pred if isinstance(lit, Atom) else lit.atom.pred)
    st = {p: 0 for p in preds}
    for _ in range(len(preds) + 2):
        changed = False
        for r in kb.rules:
            req = st[r.head.pred]
            for lit in r.body:
                if isinstance(lit, Atom):
                    req = max(req, st[lit.pred])
                else:
                    req = max(req, st[lit.atom.pred] + 1)
            if req > st[r.head.pred]:
                st[r.head.pred] = req
                changed = True
        if not changed:
            return st
    raise ValueError("not stratifiable: negative dependency cycle")


def _eval_rule(rule: Rule, by_pred: dict, known: set):
    """Yield ground heads; positive literals are joined, negations are checked.

    Safety: a negated literal whose atom is not ground under the positive
    bindings cannot be concluded, so the derivation is pruned (never guessed).
    """
    pos = tuple(l for l in rule.body if isinstance(l, Atom))
    neg = tuple(l for l in rule.body if isinstance(l, NegAtom))
    for s in _join(pos, by_pred):
        h = _subst(rule.head, s)
        if not h.is_ground():
            continue
        for lit in neg:
            ga = _subst(lit.atom, s)
            if not ga.is_ground() or ga in known:
                break
        else:
            yield h


def _stratified_closure(kb: KnowledgeBase) -> set:
    st = strata(kb)
    facts = set(kb.facts)
    by_pred: dict = {}
    for f in facts:
        by_pred.setdefault(f.pred, []).append(f)
    for k in sorted(set(st.values())):
        rules_k = [r for r in kb.rules if st[r.head.pred] == k]
        changed = True
        while changed:
            changed = False
            for r in rules_k:
                cands = _eval_rule(r, by_pred, facts) if r.body else ((r.head,)
                        if r.head.is_ground() else ())
                for h in cands:
                    if h not in facts:
                        facts.add(h)
                        by_pred.setdefault(h.pred, []).append(h)
                        changed = True
    return facts


def description_length(rules: Iterable[Rule]) -> int:
    """Each rule costs its head plus each body literal (facts are free input)."""
    return sum(1 + len(r.body) for r in rules)