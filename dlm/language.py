"""Embedded TreeLisp rule programs: persisted code that composes logic candidates."""
from __future__ import annotations

from itertools import product
from typing import Iterable, Sequence

from .ir import Form, canonical_json, field, replace_field, validate_rule
from .kernel import Atom, episode_data, rule_from_ir, safe


def _template(name: str, head: Form, *body: Form) -> Form:
    return ("program", name, ("rule-template", head, ("body", *body)))


def default_language() -> Form:
    """Fixed code library. It is model state, but it has no assertion capability."""
    x, y, z = ("var", "x"), ("var", "y"), ("var", "z")
    programs = (
        _template("unary-project", ("atom", "$H", x), ("atom", "$P", x)),
        _template("unary-from-binary", ("atom", "$H", x), ("atom", "$P", x, y)),
        _template("binary-copy", ("atom", "$H", x, z), ("atom", "$P", x, z)),
        _template("binary-inverse", ("atom", "$H", x, z), ("atom", "$P", z, x)),
        _template("binary-chain", ("atom", "$H", x, z),
                  ("atom", "$P", x, y), ("atom", "$Q", y, z)),
        _template("binary-join-right", ("atom", "$H", x, z),
                  ("atom", "$P", x, y), ("atom", "$Q", z, y)),
        _template("binary-join-left", ("atom", "$H", x, z),
                  ("atom", "$P", y, x), ("atom", "$Q", y, z)),
        _template("binary-common-target", ("atom", "$H", x, z),
                  ("atom", "$P", y, x), ("atom", "$Q", z, y)),
    )
    return (
        "language",
        ("stdlib", ("primitive", "match"), ("primitive", "join"),
         ("primitive", "compose"), ("primitive", "emit-candidate")),
        ("programs", *programs),
        ("controller", ("pipeline", "retract", "run-programs", "rank",
                        "kernel-test", "contrast", "admit", "record")),
        ("program-stats", *(("program-stat", program[1], 0, 0)
                             for program in programs)),
    )


def validate_program(program: Form) -> None:
    if not isinstance(program, tuple) or len(program) != 3 or program[0] != "program":
        raise ValueError("expected (program NAME (rule-template ...))")
    if not isinstance(program[1], str) or not program[1]:
        raise ValueError("program name must be a non-empty string")
    template = program[2]
    if not isinstance(template, tuple) or len(template) != 3 or template[0] != "rule-template":
        raise ValueError("program must contain one rule-template")
    # Meta predicates are legal only in code templates, never emitted rules.
    if not isinstance(template[1], tuple) or template[1][0] != "atom":
        raise ValueError("template head must be an atom")
    if not isinstance(template[2], tuple) or template[2][0] != "body" or len(template[2]) < 2:
        raise ValueError("template body must be non-empty")


def validate_language(language: Form) -> None:
    if not isinstance(language, tuple) or language[0] != "language":
        raise ValueError("expected embedded language")
    field(language, "stdlib")
    programs = field(language, "programs")
    names = []
    for program in programs[1:]:
        validate_program(program)
        names.append(program[1])
    if len(names) != len(set(names)):
        raise ValueError("TreeLisp program names must be unique")
    stats = field(language, "program-stats")
    stat_names = set()
    for stat in stats[1:]:
        if (not isinstance(stat, tuple) or len(stat) != 4 or stat[0] != "program-stat"
                or not isinstance(stat[1], str)
                or not isinstance(stat[2], int) or isinstance(stat[2], bool)
                or not isinstance(stat[3], int) or isinstance(stat[3], bool)
                or stat[2] < 0 or stat[3] < 0 or stat[3] > stat[2]):
            raise ValueError("invalid program stat")
        stat_names.add(stat[1])
    if stat_names != set(names):
        raise ValueError("program stats must cover exactly the programs")
    controller = field(language, "controller")
    pipeline = field(controller, "pipeline")
    required = ("retract", "run-programs", "rank", "kernel-test", "contrast",
                "admit", "record")
    if tuple(pipeline[1:]) != required:
        raise ValueError("learning controller pipeline is incomplete or reordered")


