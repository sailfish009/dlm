"""DLM v0.0001 — rule induction (the Cyc difference).

Cyc hand-authors its rules. DLM induces them: from a background KB plus
positive/negative ground examples it searches for the shortest Horn rule that
covers all positives and no negatives. This is a bounded, classical
inductive-logic-programming step (anti-unification for the head, bounded body
search, forward-chaining for the coverage test).

Scope of v0.0001: binary/unary background predicates, bodies up to
``max_body`` literals, ``n_exist`` existential variables. Full ILP (recursive
invention, predicate invention) is out of scope and is listed in work.txt.
"""
from __future__ import annotations

from itertools import combinations, product
from typing import Dict, Iterable, List, Sequence, Set, Tuple

from .deduce import Engine
from .kb import KnowledgeBase
from .rules import Rule
from .terms import Atom, Const, Term, Var


def _lgg_term(a: Term, b: Term, mapping: Dict[Tuple[Term, Term], Var]) -> Term:
    if a == b:
        return a
    key = (a, b)
    if key not in mapping:
        mapping[key] = Var(f"G{len(mapping)}")
    return mapping[key]


def lgg_atoms(examples: Sequence[Atom]) -> Atom:
    """Least general generalization (anti-unification) of example atoms."""
    if not examples:
        raise ValueError("no examples")
    head = examples[0]
    mapping: Dict[Tuple[Term, Term], Var] = {}
    for a in examples[1:]:
        if a.pred != head.pred or len(a.args) != len(head.args):
            raise ValueError("examples must share predicate and arity")
        head = Atom(
            head.pred,
            tuple(_lgg_term(x, y, mapping) for x, y in zip(head.args, a.args)),
        )
    return head


def _variate(atom_: Atom, prefix: str = "H") -> Atom:
    """Replace every constant with a fresh variable (most general single head)."""
    seen: Dict[Term, Var] = {}
    args: List[Term] = []
    for a in atom_.args:
        if isinstance(a, Var):
            args.append(a)
            continue
        if a not in seen:
            seen[a] = Var(f"{prefix}{len(seen)}")
        args.append(seen[a])
    return Atom(atom_.pred, tuple(args))


def _literal_space(
    kb: KnowledgeBase, target_pred: str, target_arity: int, variables: Sequence[Var]
) -> List[Atom]:
    """All feasible literals over ``variables`` using background predicates."""
    preds: Set[Tuple[str, int]] = set()
    for p in kb.predicates:
        for f in kb.facts_for(p):
            preds.add((f.pred, len(f.args)))
        for r in kb.rules_for(p):
            preds.add((r.head.pred, len(r.head.args)))
    preds.add((target_pred, target_arity))
    space: List[Atom] = []
    for pred, arity in sorted(preds):
        if arity == 0 or arity > 3:
            continue
        for combo in product(variables, repeat=arity):
            space.append(Atom(pred, tuple(combo)))
    return space


def _covers(
    kb: KnowledgeBase, rule_: Rule, positives: Set[Atom], negatives: Set[Atom]
) -> bool:
    trial = KnowledgeBase()
    for f in kb.facts():
        trial.add_fact(f)
    for r in kb.rules():
        trial.add_rule(r)
    trial.add_rule(rule_)
    closure = Engine(trial).forward_chain()
    if not positives <= closure:
        return False
    if negatives & closure:
        return False
    return True


def induce_rules(
    kb: KnowledgeBase,
    positives: Iterable[Atom],
    negatives: Iterable[Atom] = (),
    max_body: int = 2,
    n_exist: int = 1,
) -> List[Rule]:
    """Induce shortest consistent Horn rules, grouped by head predicate."""
    pos_by_pred: Dict[str, List[Atom]] = {}
    for p in positives:
        pos_by_pred.setdefault(p.pred, []).append(p)
    neg_set = set(negatives)
    all_pos = {p for plist in pos_by_pred.values() for p in plist}

    results: List[Rule] = []
    for pred, exs in pos_by_pred.items():
        head = lgg_atoms(exs) if len(exs) > 1 else _variate(exs[0])
        head_var_names = list(dict.fromkeys(head.vars()))
        variables: List[Var] = [Var(v) for v in head_var_names]
        variables += [Var(f"E{i}") for i in range(n_exist)]
        literals = _literal_space(kb, pred, len(head.args), variables)
        # keep one literal per canonical variable pattern
        seen_lit: Set[Tuple[str, Tuple[str, ...]]] = set()
        uniq: List[Atom] = []
        for lit in literals:
            key = (lit.pred, tuple(str(a) for a in lit.args))
            if key not in seen_lit:
                seen_lit.add(key)
                uniq.append(lit)

        found: List[Rule] = []
        for length in range(1, max_body + 1):
            for combo in combinations(uniq, length):
                body_vars = {a.name for lit in combo for a in lit.args if isinstance(a, Var)}
                if not set(head_var_names) <= body_vars:
                    continue  # head variables must be bound (Datalog safety)
                cand = Rule(head, tuple(combo), name=f"ind_{pred}_{length}")
                if _covers(kb, cand, set(exs), neg_set):
                    found.append(cand)
            if found:
                break  # shortest bodies only
        # de-duplicate by canonical body
        dedup: Dict[str, Rule] = {}
        for r in found:
            key = "|".join(sorted(str(b) for b in r.body))
            dedup.setdefault(key, r)
        results.extend(dedup.values())
    return results