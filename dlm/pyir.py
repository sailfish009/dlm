"""Untrusted Python frontend: AST -> typed hierarchical PyIR -> Horn observations."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Iterable

from .ir import Form, IRValidationError, field, sorted_forms
from .kernel import Atom


def _stable_id(kind: str, *parts: object) -> str:
    text = "\0".join(map(str, (kind, *parts)))
    return "@" + kind + "-" + hashlib.sha256(text.encode()).hexdigest()[:14]


def _span(path: str, node: ast.AST) -> Form:
    return ("source-span", path, int(getattr(node, "lineno", 0)),
            int(getattr(node, "col_offset", 0)), int(getattr(node, "end_lineno", 0)),
            int(getattr(node, "end_col_offset", 0)))


def _target(call: ast.Call) -> str:
    fn = call.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return "<dynamic>"


class _Calls(ast.NodeVisitor):
    def __init__(self):
        self.calls: list[ast.Call] = []

    def visit_Call(self, node: ast.Call):
        self.calls.append(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        return None

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef


def _function_records(path: Path, logical: str):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=logical)
    records = []

    def recurse(body, scope=()):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = ".".join((*scope, node.name))
                records.append((qual, node))
                recurse(node.body, (*scope, node.name))
            elif isinstance(node, ast.ClassDef):
                recurse(node.body, (*scope, node.name))

    recurse(tree.body)
    return records


def lower_paths(paths: Iterable[str | Path], root: str | Path | None = None) -> Form:
    paths = tuple(sorted((Path(p) for p in paths), key=str))
    base = Path(root) if root is not None else Path.cwd()
    raw = []
    names: dict[str, list[str]] = {}
    for path in paths:
        try:
            logical = str(path.relative_to(base))
        except ValueError:
            logical = str(path)
        module = logical.removesuffix(".py").replace("/", ".")
        for local_name, node in _function_records(path, logical):
            qualified = f"{module}.{local_name}"
            raw.append((logical, qualified, node))
            names.setdefault(node.name, []).append(qualified)

    modules: dict[str, list[Form]] = {}
    package_edges: list[Form] = []
    all_node_ids: set[str] = set()
    for logical, qualified, fn in raw:
        fn_id = _stable_id("fn", logical, qualified)
        all_node_ids.add(fn_id)
        collector = _Calls()
        for statement in fn.body:
            collector.visit(statement)
        operations: list[Form] = []
        previous = None
        for index, call in enumerate(collector.calls):
            target = _target(call)
            resolved = names[target][0] if target in names and len(names[target]) == 1 else "unknown"
            op_id = _stable_id("op", logical, qualified, call.lineno, call.col_offset, index)
            all_node_ids.add(op_id)
            operation = (
                "py-node", op_id, ("kind", "py-call"), ("name", target),
                ("owner", qualified),
                ("inputs", ("port", "callable", ("type", "py-callable")),
                 *(("port", f"arg{i}", ("type", "pyobj"))
                   for i, _ in enumerate(call.args))),
                ("outputs", ("port", "result", ("type", "pyobj"))),
                ("effect", "unknown"), ("resolution", resolved), _span(logical, call),
            )
            operations.append(operation)
            package_edges.append(("py-edge", ("kind", "contains"),
                                  ("from", fn_id), ("to", op_id)))
            if previous is not None:
                package_edges.append(("py-edge", ("kind", "control"),
                                      ("from", previous), ("to", op_id)))
            previous = op_id
            if resolved != "unknown":
                target_id = _stable_id("fn", next(p for p, q, _ in raw if q == resolved), resolved)
                package_edges.append(("py-edge", ("kind", "call"),
                                      ("from", fn_id), ("to", target_id),
                                      ("via", op_id)))
        function = (
            "py-node", fn_id, ("kind", "function"), ("name", qualified),
            ("inputs", *(("port", arg.arg, ("type", "pyobj")) for arg in fn.args.args)),
            ("outputs", ("port", "return", ("type", "pyobj"))),
            ("effect", "control"), _span(logical, fn),
            ("region", ("py-graph", ("nodes", *operations))),
        )
        modules.setdefault(logical, []).append(function)

    module_forms = []
    for logical in sorted(modules):
        module_id = _stable_id("module", logical)
        nodes = tuple(sorted(modules[logical], key=lambda x: str(x[1])))
        module_forms.append(("py-node", module_id, ("kind", "module"),
                             ("name", logical), ("inputs",), ("outputs",),
                             ("effect", "declaration"),
                             ("region", ("py-graph", ("nodes", *nodes)))))
    result: Form = ("pyir-package", ("version", 1), ("nodes", *module_forms),
                    ("edges", *tuple(sorted(package_edges, key=repr))))
    validate_pyir(result)
    return result


def _all_nodes(tree: Form):
    if isinstance(tree, tuple):
        if tree and tree[0] == "py-node":
            yield tree
        for child in tree[1:]:
            yield from _all_nodes(child)


def validate_pyir(package: Form) -> None:
    if not isinstance(package, tuple) or package[0] != "pyir-package":
        raise IRValidationError("expected pyir-package")
    nodes = tuple(_all_nodes(package))
    ids = [node[1] for node in nodes]
    if len(ids) != len(set(ids)) or any(not isinstance(x, str) for x in ids):
        raise IRValidationError("PyIR node IDs must be unique strings")
    known = set(ids)
    for edge in field(package, "edges")[1:]:
        if not isinstance(edge, tuple) or edge[0] != "py-edge":
            raise IRValidationError("malformed PyIR edge")
        if field(edge, "from")[1] not in known or field(edge, "to")[1] not in known:
            raise IRValidationError("PyIR edge endpoint does not exist")


def call_facts(package: Form) -> frozenset[Atom]:
    validate_pyir(package)
    names = {node[1]: field(node, "name")[1] for node in _all_nodes(package)}
    return frozenset(Atom("calls", (names[field(edge, "from")[1]],
                                    names[field(edge, "to")[1]]))
                     for edge in field(package, "edges")[1:]
                     if field(edge, "kind")[1] == "call")


def source_hash(paths: Iterable[str | Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted((Path(p) for p in paths), key=str):
        digest.update(str(path).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
