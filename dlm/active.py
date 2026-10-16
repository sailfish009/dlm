"""Model-owned need assessment and active external acquisition transitions."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from .ingest import ingest_transition
from .ir import Form, canonical_json, field, node_id, replace_field, walk
from .kernel import atom_to_ir, closure, episode_data, state_rules
from .web import CachedWeb, acquire_documents


def _need(kind: str, query: str, target: Form, reason: str) -> Form:
    policy = {
        "unresolved-symbol": ("github", "web-search", "wikipedia"),
        "proof-hole": ("wikipedia", "web-search", "github"),
        "unknown-premise": ("wikipedia", "web-search", "github"),
    }
    providers = policy[kind]
    identity = hashlib.sha256(canonical_json(
        ("need-key", kind, query, target, reason, providers)).encode()).hexdigest()
    return ("information-need", ("id", "@need-" + identity[:20]),
            ("kind", kind), ("query", query), ("target", target),
            ("reason", reason), ("providers", *providers))


def _history(state: Form) -> tuple[dict[str, int], set[str]]:
    attempts: dict[str, int] = {}
    acquired: set[str] = set()
    for record in field(field(state, "agenda"), "acquisitions")[1:]:
        key = field(field(record, "need")[1], "id")[1]
        attempts[key] = attempts.get(key, 0) + 1
        if field(record, "status")[1] == "acquired":
            acquired.add(key)
    return attempts, acquired


def information_needs(state: Form) -> tuple[Form, ...]:
    """Derive deterministic proof/source holes from state, not from a candidate rule."""
    needs: list[Form] = []
    subject = field(state, "subject")[1]
    if subject[0] == "source-subject":
        pyir = field(subject, "pyir")[1]
        names = set()
        for node in walk(pyir):
            if not isinstance(node, tuple) or not node or node[0] != "py-node":
                continue
            try:
                if field(node, "kind")[1] == "py-call" and field(node, "resolution")[1] == "unknown":
                    names.add(str(field(node, "name")[1]))
            except ValueError:
                continue
        for name in sorted(names):
            if name != "<dynamic>":
                needs.append(_need(
                    "unresolved-symbol", f"Python {name} API semantics",
                    ("symbol", name), "source call has no resolved local definition"))

    rules = state_rules(state)
    for episode in field(state, "evidence")[1:]:
        data = episode_data(episode)
        closed = closure(data["facts"], rules)
        for atom in sorted(data["confirmed"] - closed):
            query = " ".join((*atom.args, atom.pred.replace("-", " ")))
            needs.append(_need("proof-hole", query, atom_to_ir(atom),
                               "confirmed target has no kernel proof"))
        for atom in sorted(data["unknown"]):
            query = " ".join((*atom.args, atom.pred.replace("-", " ")))
            needs.append(_need("unknown-premise", query, atom_to_ir(atom),
                               "explicit unknown may need an external premise"))

    seen, unique = set(), []
    attempts, acquired = _history(state)
    for order, need in enumerate(needs):
        key = field(need, "id")[1]
        if key not in seen and key not in acquired:
            seen.add(key)
            unique.append((attempts.get(key, 0), order, need))
    # Cache misses rotate behind untouched needs; an online restart can retry them.
    unique.sort(key=lambda item: (item[0], item[1]))
    return tuple(item[2] for item in unique)


def next_need(state: Form) -> Form | None:
    needs = information_needs(state)
    return needs[0] if needs else None


def acquisition_transition(state: Form, need: Form,
                           documents: Iterable[Form]) -> Form:
    """Ingest fetched observations and append the selected need/outcome to agenda."""
    expected = next_need(state)
    if expected is None or canonical_json(expected) != canonical_json(need):
        raise ValueError("acquisition need is not the model's current next need")
    documents = tuple(documents)
    ingested = ingest_transition(state, documents)
    work = field(ingested, "after")[1]
    status = "acquired" if documents else "abstained"
    record = ("acquisition-record", ("need", need), ("status", status),
              ("round", field(state, "round")[1]),
              ("document-ids", *(field(document, "id")[1] for document in documents)))
    agenda = field(work, "agenda")
    work = replace_field(work, "agenda",
                         ("agenda", ("acquisitions",
                          *field(agenda, "acquisitions")[1:], record)))
    from .ir import validate_model_state
    validate_model_state(work)
    action = ("acquire", ("need", need), ("documents", *documents))
    return ("transition", ("before", node_id(state)), ("action", action),
            ("verdicts",), ("events",), ("after", work))


def acquire_once(state: Form, *, cache_dir: str | Path, offline: bool = True,
                 providers: Iterable[str] = ("wikipedia", "github", "web-search"),
                 limit: int = 1, timeout: float = 10.0,
                 web: CachedWeb | None = None) -> Form | None:
    """Let the model choose one need, query external senses, and return a transition."""
    need = next_need(state)
    if need is None:
        return None
    web = web or CachedWeb(cache_dir, offline=offline, timeout=timeout)
    allowed = set(providers)
    selected = tuple(name for name in field(need, "providers")[1:] if name in allowed)
    documents = acquire_documents(
        str(field(need, "query")[1]), cache_dir=cache_dir, offline=offline,
        providers=selected, limit=limit, web=web)
    return acquisition_transition(state, need, documents)
