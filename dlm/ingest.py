"""Candidate-blind external text/code -> typed IR-TREE documents and evidence."""
from __future__ import annotations

import ast
import hashlib
import html
import re
import unicodedata
from html.parser import HTMLParser
from typing import Iterable, Sequence

from .ir import (Form, field, node_id, replace_field, validate_model_state)
from .kernel import Atom, atom_to_ir, episode_ir

_WS = re.compile(r"\s+")
_SENTENCE = re.compile(r"[^\n.!?]+(?:[.!?]+|$)")
_MD_LINK = re.compile(r"\[([^]]+)\]\([^)]+\)")
_MD_MARK = re.compile(r"(?m)^\s{0,3}(?:#{1,6}\s+|[-*+]\s+|>\s*)")


class _TextHTML(HTMLParser):
    """Small deterministic HTML-to-text reducer; scripts/styles are ignored."""

    _blocks = {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3",
               "h4", "h5", "h6", "tr", "pre", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.hidden += 1
        elif not self.hidden and tag in self._blocks:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.hidden:
            self.hidden -= 1
        elif not self.hidden and tag in self._blocks:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def normalize_text(content: str, media_type: str = "text/plain") -> str:
    """Reduce presentation syntax while retaining all readable text."""
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    if "html" in media_type:
        parser = _TextHTML()
        parser.feed(text)
        text = "".join(parser.parts)
    elif "markdown" in media_type or media_type in {"text/x-markdown", "text/md"}:
        text = _MD_LINK.sub(r"\1", text)
        text = _MD_MARK.sub("", text)
        text = text.replace("```", "\n")
        text = re.sub(r"[*_`~]", "", text)
    text = html.unescape(text)
    lines = [_WS.sub(" ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _entity(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _WS.sub(" ", text).strip(" \t\n\"'`()[]{}:;,.-")
    return text.casefold()[:240]


def _sentences(text: str) -> tuple[Form, ...]:
    result = []
    index = 0
    for match in _SENTENCE.finditer(text):
        sentence = _WS.sub(" ", match.group(0)).strip()
        if not sentence:
            continue
        result.append(("sentence", ("id", f"s{index}"), ("text", sentence),
                       ("span", match.start(), match.end())))
        index += 1
    return tuple(result)


def _claim(atom: Atom, sentence: Form, extractor: str, confidence: float,
           status: str = "acquired") -> Form:
    return ("claim", ("proposition", atom_to_ir(atom)), ("status", status),
            ("extractor", extractor), ("confidence", float(confidence)),
            ("support", field(sentence, "id")[1]), field(sentence, "span"))


def _text_claims(sentences: Sequence[Form]) -> tuple[Form, ...]:
    """Conservative lexical extraction. It receives no theory or candidate."""
    patterns = (
        ("is-a", re.compile(r"^(.{1,100}?)\s+(?:is|are)\s+(?:an?|the)\s+(.{1,160}?)(?:[,;]|[.!?]?$)", re.I), .88),
        ("depends-on", re.compile(r"^(.{1,100}?)\s+depends\s+on\s+(.{1,160}?)(?:[,;]|[.!?]?$)", re.I), .93),
        ("uses", re.compile(r"^(.{1,100}?)\s+uses\s+(.{1,160}?)(?:[,;]|[.!?]?$)", re.I), .92),
        ("contains", re.compile(r"^(.{1,100}?)\s+contains\s+(.{1,160}?)(?:[,;]|[.!?]?$)", re.I), .92),
        ("part-of", re.compile(r"^(.{1,100}?)\s+is\s+part\s+of\s+(.{1,160}?)(?:[,;]|[.!?]?$)", re.I), .94),
    )
    claims: list[Form] = []
    for sentence in sentences:
        text = field(sentence, "text")[1]
        low = text.casefold()
        uncertain = any(cue in low for cue in (" may ", " might ", " reportedly ",
                                                " alleged", " is not ", " are not "))
        for predicate, pattern, confidence in patterns:
            match = pattern.match(text)
            if not match:
                continue
            left, right = _entity(match.group(1)), _entity(match.group(2))
            if not left or not right or left == right:
                continue
            status = "guessed" if uncertain else "acquired"
            claims.append(_claim(Atom(predicate, (left, right)), sentence,
                                 "lexical-relations-v1", confidence, status))
            break
    return tuple(claims)


def _python_projection(content: str, logical_name: str) -> tuple[Form, tuple[Form, ...]]:
    """AST-only code projection; unresolved calls stay guessed structural data."""
    try:
        tree = ast.parse(content, filename=logical_name)
    except (SyntaxError, ValueError, RecursionError):
        return ("python-tree", ("status", "unparsed"), ("nodes",)), ()
    nodes: list[Form] = []
    claims: list[Form] = []
    local_names = {node.name for node in ast.walk(tree)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    module = _entity(logical_name)
    sentence = ("sentence", ("id", "python-ast"), ("text", logical_name),
                ("span", 0, len(content)))

    def dotted(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = dotted(node.value)
            return (prefix + "." + node.attr).strip(".") if prefix else node.attr
        return "<dynamic>"

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.scope = [module]

        def _definition(self, node, kind):
            name = _entity(".".join((*self.scope[1:], node.name)) or node.name)
            nodes.append(("python-node", ("kind", kind), ("name", name),
                          ("line", int(node.lineno))))
            claims.append(_claim(Atom("defines", (module, name)), sentence,
                                 "python-ast-v1", 1.0))
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

        def visit_FunctionDef(self, node):
            self._definition(node, "function")

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            self._definition(node, "class")

        def visit_Import(self, node):
            for alias in node.names:
                self._import(alias.name, node.lineno)

        def visit_ImportFrom(self, node):
            if node.module:
                self._import(("." * node.level) + node.module, node.lineno)
            else:
                for alias in node.names:
                    self._import(("." * node.level) + alias.name, node.lineno)

        def _import(self, name, line):
            target = _entity(name)
            nodes.append(("python-node", ("kind", "import"),
                          ("name", target), ("line", int(line))))
            claims.append(_claim(Atom("imports", (module, target)), sentence,
                                 "python-ast-v1", 1.0))

        def visit_Call(self, node):
            owner = _entity(".".join(self.scope))
            target = _entity(dotted(node.func))
            resolved = target != "<dynamic>" and target.rsplit(".", 1)[-1] in local_names
            status = "acquired" if resolved else "guessed"
            nodes.append(("python-node", ("kind", "call"), ("owner", owner),
                          ("name", target),
                          ("resolution", "local" if resolved else "unknown"),
                          ("line", int(node.lineno))))
            claims.append(_claim(Atom("calls", (owner, target)), sentence,
                                 "python-ast-v1", 1.0, status))
            self.generic_visit(node)

    Visitor().visit(tree)
    return ("python-tree", ("status", "parsed"), ("nodes", *nodes)), tuple(claims)


def _build_document(*, provider: str, uri: str, title: str, content: str,
                    media_type: str, source_group: str, revision: str,
                    trust: str) -> Form:
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    document_id = "@doc-" + hashlib.sha256(
        (provider + "\0" + uri + "\0" + content_hash).encode()).hexdigest()[:20]
    normalized = normalize_text(content, media_type)
    sentences = _sentences(normalized)
    tree: Form = ("document-tree", ("sentences", *sentences))
    claims = _text_claims(sentences)
    if media_type in {"text/x-python", "application/x-python-code"} or uri.endswith(".py"):
        py_tree, py_claims = _python_projection(content, title or uri)
        tree = ("document-tree", ("sentences", *sentences), py_tree)
        claims = claims + py_claims
    document: Form = (
        "source-document", ("id", document_id),
        ("provenance", ("provider", provider), ("uri", uri),
         ("source-group", source_group or f"{provider}:{title or uri}"),
         ("trust", trust), ("revision", revision), ("content-hash", content_hash)),
        ("media-type", media_type), ("title", title), ("content", content),
        ("normalized", normalized), tree, ("claims", *claims),
    )
    return document


def source_document(*, provider: str, uri: str, title: str, content: str,
                    media_type: str = "text/plain", source_group: str = "",
                    revision: str = "", trust: str = "acquired") -> Form:
    """Convert one external payload completely into a canonical typed document."""
    if trust not in {"observed", "acquired", "guessed"}:
        raise ValueError("external document trust must be observed/acquired/guessed")
    document = _build_document(
        provider=provider, uri=uri, title=title, content=content,
        media_type=media_type, source_group=source_group, revision=revision,
        trust=trust)
    from .ir import validate_document
    validate_document(document)
    return document


def canonical_document(document: Form) -> Form:
    """Re-run the candidate-blind projection from a document's raw payload."""
    provenance = field(document, "provenance")
    return _build_document(
        provider=field(provenance, "provider")[1],
        uri=field(provenance, "uri")[1], title=field(document, "title")[1],
        content=field(document, "content")[1],
        media_type=field(document, "media-type")[1],
        source_group=field(provenance, "source-group")[1],
        revision=field(provenance, "revision")[1],
        trust=field(provenance, "trust")[1])


def document_to_episode(document: Form, *, role: str = "train",
                        min_confidence: float = .85) -> Form:
    """Project only admitted claims to evidence; guessed claims remain questions."""
    from .ir import validate_document
    validate_document(document)
    facts = []
    document_trust = field(field(document, "provenance"), "trust")[1]
    for claim in field(document, "claims")[1:]:
        if (document_trust != "guessed"
                and field(claim, "status")[1] == "acquired"
                and float(field(claim, "confidence")[1]) >= min_confidence):
            from .kernel import atom_from_ir
            facts.append(atom_from_ir(field(claim, "proposition")[1]))
    provenance = field(document, "provenance")
    episode = episode_ir(field(provenance, "source-group")[1], facts, role=role)
    return (*episode, ("document-id", field(document, "id")[1]),
            ("trust", field(provenance, "trust")[1]))


def ingest_transition(state: Form, documents: Iterable[Form], *, role: str = "train",
                      min_confidence: float = .85) -> Form:
    """Return a pure external-observation transition; no candidate is consulted."""
    validate_model_state(state)
    supplied = tuple(documents)
    from .ir import validate_document
    by_id = {}
    for document in supplied:
        validate_document(document)
        by_id.setdefault(field(document, "id")[1], document)
    incoming = tuple(by_id[key] for key in sorted(by_id))
    existing_docs = tuple(field(state, "documents")[1:])
    existing_ids = {field(document, "id")[1] for document in existing_docs}
    added = tuple(document for document in incoming
                  if field(document, "id")[1] not in existing_ids)
    episodes = tuple(document_to_episode(document, role=role,
                                         min_confidence=min_confidence)
                     for document in added)
    work = replace_field(state, "documents", ("documents", *existing_docs, *added))
    work = replace_field(work, "evidence",
                         ("evidence", *field(state, "evidence")[1:], *episodes))
    work = replace_field(work, "candidates", ("candidates",))
    from .learn import _set_metrics
    work = _set_metrics(work, 0)
    validate_model_state(work)
    action = ("ingest", ("role", role), ("min-confidence", float(min_confidence)),
              ("documents", *incoming))
    return ("transition", ("before", node_id(state)), ("action", action),
            ("verdicts",), ("events",), ("after", work))
