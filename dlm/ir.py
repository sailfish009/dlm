"""Canonical typed IR-TREE, the single persistent language of DLM 0.0.65."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

Scalar = str | int | float | bool | None
Form = Scalar | tuple["Form", ...]

_SYMBOL = re.compile(r"^[A-Za-z_@?+*/<>=!$%&~.^:-][A-Za-z0-9_@?+*/<>=!$%&~.^:-]*$")
_TOKEN = re.compile(r'\s*(?:(\()|(\))|("(?:\\.|[^"\\])*")|([^\s()]+))')
_VALID_DOCUMENTS: set[str] = set()


class IRValidationError(ValueError):
    pass


def is_form(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, (str, int, bool)) or value is None:
        return True
    return (isinstance(value, tuple) and len(value) > 0
            and isinstance(value[0], str) and all(is_form(x) for x in value[1:]))


def head(form: Form) -> str:
    if not isinstance(form, tuple) or not form:
        raise IRValidationError("expected a non-empty IR form")
    return form[0]


def children(form: Form) -> tuple[Form, ...]:
    return form[1:] if isinstance(form, tuple) else ()


def walk(form: Form):
    yield form
    if isinstance(form, tuple):
        for child in form[1:]:
            yield from walk(child)


def _bare(token: str) -> Scalar:
    if token == "true":
        return True
    if token == "false":
        return False
    if token == "null":
        return None
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token


def dump(form: Form) -> str:
    if isinstance(form, tuple):
        return "(" + " ".join(dump(x) for x in form) + ")"
    if isinstance(form, str):
        return form if _SYMBOL.fullmatch(form) and _bare(form) == form else json.dumps(form)
    if form is True:
        return "true"
    if form is False:
        return "false"
    if form is None:
        return "null"
    return repr(form)


def loads(text: str) -> Form:
    tokens: list[tuple[str, Scalar]] = []
    pos = 0
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if match is None:
            if text[pos:].strip():
                raise IRValidationError(f"invalid token at byte {pos}")
            break
        pos = match.end()
        left, right, quoted, bare = match.groups()
        if left:
            tokens.append(("left", "("))
        elif right:
            tokens.append(("right", ")"))
        elif quoted is not None:
            tokens.append(("value", json.loads(quoted)))
        elif bare is not None:
            tokens.append(("value", _bare(bare)))

    def parse(index: int) -> tuple[Form, int]:
        if index >= len(tokens):
            raise IRValidationError("unexpected end of input")
        kind, token = tokens[index]
        if kind == "left":
            values: list[Form] = []
            index += 1
            while index < len(tokens) and tokens[index][0] != "right":
                value, index = parse(index)
                values.append(value)
            if index >= len(tokens):
                raise IRValidationError("unclosed form")
            if not values or not isinstance(values[0], str):
                raise IRValidationError("a form must have a symbolic head")
            return tuple(values), index + 1
        if kind == "right":
            raise IRValidationError("unexpected closing parenthesis")
        return token, index + 1

    value, end = parse(0)
    if end != len(tokens):
        raise IRValidationError("expected exactly one IR expression")
    if not is_form(value):
        raise IRValidationError("invalid IR expression")
    return value


def _tuple_tree(value: Any) -> Form:
    if isinstance(value, list):
        return tuple(_tuple_tree(x) for x in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise IRValidationError(f"JSON value {type(value).__name__} is outside the IR")


def canonical_json(form: Form) -> str:
    if not is_form(form):
        raise IRValidationError("cannot serialize a malformed IR tree")
    return json.dumps(form, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def from_json(text: str) -> Form:
    form = _tuple_tree(json.loads(text))
    if not is_form(form):
        raise IRValidationError("JSON does not encode a finite IR expression")
    return form


def node_id(form: Form) -> str:
    return "@" + hashlib.sha256(canonical_json(form).encode()).hexdigest()[:20]


def dag_index(form: Form) -> dict[str, Form]:
    """Rebuildable content-addressed view; it is never authoritative state."""
    return {node_id(x): x for x in walk(form) if isinstance(x, tuple)}


def field(form: Form, name: str) -> Form:
    if not isinstance(form, tuple):
        raise IRValidationError(f"{name}: expected form")
    matches = [x for x in form[1:] if isinstance(x, tuple) and x[0] == name]
    if len(matches) != 1:
        raise IRValidationError(f"{form[0]} needs exactly one ({name} ...) field")
    return matches[0]


def replace_field(form: Form, name: str, value: Form) -> Form:
    if not isinstance(form, tuple) or not isinstance(value, tuple) or value[0] != name:
        raise IRValidationError("invalid field replacement")
    found = 0
    out: list[Form] = [form[0]]
    for item in form[1:]:
        if isinstance(item, tuple) and item[0] == name:
            out.append(value)
            found += 1
        else:
            out.append(item)
    if found != 1:
        raise IRValidationError(f"cannot replace non-unique field {name}")
    return tuple(out)


def _integer(value: Form) -> bool:
    return type(value) is int


def _number(value: Form) -> bool:
    return (type(value) is int or type(value) is float) and math.isfinite(float(value))


def validate_term(term: Form) -> None:
    if (not isinstance(term, tuple) or len(term) != 2
            or term[0] not in {"const", "var"} or not isinstance(term[1], str)):
        raise IRValidationError("term must be (const STRING) or (var NAME)")
    if term[0] == "var" and not term[1]:
        raise IRValidationError("variable names cannot be empty")


def validate_atom(atom: Form) -> None:
    if not isinstance(atom, tuple) or len(atom) < 2 or atom[0] != "atom":
        raise IRValidationError("expected (atom PRED TERM...)")
    if not isinstance(atom[1], str) or not atom[1]:
        raise IRValidationError("atom predicate must be a non-empty string")
    for term in atom[2:]:
        validate_term(term)


def validate_rule(rule: Form) -> None:
    if not isinstance(rule, tuple) or len(rule) != 3 or rule[0] != "rule":
        raise IRValidationError("expected (rule HEAD (body ATOM...))")
    validate_atom(rule[1])
    if not isinstance(rule[2], tuple) or rule[2][0] != "body" or len(rule[2]) < 2:
        raise IRValidationError("rule body must be non-empty")
    for atom in rule[2][1:]:
        validate_atom(atom)


def validate_episode(episode: Form) -> None:
    if not isinstance(episode, tuple) or episode[0] != "episode":
        raise IRValidationError("expected episode")
    for name in ("source", "role", "facts", "confirmed", "contradicted", "unknown"):
        field(episode, name)
    if len(field(episode, "source")) != 2 or not isinstance(field(episode, "source")[1], str):
        raise IRValidationError("episode source must be a string")
    if field(episode, "role")[1] not in {"train", "validation"}:
        raise IRValidationError("episode role must be train or validation")
    partitions = []
    for name in ("facts", "confirmed", "contradicted", "unknown"):
        part = field(episode, name)
        for atom in part[1:]:
            validate_atom(atom)
            if any(t[0] == "var" for t in atom[2:]):
                raise IRValidationError("evidence atoms must be ground")
        partitions.append(set(part[1:]))
    if partitions[1] & partitions[2]:
        raise IRValidationError("evidence cannot confirm and contradict an atom")


def validate_document(document: Form) -> None:
    if not isinstance(document, tuple) or document[0] != "source-document":
        raise IRValidationError("expected source-document")
    for name in ("id", "provenance", "media-type", "title", "content",
                 "normalized", "document-tree", "claims"):
        field(document, name)
    for name in ("id", "media-type", "title", "content", "normalized"):
        value = field(document, name)
        if len(value) != 2 or not isinstance(value[1], str):
            raise IRValidationError(f"document {name} must be a string")
    provenance = field(document, "provenance")
    for name in ("provider", "uri", "source-group", "trust", "revision",
                 "content-hash"):
        value = field(provenance, name)
        if len(value) != 2 or not isinstance(value[1], str):
            raise IRValidationError(f"provenance {name} must be a string")
    if not field(provenance, "provider")[1] or not field(provenance, "uri")[1]:
        raise IRValidationError("document provider and URI cannot be empty")
    if not field(provenance, "source-group")[1]:
        raise IRValidationError("source-group cannot be empty")
    if field(provenance, "trust")[1] not in {"observed", "acquired", "guessed"}:
        raise IRValidationError("unknown external trust tier")
    content = field(document, "content")[1]
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if field(provenance, "content-hash")[1] != digest:
        raise IRValidationError("document content hash mismatch")
    expected_id = "@doc-" + hashlib.sha256(
        (field(provenance, "provider")[1] + "\0" + field(provenance, "uri")[1]
         + "\0" + digest).encode()).hexdigest()[:20]
    if field(document, "id")[1] != expected_id:
        raise IRValidationError("document ID does not match provenance and content")
    tree = field(document, "document-tree")
    if len(tree) < 2:
        raise IRValidationError("document tree cannot be empty")
    for claim in field(document, "claims")[1:]:
        if not isinstance(claim, tuple) or claim[0] != "claim":
            raise IRValidationError("claims must contain claim forms")
        for name in ("proposition", "status", "extractor", "confidence", "support", "span"):
            field(claim, name)
        proposition = field(claim, "proposition")
        if len(proposition) != 2:
            raise IRValidationError("claim needs one proposition")
        validate_atom(proposition[1])
        if any(term[0] == "var" for term in proposition[1][2:]):
            raise IRValidationError("external claims must be ground")
        if field(claim, "status")[1] not in {"acquired", "guessed"}:
            raise IRValidationError("unknown claim status")
        confidence = field(claim, "confidence")[1]
        if not _number(confidence) or not 0.0 <= float(confidence) <= 1.0:
            raise IRValidationError("claim confidence must be in [0,1]")
        span = field(claim, "span")
        if (len(span) != 3 or not _integer(span[1]) or not _integer(span[2])
                or span[1] < 0 or span[2] < span[1]):
            raise IRValidationError("claim span is malformed")
    # Raw content is authoritative input; derived text/tree/claims must be the
    # exact output of the candidate-blind internal projection, not supplied facts.
    document_key = hashlib.sha256(canonical_json(document).encode()).hexdigest()
    if document_key not in _VALID_DOCUMENTS:
        from .ingest import canonical_document
        if canonical_json(canonical_document(document)) != canonical_json(document):
            raise IRValidationError("document projection is not canonical")
        _VALID_DOCUMENTS.add(document_key)


def validate_verdict(verdict: Form) -> None:
    if not isinstance(verdict, tuple) or verdict[0] != "verdict":
        raise IRValidationError("expected verdict")
    for name in ("formal", "coverage", "debt", "false-asserts", "support-sources",
                 "mdl", "reward", "useful"):
        field(verdict, name)
    if field(verdict, "formal")[1] not in {True, False}:
        raise IRValidationError("formal must be boolean")
    if field(verdict, "useful")[1] not in {True, False}:
        raise IRValidationError("useful must be boolean")
    for name in ("coverage", "debt", "false-asserts", "mdl"):
        if not _integer(field(verdict, name)[1]):
            raise IRValidationError(f"{name} must be an integer")
    if not _number(field(verdict, "reward")[1]):
        raise IRValidationError("reward must be numeric")
    if any(not isinstance(x, str) for x in field(verdict, "support-sources")[1:]):
        raise IRValidationError("support source names must be strings")


def validate_event(event: Form) -> None:
    if not isinstance(event, tuple) or event[0] != "learning-event":
        raise IRValidationError("expected learning-event")
    kind = field(event, "kind")[1]
    if kind == "abstain":
        field(event, "reason")
        field(event, "round")
        return
    if kind != "improvement":
        raise IRValidationError("unknown learning-event kind")
    for name in ("round", "coverage-before", "coverage-after", "false-before",
                 "false-after", "learned", "retracted"):
        field(event, name)
    for name in ("round", "coverage-before", "coverage-after", "false-before",
                 "false-after"):
        if not _integer(field(event, name)[1]):
            raise IRValidationError(f"event {name} must be an integer")
    for name in ("learned", "retracted"):
        for rule in field(event, name)[1:]:
            validate_rule(rule)


def validate_model_state(state: Form) -> None:
    if not is_form(state):
        raise IRValidationError("model-state contains a non-IR value")
    if not isinstance(state, tuple) or state[0] != "model-state":
        raise IRValidationError("expected model-state")
    required = ("version", "round", "documents", "agenda", "evidence", "theory",
                "memory", "language", "decision", "candidates", "verdicts",
                "events", "metrics", "subject")
    for name in required:
        field(state, name)
    if field(state, "version")[1] != "0.0.65":
        raise IRValidationError("wrong model-state version")
    if not _integer(field(state, "round")[1]):
        raise IRValidationError("round must be an integer")
    documents = field(state, "documents")[1:]
    for document in documents:
        validate_document(document)
    document_ids = [field(document, "id")[1] for document in documents]
    if len(document_ids) != len(set(document_ids)):
        raise IRValidationError("document IDs must be unique")
    agenda = field(state, "agenda")
    acquisitions = field(agenda, "acquisitions")
    for record in acquisitions[1:]:
        if not isinstance(record, tuple) or record[0] != "acquisition-record":
            raise IRValidationError("agenda must contain acquisition records")
        for name in ("need", "status", "round", "document-ids"):
            field(record, name)
        need_field = field(record, "need")
        if len(need_field) != 2 or not isinstance(need_field[1], tuple):
            raise IRValidationError("acquisition record needs one information need")
        need = need_field[1]
        if need[0] != "information-need":
            raise IRValidationError("expected information-need")
        for name in ("id", "kind", "query", "target", "reason", "providers"):
            field(need, name)
        for name in ("id", "kind", "query", "reason"):
            if len(field(need, name)) != 2 or not isinstance(field(need, name)[1], str):
                raise IRValidationError(f"information need {name} must be a string")
        if not isinstance(field(need, "target")[1], tuple):
            raise IRValidationError("information need target must be a form")
        if (not field(need, "providers")[1:]
                or any(name not in {"wikipedia", "github", "web-search"}
                       for name in field(need, "providers")[1:])):
            raise IRValidationError("information need providers are invalid")
        status = field(record, "status")[1]
        document_refs = field(record, "document-ids")[1:]
        if status not in {"acquired", "abstained"}:
            raise IRValidationError("unknown acquisition status")
        if (status == "acquired") != bool(document_refs):
            raise IRValidationError("acquisition status disagrees with documents")
        if not _integer(field(record, "round")[1]):
            raise IRValidationError("acquisition round must be an integer")
        if any(not isinstance(value, str) or value not in set(document_ids)
               for value in document_refs):
            raise IRValidationError("acquisition refers to an absent document")
    for episode in field(state, "evidence")[1:]:
        validate_episode(episode)
        document_fields = [x for x in episode[1:]
                           if isinstance(x, tuple) and x[0] == "document-id"]
        if document_fields and document_fields[0][1] not in set(document_ids):
            raise IRValidationError("evidence refers to an absent document")
    theory = field(state, "theory")
    for tier in ("ground", "experience"):
        rules = field(theory, tier)
        for rule in rules[1:]:
            validate_rule(rule)
    memory = field(state, "memory")
    for record in memory[1:]:
        if not isinstance(record, tuple) or record[0] != "experience-record":
            raise IRValidationError("memory must contain experience records")
        for name in ("id", "rule", "status", "round", "support-sources", "reason"):
            field(record, name)
        if not isinstance(field(record, "id")[1], str):
            raise IRValidationError("experience record id must be a string")
        rule_field = field(record, "rule")
        if len(rule_field) != 2:
            raise IRValidationError("experience record must contain one rule")
        validate_rule(rule_field[1])
        if field(record, "status")[1] not in {"active", "retracted"}:
            raise IRValidationError("unknown experience status")
        if not _integer(field(record, "round")[1]):
            raise IRValidationError("experience round must be an integer")
    language = field(state, "language")
    from .language import validate_language
    validate_language(language)
    decision = field(state, "decision")
    if not _number(field(decision, "lr")[1]):
        raise IRValidationError("decision learning rate must be numeric")
    if not _number(field(decision, "margin")[1]):
        raise IRValidationError("decision margin must be numeric")
    if not _integer(field(decision, "updates")[1]):
        raise IRValidationError("decision update count must be an integer")
    replay = field(decision, "replay")
    for item in replay[1:]:
        if not isinstance(item, tuple) or item[0] != "contrast":
            raise IRValidationError("decision replay must contain contrast records")
    for weight in field(decision, "weights")[1:]:
        if (not isinstance(weight, tuple) or len(weight) != 3 or weight[0] != "weight"
                or not isinstance(weight[1], str) or not _number(weight[2])):
            raise IRValidationError("malformed decision weight")
    for candidate in field(state, "candidates")[1:]:
        validate_rule(candidate)
    for checked in field(state, "verdicts")[1:]:
        if not isinstance(checked, tuple) or checked[0] != "checked":
            raise IRValidationError("malformed checked verdict")
        candidate = field(checked, "candidate")
        if len(candidate) != 2:
            raise IRValidationError("checked candidate must contain one rule")
        validate_rule(candidate[1])
        verdicts = [x for x in checked[1:] if isinstance(x, tuple) and x[0] == "verdict"]
        if len(verdicts) != 1:
            raise IRValidationError("checked record needs exactly one verdict")
        validate_verdict(verdicts[0])
        if field(checked, "admitted")[1] not in {True, False}:
            raise IRValidationError("admitted must be boolean")
    for event in field(state, "events")[1:]:
        validate_event(event)
    metrics = field(state, "metrics")
    for name in ("checks", "held-coverage", "held-total", "held-false"):
        value = field(metrics, name)
        if len(value) != 2 or not _integer(value[1]):
            raise IRValidationError(f"metric {name} must be an integer")
    subject_field = field(state, "subject")
    if len(subject_field) != 2 or not isinstance(subject_field[1], tuple):
        raise IRValidationError("subject must contain exactly one form")
    subject = subject_field[1]
    if subject[0] == "source-subject":
        if not isinstance(field(subject, "sha256")[1], str):
            raise IRValidationError("source subject hash must be a string")
        pyir = field(subject, "pyir")
        if len(pyir) != 2 or not isinstance(pyir[1], tuple) or pyir[1][0] != "pyir-package":
            raise IRValidationError("source subject must contain a PyIR package")
        from .pyir import validate_pyir
        validate_pyir(pyir[1])
    elif subject[0] != "none":
        raise IRValidationError("unknown subject kind")


def validate_transition(transition: Form) -> None:
    if not is_form(transition):
        raise IRValidationError("transition contains a non-IR value")
    if not isinstance(transition, tuple) or transition[0] != "transition":
        raise IRValidationError("expected transition")
    for name in ("before", "action", "verdicts", "events", "after"):
        field(transition, name)
    if not isinstance(field(transition, "before")[1], str):
        raise IRValidationError("transition before must be a content ID")
    if not isinstance(field(transition, "action")[1], tuple):
        raise IRValidationError("transition action must be a form")
    for checked in field(transition, "verdicts")[1:]:
        if not isinstance(checked, tuple) or checked[0] != "checked":
            raise IRValidationError("transition contains a malformed verdict record")
        verdicts = [x for x in checked[1:] if isinstance(x, tuple) and x[0] == "verdict"]
        if len(verdicts) != 1:
            raise IRValidationError("transition verdict record is incomplete")
        validate_verdict(verdicts[0])
    for event in field(transition, "events")[1:]:
        validate_event(event)
    after = field(transition, "after")
    if len(after) != 2:
        raise IRValidationError("transition after must contain one state")
    validate_model_state(after[1])


def save(path: str | Path, form: Form) -> None:
    validate_model_state(form)
    Path(path).write_text(json.dumps(form, ensure_ascii=False, indent=2) + "\n")


def load(path: str | Path) -> Form:
    form = from_json(Path(path).read_text())
    validate_model_state(form)
    return form


def sorted_forms(forms: Iterable[Form]) -> tuple[Form, ...]:
    return tuple(sorted(set(forms), key=canonical_json))
