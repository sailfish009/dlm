"""DLM v0.0048 -- label-free abstraction (untrusted, kernel-certified).

The LLM fits data to an external label ``y``.  The deductive model has **no
label**: its target is its own closure.  Learning is therefore *abstraction* --
factoring recurring structure out of a theory into a shorter theory with the
**same** closure.  The kernel proves the equality; nothing here asserts.

Two conservative operators:

* ``invent``  -- first-order subgoal abstraction: a recurring body conjunction
                becomes a new predicate with a definitional rule;
* ``mined_subforms`` -- syntactic compression: a recurring form pattern (the IR
                tree, see :mod:`dlm.ir`) is named for a macro library.

An abstraction is accepted only when ``closure_preserved`` holds **and** the
form-tree description length strictly shrinks.  Conservative abstraction cannot
derive *more* atoms; under a fixed inference budget (``closure_budget``) it can
derive the same atoms in fewer steps, which is the falsifiable claim.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from . import Atom, KnowledgeBase, Rule, Var, closure
from .ir import pattern_key
from .lisp import atom_to_form, dump, is_var, rule_to_form

__all__ = [
    "theory_dl", "closure_preserved", "closure_budget", "common_body_patterns",
    "mined_subforms", "abstract_theory", "Abstraction", "AbstractResult",
]


# --------------------------------------------------------------------------- #
# description length on the IR (the form tree), not the flat rule
# --------------------------------------------------------------------------- #
def _nodes(form: object) -> int:
    if isinstance(form, tuple):
        return 1 + sum(_nodes(x) for x in form)
    return 1


def theory_dl(rules: Iterable[Rule]) -> int:
    """Total form-tree node count of a rule theory (the IR description length)."""
    return sum(_nodes(rule_to_form(r)) for r in rules)


# --------------------------------------------------------------------------- #
# certification
# --------------------------------------------------------------------------- #
def closure_preserved(facts: Iterable[Atom], old: Sequence[Rule],
                      new: Sequence[Rule]) -> bool:
    """The kernel re-derives the SAME entailment over the ORIGINAL signature.

    An invented predicate legitimately adds atoms of its own; a conservative
    (definitional) extension must not change any atom over the original
    predicates.  Comparing full closures would reject every useful abstraction.
    """
    facts = set(facts)
    vocab = {a.pred for a in facts} | {r.head.pred for r in old}
    a = {x for x in closure(KnowledgeBase(facts, tuple(old))) if x.pred in vocab}
    b = {x for x in closure(KnowledgeBase(facts, tuple(new))) if x.pred in vocab}
    return a == b


def closure_budget(kb: KnowledgeBase, max_work: int) -> set:
    """Forward chaining stopped after ``max_work`` join attempts (unifications).

    A *rule application* budget is the wrong lens: a baseline rule that joins
    four body literals is one application, and a definitional extension adds a
    layer, so abstraction looks slower.  Counting **join work** exposes the
    saving: a shared subgoal is derived once and reused by every rule, instead
    of re-joined per rule.  Returns the facts derived within the work budget.
    """
    facts = set(kb.facts)
    counter = [0]
    by_pred: dict = {}
    for f in facts:
        by_pred.setdefault(f.pred, []).append(f)
    changed = True
    while changed and counter[0] < max_work:
        changed = False
        for rule in kb.rules:
            for s in _join(rule.body, by_pred, 0, {}, counter, max_work):
                h = _subst(rule.head, s)
                if not h.is_ground() or h in facts:
                    continue
                facts.add(h)
                by_pred.setdefault(h.pred, []).append(h)
                changed = True
            if counter[0] >= max_work:
                break
    return facts


def _join(body, by_pred, i=0, s=None, counter=None, limit=None):
    from . import unify
    if s is None:
        s = {}
    if counter is None:
        counter = [0]
    if i == len(body):
        yield s
        return
    for f in tuple(by_pred.get(body[i].pred, ())):
        counter[0] += 1
        if limit is not None and counter[0] > limit:
            return
        ns = unify(body[i], f, s)
        if ns is not None:
            yield from _join(body, by_pred, i + 1, ns, counter, limit)


def _subst(atom: Atom, s: Dict) -> Atom:
    return Atom(atom.pred, tuple(s.get(t.name, t) if isinstance(t, Var) else t for t in atom.args))


# --------------------------------------------------------------------------- #
# pattern mining (up to variable renaming) on the canonical form tree
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Abstraction:
    kind: str
    name: str
    definition: Rule
    support: int
    uses: int
    dl_before: int
    dl_after: int


@dataclass(frozen=True)
class AbstractResult:
    theory: Tuple[Rule, ...]
    abstractions: Tuple[Abstraction, ...]
    dl_before: int
    dl_after: int
    facts: frozenset

    @property
    def compression_gain(self) -> int:
        return self.dl_before - self.dl_after


def _canon(atoms: Sequence[Atom]):
    """Canonicalise a body conjunction up to variable renaming.

    Returns ``(key, converted, canon_to_orig)`` where ``key`` is renaming
    invariant, ``converted`` uses ``?V0..`` and ``canon_to_orig`` maps a
    canonical variable name back to this occurrence's original term.
    """
    to_canon: Dict[str, Var] = {}
    canon_to_orig: Dict[str, object] = {}

    def cv(t):
        if not is_var(t.name):
            return t
        c = to_canon.get(t.name)
        if c is None:
            c = Var(f"?V{len(to_canon)}")
            to_canon[t.name] = c
            canon_to_orig[c.name] = t
        return c

    converted = tuple(Atom(a.pred, tuple(cv(t) for t in a.args)) for a in atoms)
    key = tuple(sorted(dump(atom_to_form(a)) for a in converted))
    return key, converted, canon_to_orig


def common_body_patterns(rules: Sequence[Rule], *, min_support: int = 2,
                         max_pattern: int = 4) -> Dict[tuple, list]:
    """Body conjunctions (size 2..``max_pattern``) shared by >= ``min_support`` rules."""
    groups: Dict[tuple, list] = {}
    for ri, r in enumerate(rules):
        seen = set()
        for size in range(2, max_pattern + 1):
            if size > len(r.body):
                break
            for pos in itertools.combinations(range(len(r.body)), size):
                atoms = tuple(r.body[i] for i in pos)
                key, converted, c2o = _canon(atoms)
                if key in seen:
                    continue
                seen.add(key)
                groups.setdefault(key, []).append((ri, pos, converted, c2o))
    return {k: v for k, v in groups.items()
            if len({ri for ri, *_ in v}) >= min_support}


def mined_subforms(forms: Sequence[object], *, min_support: int = 2,
                   max_size: int = 4) -> List[Tuple[str, int]]:
    """Recurring sub-forms of a corpus, by renaming-invariant key (macro library)."""
    counts: Dict[str, int] = {}
    for f in forms:
        local = set()

        def walk(x):
            if isinstance(x, tuple):
                if 2 <= _nodes(x) <= max_size:
                    local.add(pattern_key(x))
                for y in x[1:]:
                    walk(y)

        walk(f)
        for k in local:
            counts[k] = counts.get(k, 0) + 1
    return sorted(((k, n) for k, n in counts.items() if n >= min_support),
                  key=lambda kn: (-kn[1], kn[0]))


# --------------------------------------------------------------------------- #
# predicate invention
# --------------------------------------------------------------------------- #
def _vocab(rules: Sequence[Rule]) -> set:
    return ({r.head.pred for r in rules}
            | {b.pred for r in rules for b in r.body})


def _occ_interface(rule: Rule, pos: tuple, c2o: Dict[str, object],
                   basis_vars: Tuple[Var, ...]) -> Tuple[str, ...]:
    """Canonical vars of the pattern that also occur OUTSIDE it (head or rest)."""
    drop = set(pos)
    outside = {t.name for a in (rule.head,) + tuple(
        x for i, x in enumerate(rule.body) if i not in drop)
        for t in a.args if isinstance(t, Var)}
    return tuple(v.name for v in basis_vars
                 if isinstance(c2o.get(v.name), Var) and c2o[v.name].name in outside)


def _invent(rules: Sequence[Rule], occs: list, name: str):
    """Fold the pattern into a new predicate defined over its interface variables.

    The definition quantifies the pattern's *internal* variables existentially;
    only variables shared with the head / other body atoms become argument
    positions, so the rewrite is a conservative definitional extension.
    """
    basis = occs[0][2]                          # canonical definition body
    basis_vars = tuple(dict.fromkeys(v for a in basis for v in a.args
                                     if isinstance(v, Var)))
    chosen: Dict[int, tuple] = {}
    for ri, pos, _basis, c2o in occs:
        chosen.setdefault(ri, (pos, c2o))
    # definition head = union of interfaces, in first-appearance order
    head_names: List[str] = []
    for ri, (pos, c2o) in chosen.items():
        for n in _occ_interface(rules[ri], pos, c2o, basis_vars):
            if n not in head_names:
                head_names.append(n)
    head_vars = tuple(Var(n) for n in head_names)
    definition = Rule(Atom(name, head_vars), basis, name=name)

    out: List[Rule] = []
    for ri, r in enumerate(rules):
        if ri not in chosen:
            out.append(r)
            continue
        pos, c2o = chosen[ri]
        iface = set(_occ_interface(r, pos, c2o, basis_vars))
        args: List[object] = []
        fresh = 0
        for n in head_names:
            term = c2o.get(n)
            if n in iface and isinstance(term, Var):
                args.append(term)
            else:
                args.append(Var(f"?E{fresh}_{ri}"))
                fresh += 1
        body = tuple(a for i, a in enumerate(r.body) if i not in set(pos))
        out.append(Rule(r.head, body + (Atom(name, tuple(args)),), r.name))
    # the definition must precede its uses so one pass can fold then reuse it
    return [definition] + out, definition


def abstract_theory(rules: Sequence[Rule], facts: Iterable[Atom], *,
                    max_rounds: int = 8, min_support: int = 2,
                    max_pattern: int = 4) -> AbstractResult:
    """Greedily fold recurring body patterns into invented predicates.

    Each round admits the candidate with the lowest resulting DL that the kernel
    certifies preserves the closure; stops when none shrinks DL.
    """
    current = list(rules)
    facts = frozenset(facts)
    dl0 = theory_dl(current)
    accepted: List[Abstraction] = []
    while len(accepted) < max_rounds:
        groups = common_body_patterns(current, min_support=min_support,
                                      max_pattern=max_pattern)
        best = None
        for key in sorted(groups):
            occs = groups[key]
            name = f"inv{len(accepted)}"
            while name in _vocab(current) | {a.pred for a in facts}:
                name += "_"
            cand, definition = _invent(current, occs, name)
            dl = theory_dl(cand)
            before = theory_dl(current)
            if dl >= before or not closure_preserved(facts, current, cand):
                continue
            uses = sum(1 for r in cand if any(b.pred == name for b in r.body))
            item = (dl, name, cand,
                    Abstraction("invent", name, definition,
                                len({ri for ri, *_ in occs}), uses, before, dl))
            if best is None or (item[0], item[1]) < (best[0], best[1]):
                best = item
        if best is None:
            break
        accepted.append(best[3])
        current = best[2]
    return AbstractResult(tuple(current), tuple(accepted), dl0,
                          theory_dl(current), facts)