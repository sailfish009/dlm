"""Small trusted Horn projection and closure kernel for typed IR forms."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .ir import (Form, field, sorted_forms, validate_atom, validate_rule)


@dataclass(frozen=True, order=True)
class Atom:
    pred: str
    args: tuple[str, ...] = ()


@dataclass(frozen=True)
class Rule:
    head: Atom
    body: tuple[Atom, ...]


def is_var(term: str) -> bool:
    return term.startswith("?")


def atom_to_ir(atom: Atom) -> Form:
    return ("atom", atom.pred,
            *(("var", x[1:]) if is_var(x) else ("const", x) for x in atom.args))


def atom_from_ir(form: Form) -> Atom:
    validate_atom(form)
    assert isinstance(form, tuple)
    args = tuple(("?" + t[1]) if t[0] == "var" else t[1] for t in form[2:])
    return Atom(form[1], args)


def rule_to_ir(rule: Rule) -> Form:
    return ("rule", atom_to_ir(rule.head),
            ("body", *(atom_to_ir(atom) for atom in rule.body)))


def rule_from_ir(form: Form) -> Rule:
    validate_rule(form)
    assert isinstance(form, tuple) and isinstance(form[2], tuple)
    return Rule(atom_from_ir(form[1]), tuple(atom_from_ir(a) for a in form[2][1:]))


def safe(rule: Rule) -> bool:
    head_vars = {x for x in rule.head.args if is_var(x)}
    body_vars = {x for atom in rule.body for x in atom.args if is_var(x)}
    return bool(rule.body) and head_vars <= body_vars


def _match(pattern: Atom, fact: Atom, env: Mapping[str, str] | None = None):
    if pattern.pred != fact.pred or len(pattern.args) != len(fact.args):
        return None
    result = dict(env or {})
    for left, right in zip(pattern.args, fact.args):
        if is_var(left):
            if left in result and result[left] != right:
                return None
            result[left] = right
        elif left != right:
            return None
    return result


def _substitute(atom: Atom, env: Mapping[str, str]) -> Atom:
    return Atom(atom.pred, tuple(env.get(x, x) for x in atom.args))


def closure(facts: Iterable[Atom], rules: Iterable[Rule] = ()) -> frozenset[Atom]:
    """Compute a least fixpoint with a semi-naive delta agenda and predicate index."""
    known = set(facts)
    if any(is_var(x) for atom in known for x in atom.args):
        raise ValueError("facts must be ground")
    rules = tuple(rules)
    if any(not safe(rule) for rule in rules):
        raise ValueError("unsafe rule")
    by_pred: dict[str, set[Atom]] = {}
    for atom in known:
        by_pred.setdefault(atom.pred, set()).add(atom)
    delta = set(known)
    while delta:
        delta_by_pred: dict[str, set[Atom]] = {}
        for atom in delta:
            delta_by_pred.setdefault(atom.pred, set()).add(atom)
        produced: set[Atom] = set()
        for rule in rules:
            # Every new derivation must use at least one fact from this frontier.
            for pivot, literal in enumerate(rule.body):
                if literal.pred not in delta_by_pred:
                    continue
                envs = [dict()]
                for index, body_literal in enumerate(rule.body):
                    source = (delta_by_pred if index == pivot else by_pred)
                    envs = [match for env in envs
                            for fact in source.get(body_literal.pred, ())
                            if (match := _match(body_literal, fact, env)) is not None]
                    if not envs:
                        break
                for env in envs:
                    atom = _substitute(rule.head, env)
                    if not any(is_var(x) for x in atom.args) and atom not in known:
                        produced.add(atom)
        delta = produced
        known.update(delta)
        for atom in delta:
            by_pred.setdefault(atom.pred, set()).add(atom)
    return frozenset(known)


def prove(facts: Iterable[Atom], rules: Iterable[Rule], target: Atom) -> Form | None:
    """Construct one deterministic proof tree for a ground target."""
    facts = frozenset(facts)
    rules = tuple(rules)
    if any(not safe(rule) for rule in rules):
        raise ValueError("unsafe rule")
    proofs: dict[Atom, Form] = {
        atom: ("proof", ("conclusion", atom_to_ir(atom)), ("kind", "fact"),
               ("rule-ref", ("none",)), ("premises",))
        for atom in sorted(facts)
    }
    if target in proofs:
        return proofs[target]
    changed = True
    while changed:
        changed = False
        by_pred: dict[str, list[Atom]] = {}
        for atom in proofs:
            by_pred.setdefault(atom.pred, []).append(atom)
        for values in by_pred.values():
            values.sort()
        for rule in sorted(rules, key=lambda r: repr(rule_to_ir(r))):
            states = [(dict(), tuple())]
            for literal in rule.body:
                next_states = []
                for env, premises in states:
                    for fact in by_pred.get(literal.pred, ()):
                        match = _match(literal, fact, env)
                        if match is not None:
                            next_states.append((match, premises + (proofs[fact],)))
                states = next_states
            for env, premises in states:
                conclusion = _substitute(rule.head, env)
                if any(is_var(x) for x in conclusion.args) or conclusion in proofs:
                    continue
                proofs[conclusion] = (
                    "proof", ("conclusion", atom_to_ir(conclusion)), ("kind", "rule"),
                    ("rule-ref", rule_to_ir(rule)), ("premises", *premises))
                changed = True
                if conclusion == target:
                    return proofs[conclusion]
    return None


def verify_proof(proof: Form, facts: Iterable[Atom], rules: Iterable[Rule]) -> bool:
    """Reject forged rules: every rule witness must belong to the supplied theory."""
    facts, rules = frozenset(facts), tuple(rules)

    def verify(node: Form) -> Atom | None:
        if not isinstance(node, tuple) or node[0] != "proof":
            return None
        try:
            conclusion = atom_from_ir(field(node, "conclusion")[1])
            kind = field(node, "kind")[1]
            rule_ref = field(node, "rule-ref")[1]
            premises = field(node, "premises")[1:]
        except (ValueError, IndexError, TypeError):
            return None
        if kind == "fact":
            return conclusion if rule_ref == ("none",) and not premises and conclusion in facts else None
        if kind != "rule":
            return None
        try:
            rule = rule_from_ir(rule_ref)
        except (ValueError, TypeError):
            return None
        if rule not in rules or len(premises) != len(rule.body):
            return None
        env: dict[str, str] = {}
        for literal, premise in zip(rule.body, premises):
            premise_atom = verify(premise)
            if premise_atom is None:
                return None
            matched = _match(literal, premise_atom, env)
            if matched is None:
                return None
            env = matched
        return conclusion if _substitute(rule.head, env) == conclusion else None

    return verify(proof) is not None


def episode_data(episode: Form) -> dict[str, object]:
    return {
        "source": field(episode, "source")[1],
        "role": field(episode, "role")[1],
        "facts": frozenset(atom_from_ir(x) for x in field(episode, "facts")[1:]),
        "confirmed": frozenset(atom_from_ir(x) for x in field(episode, "confirmed")[1:]),
        "contradicted": frozenset(atom_from_ir(x) for x in field(episode, "contradicted")[1:]),
        "unknown": frozenset(atom_from_ir(x) for x in field(episode, "unknown")[1:]),
    }


def episode_ir(source: str, facts: Iterable[Atom], confirmed: Iterable[Atom] = (),
               contradicted: Iterable[Atom] = (), unknown: Iterable[Atom] = (),
               role: str = "train") -> Form:
    return ("episode", ("source", source), ("role", role),
            ("facts", *sorted_forms(atom_to_ir(x) for x in facts)),
            ("confirmed", *sorted_forms(atom_to_ir(x) for x in confirmed)),
            ("contradicted", *sorted_forms(atom_to_ir(x) for x in contradicted)),
            ("unknown", *sorted_forms(atom_to_ir(x) for x in unknown)))


def state_rules(state: Form) -> tuple[Rule, ...]:
    theory = field(state, "theory")
    return tuple(rule_from_ir(x) for tier in ("ground", "experience")
                 for x in field(theory, tier)[1:])


def state_tier(state: Form, tier: str) -> tuple[Rule, ...]:
    return tuple(rule_from_ir(x) for x in field(field(state, "theory"), tier)[1:])


def state_prove(state: Form, atom_form: Form) -> Form:
    target = atom_from_ir(atom_form)
    rules = state_rules(state)
    for episode in field(state, "evidence")[1:]:
        data = episode_data(episode)
        proof = prove(data["facts"], rules, target)
        if proof is not None and verify_proof(proof, data["facts"], rules):
            return ("proof-result", ("status", "proved"),
                    ("source", data["source"]), ("proof", proof))
    return ("proof-result", ("status", "unknown"), ("source", ""),
            ("proof", ("noul",)))


def query(state: Form, atom_form: Form) -> Form:
    target = atom_from_ir(atom_form)
    proofs = []
    rules = state_rules(state)
    for episode in field(state, "evidence")[1:]:
        data = episode_data(episode)
        if target in closure(data["facts"], rules):
            proofs.append(("entailed-in", data["source"]))
    return (("query-result", ("atom", atom_form), ("status", "entailed"),
             ("support", *proofs)) if proofs else
            ("query-result", ("atom", atom_form), ("status", "unknown"),
             ("support",)))
