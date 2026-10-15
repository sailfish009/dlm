"""DLM v0.0048 -- theory persistence (untrusted).

A learned theory is Ground rules + Experience rules + the facts they were learned
over.  To run for a long time you must be able to stop, checkpoint, and resume, so
this module round-trips all three through JSON.  The kernel is untouched: loading
a theory only rebuilds kernel dataclasses; every derived claim is still decided by
``closure`` at use time, never by the file.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Tuple

from . import Atom, Const, KnowledgeBase, Rule, Var

__all__ = [
    "Theory", "atom_to_json", "atom_from_json", "rule_to_json", "rule_from_json",
    "theory_to_dict", "theory_from_dict", "save_theory", "load_theory", "SCHEMA",
]

SCHEMA = 1


def _term_to_json(t: Any) -> list:
    if isinstance(t, Var):
        return ["v", t.name]
    if isinstance(t, Const):
        return ["c", t.name]
    raise TypeError(f"not a kernel term: {t!r}")


def _term_from_json(o: list) -> Any:
    kind, name = o
    return Var(name) if kind == "v" else Const(name)


def atom_to_json(a: Atom) -> dict:
    return {"pred": a.pred, "args": [_term_to_json(t) for t in a.args]}


def atom_from_json(o: dict) -> Atom:
    return Atom(o["pred"], tuple(_term_from_json(t) for t in o["args"]))


def rule_to_json(r: Rule) -> dict:
    return {"name": r.name, "head": atom_to_json(r.head),
            "body": [atom_to_json(b) for b in r.body]}


def rule_from_json(o: dict) -> Rule:
    return Rule(atom_from_json(o["head"]), tuple(atom_from_json(b) for b in o["body"]),
                o.get("name", ""))


@dataclass(frozen=True)
class Theory:
    """A checkpoint: the rules learned so far plus the facts and arbitrary meta."""

    ground: Tuple[Rule, ...] = ()
    experience: Tuple[Rule, ...] = ()
    facts: frozenset = frozenset()
    meta: Dict[str, Any] = field(default_factory=dict)

    def base(self) -> KnowledgeBase:
        from .ground import Ground
        return Ground(self.ground).base(self.facts)

    def to_kb(self) -> KnowledgeBase:
        from .ground import Experience
        return Experience(self.experience).to_kb(self.base())


def theory_to_dict(t: Theory) -> dict:
    return {
        "schema": SCHEMA,
        "ground": [rule_to_json(r) for r in t.ground],
        "experience": [rule_to_json(r) for r in t.experience],
        "facts": [atom_to_json(a) for a in sorted(t.facts, key=str)],
        "meta": dict(t.meta),
    }


def theory_from_dict(d: dict) -> Theory:
    if d.get("schema") != SCHEMA:
        raise ValueError(f"unsupported theory schema {d.get('schema')!r}")
    return Theory(
        ground=tuple(rule_from_json(r) for r in d["ground"]),
        experience=tuple(rule_from_json(r) for r in d["experience"]),
        facts=frozenset(atom_from_json(a) for a in d["facts"]),
        meta=dict(d.get("meta", {})),
    )


def save_theory(path: str, theory: Theory) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(theory_to_dict(theory), fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def load_theory(path: str) -> Theory:
    with open(path, "r", encoding="utf-8") as fh:
        return theory_from_dict(json.load(fh))