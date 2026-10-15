"""MNIST ``main.py`` -> function-free Horn facts (the REDUCTION spec).

This is the untrusted *reduction* of external source code into the model's form
vocabulary.  It is deliberately lossy and purpose-driven: it does not try to
represent Python, only the relations a deductive reader needs to answer "what
does this file do?".

Relations (all function-free, binary or unary)::

    (imports   module package)
    (defines   module symbol)
    (method_of class  method)
    (inherits  class  base)
    (creates   owner  class)         ; `owner` instantiates `class`
    (calls     owner  callee)        ; resolved call site
    (step_of   owner  step)          ; a call site as an ordered step
    (before    step   step)          ; consecutive steps inside one owner

Constants are single-token slugs; ``labels`` maps each slug back to the human
name so the realizer can speak.  The order of call sites is source order by
``(lineno, col_offset)``; ``pipelines`` keeps that order per owner.
"""
from __future__ import annotations

import ast
import re
from typing import Dict, List, Tuple

Fact = Tuple[str, ...]  # (pred, *slug args)


def slug(text: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "_", str(text).strip().lower())
    return out.strip("_") or "unknown"


class _Reduce:
    def __init__(self) -> None:
        self.facts: set = set()
        self.labels: Dict[str, str] = {}
        self.pipelines: Dict[str, List[str]] = {}

    def lab(self, name: str) -> str:
        s = slug(name)
        self.labels.setdefault(s, name)
        return s

    def add(self, pred: str, *args: str) -> None:
        self.facts.add((pred,) + tuple(args))


def _dotted(func: ast.expr) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts: List[str] = []
        o: ast.expr = func
        while isinstance(o, ast.Attribute):
            parts.append(o.attr)
            o = o.value
        if isinstance(o, ast.Name):
            parts.append(o.id)
        return ".".join(reversed(parts))
    return "?"


def _body(R: _Reduce, owner_name: str, node: ast.AST) -> None:
    owner = R.lab(owner_name)
    calls = [(getattr(c, "lineno", 0), getattr(c, "col_offset", 0), c)
             for c in ast.walk(node) if isinstance(c, ast.Call)]
    calls.sort(key=lambda t: (t[0], t[1]))
    order: List[str] = []
    for _, _, call in calls:
        name = _dotted(call.func)
        if name == "?":
            continue
        callee = R.lab(name)
        R.add("calls", owner, callee)
        last = name.split(".")[-1]
        if last[:1].isupper():  # a constructor call -> instantiation
            R.add("creates", owner, R.lab(last))
        if callee not in order:
            order.append(callee)
    R.pipelines[owner] = order
    for a, b in zip(order, order[1:]):
        sa = R.lab(f"{owner_name}__{a}")
        sb = R.lab(f"{owner_name}__{b}")
        R.add("step_of", owner, sa)
        R.add("step_of", owner, sb)
        R.add("before", sa, sb)


def extract(src: str, module: str = "main") -> dict:
    """Python source -> {module, facts, labels, pipelines}; raises on syntax error."""
    tree = ast.parse(src)
    R = _Reduce()
    mod = R.lab(module)

    for n in tree.body:
        if isinstance(n, ast.Import):
            for a in n.names:
                R.add("imports", mod, R.lab(a.name))
        elif isinstance(n, ast.ImportFrom):
            R.add("imports", mod, R.lab(n.module or ""))
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            R.add("defines", mod, R.lab(n.name))

    for c in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        cls = R.lab(c.name)
        for b in c.bases:
            R.add("inherits", cls, R.lab(ast.unparse(b)))
        for m in c.body:
            if isinstance(m, ast.FunctionDef):
                R.add("method_of", cls, R.lab(f"{c.name}.{m.name}"))
                _body(R, f"{c.name}.{m.name}", m)

    for f in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        _body(R, f.name, f)

    return {"module": mod, "facts": sorted(R.facts), "labels": R.labels,
            "pipelines": R.pipelines}