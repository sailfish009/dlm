"""Natural language is an untrusted realization of IR learning events."""
from __future__ import annotations

from .ir import Form, dump, field


def realize(event: Form) -> str:
    if not isinstance(event, tuple) or event[0] != "learning-event":
        raise ValueError("speech requires a learning-event IR form")
    kind = field(event, "kind")[1]
    if kind == "abstain":
        return f"I abstained because {field(event, 'reason')[1]}."
    if kind != "improvement":
        raise ValueError(f"unknown learning event {kind}")
    learned = field(event, "learned")[1:]
    retracted = field(event, "retracted")[1:]
    changes = []
    if learned:
        changes.append("learned " + "; ".join(dump(rule) for rule in learned))
    if retracted:
        changes.append("retracted " + "; ".join(dump(rule) for rule in retracted))
    return ("I improved my IR model: held-out coverage "
            f"{field(event, 'coverage-before')[1]}->{field(event, 'coverage-after')[1]}, "
            f"contradictions {field(event, 'false-before')[1]}->{field(event, 'false-after')[1]}; "
            + " and ".join(changes) + ".")