def _signatures(atoms: Iterable[Atom]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted({(atom.pred, len(atom.args)) for atom in atoms if atom.args}))


def _schemas(state: Form):
    episodes = field(state, "evidence")[1:]
    train = tuple(e for e in episodes if episode_data(e)["role"] == "train") or episodes
    facts = {a for episode in train for a in episode_data(episode)["facts"]}
    goals = {a for episode in train for key in ("confirmed", "contradicted")
             for a in episode_data(episode)[key]}
    return _signatures(facts | goals), _signatures(goals)


def _meta_constraints(template: Form):
    head_atom, body = template[1], template[2]
    constraints: dict[str, list[tuple[str, int]]] = {}
    if isinstance(head_atom[1], str) and head_atom[1].startswith("$"):
        constraints.setdefault(head_atom[1], []).append(("head", len(head_atom) - 2))
    for atom in body[1:]:
        if isinstance(atom[1], str) and atom[1].startswith("$"):
            constraints.setdefault(atom[1], []).append(("body", len(atom) - 2))
    return constraints


def _replace_meta(form: Form, bindings: dict[str, str]) -> Form:
    if not isinstance(form, tuple):
        return form
    if form[0] == "atom" and form[1] in bindings:
        return ("atom", bindings[form[1]], *form[2:])
    return tuple(_replace_meta(x, bindings) for x in form)


def execute_programs(state: Form) -> tuple[Form, ...]:
    """Interpret persisted rule-template programs against current IR schemas."""
    language = field(state, "language")
    validate_language(language)
    body_sigs, head_sigs = _schemas(state)
    emitted: set[Form] = set()
    for program in field(language, "programs")[1:]:
        template = program[2]
        constraints = _meta_constraints(template)
        metas = sorted(constraints)
        domains = []
        for meta in metas:
            allowed: set[str] | None = None
            for role, arity in constraints[meta]:
                source = head_sigs if role == "head" else body_sigs
                choices = {pred for pred, candidate_arity in source if candidate_arity == arity}
                allowed = choices if allowed is None else allowed & choices
            domains.append(tuple(sorted(allowed or ())))
        for values in product(*domains):
            concrete = _replace_meta(("rule", template[1], template[2]),
                                     dict(zip(metas, values)))
            validate_rule(concrete)
            if safe(rule_from_ir(concrete)):
                emitted.add(concrete)
    return tuple(sorted(emitted, key=canonical_json))


def update_program_stats(state: Form, checked: Sequence[Form],
                         winners: Sequence[Form]) -> Form:
    """Persist program search Experience; it never grants assertion authority."""
    language = field(state, "language")
    old = {stat[1]: (stat[2], stat[3])
           for stat in field(language, "program-stats")[1:]}
    tried = {name: 0 for name in old}
    won = {name: 0 for name in old}
    for candidate in checked:
        for name in program_origins(state, candidate):
            tried[name] += 1
    for candidate in winners:
        for name in program_origins(state, candidate):
            won[name] += 1
    stats = ("program-stats", *(("program-stat", name,
               old[name][0] + tried[name], old[name][1] + won[name])
              for name in sorted(old)))
    updated = replace_field(language, "program-stats", stats)
    return replace_field(state, "language", updated)


def program_origins(state: Form, candidate: Form) -> tuple[str, ...]:
    """Match one emitted rule back to code templates without re-expanding domains."""
    result = []
    for program in field(field(state, "language"), "programs")[1:]:
        template = ("rule", program[2][1], program[2][2])
        bindings: dict[str, str] = {}

        def matches(left: Form, right: Form) -> bool:
            if not isinstance(left, tuple) or not isinstance(right, tuple):
                return left == right
            if len(left) != len(right) or left[0] != right[0]:
                return False
            if left[0] == "atom" and isinstance(left[1], str) and left[1].startswith("$"):
                old = bindings.get(left[1])
                if old is not None and old != right[1]:
                    return False
                bindings[left[1]] = right[1]
                return all(matches(a, b) for a, b in zip(left[2:], right[2:]))
            return all(matches(a, b) for a, b in zip(left[1:], right[1:]))

        if matches(template, candidate):
            result.append(program[1])
    return tuple(sorted(result))
