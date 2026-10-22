"""A small MLIR-shaped dialect for the DLM space79 event machine.

This is an executable front-end, not upstream MLIR and not a second semantic
engine. It provides SSA result names, explicit operation/effect metadata, a
verifier, and lowering to the existing Maru space79 API. Maru remains the
reference interpreter and the trusted proof checker.

Dialect v0 deliberately has no scheduler, storage format or optimizer. Every
operation is a synchronous Maru state transition, so a lowered module cannot
silently diverge from the event machine it names.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Iterable

from sexp import Symbol, dumps, loads_many

SPACE_TYPE = "!space79.space"
ROOT = Path(__file__).resolve().parents[1]


class DialectError(ValueError):
    def __init__(self, message: str, line: int | None = None):
        self.line = line
        super().__init__(f"line {line}: {message}" if line else message)


@dataclass(frozen=True)
class OpSpec:
    args: tuple[str, ...]
    result: bool
    effects: tuple[str, ...]


OPS: dict[str, OpSpec] = {
    "new": OpSpec((), True, ("space.create",)),
    "define": OpSpec(("state", "name", "list", "list"), True, ("space.write",)),
    "use": OpSpec(("state", "name", "name", "list"), True, ("space.write",)),
    "prove": OpSpec(("state", "name", "list"), True, ("space.write", "queue.enqueue")),
    "program": OpSpec(("state", "name", "list"), True, ("space.write", "queue.enqueue")),
    "interpolate": OpSpec(("state", "name", "list", "list", "list"), True,
                          ("space.write", "queue.enqueue")),
    "beth": OpSpec(("state", "name", "list", "list", "list"), True,
                   ("space.write", "queue.enqueue")),
    "run": OpSpec(("state", "int"), True, ("space.write", "queue.step", "proof.check")),
    "resume": OpSpec(("state", "name", "bool"), True, ("space.write", "queue.enqueue")),
    "dump": OpSpec(("state", "label"), False, ("space.read", "output.write")),
    "job": OpSpec(("state", "label", "name"), False, ("space.read", "output.write")),
    "definitions": OpSpec(("state", "label"), False, ("space.read", "output.write")),
}

_HEADER = re.compile(r"space\.module(?:\s+@([A-Za-z_][A-Za-z_0-9]*))?\s*\{\s*$")
_OP = re.compile(r"(?:(%[A-Za-z_][A-Za-z_0-9]*)\s*=\s*)?space\.([A-Za-z_][A-Za-z_0-9]*)(.*)$", re.S)


@dataclass
class Operation:
    line: int
    name: str
    result: str | None
    args: list
    annotation: str | None
    effects: tuple[str, ...]


@dataclass
class Module:
    name: str
    ops: list[Operation]


def _scan_state(text: str, start: int = 0) -> tuple[int, bool]:
    """Return (paren depth, in_string) while ignoring strings and comments."""
    depth = 0
    quoted = False
    escaped = False
    i = start
    while i < len(text):
        c = text[i]
        if quoted:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                quoted = False
        else:
            if c == '"':
                quoted = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth < 0:
                    raise DialectError("unexpected ')'")
        i += 1
    return depth, quoted


def _strip_comment(line: str) -> str:
    quoted = False
    escaped = False
    for i, c in enumerate(line):
        if quoted:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == "/" and i + 1 < len(line) and line[i + 1] == "/":
            return line[:i]
    return line


def _logical_lines(text: str) -> Iterable[tuple[int, str]]:
    buf: list[str] = []
    start = 0
    depth = 0
    quoted = False
    for number, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw)
        if not line.strip() and not buf:
            continue
        if not buf:
            start = number
        buf.append(line)
        depth, quoted = _scan_state("\n".join(buf))
        if depth == 0 and not quoted:
            yield start, "\n".join(buf).strip()
            buf = []
    if buf:
        raise DialectError("unclosed operation or string", start)


def _split_annotation(rest: str) -> tuple[str, str | None]:
    quoted = False
    escaped = False
    depth = 0
    for i, c in enumerate(rest):
        if quoted:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == ":" and depth == 0:
            return rest[:i], rest[i + 1:].strip()
    return rest, None


def parse(text: str) -> Module:
    module_name: str | None = None
    ops: list[Operation] = []
    closed = False
    for line, logical in _logical_lines(text):
        s = logical.strip()
        if not s:
            continue
        if closed:
            raise DialectError("content after module close", line)
        m = _HEADER.fullmatch(s)
        if m:
            if module_name is not None:
                raise DialectError("duplicate space.module", line)
            module_name = m.group(1) or "anonymous"
            continue
        if s == "}":
            if module_name is None:
                raise DialectError("module close before header", line)
            closed = True
            continue
        if module_name is None:
            raise DialectError("operation before space.module header", line)
        m = _OP.fullmatch(s)
        if not m:
            raise DialectError("expected '%result = space.op ...' or 'space.op ...'", line)
        result = m.group(1)
        name = m.group(2)
        spec = OPS.get(name)
        if spec is None:
            raise DialectError(f"unknown operation space.{name}", line)
        rest, annotation = _split_annotation(m.group(3))
        try:
            args = loads_many(rest)
        except ValueError as exc:
            raise DialectError(f"cannot parse arguments: {exc}", line) from exc
        ops.append(Operation(line, name, result, args, annotation, spec.effects))
    if module_name is None:
        raise DialectError("missing space.module header")
    if not closed:
        raise DialectError("missing closing '}'")
    if not ops:
        raise DialectError("module has no operations")
    return Module(module_name, ops)


def _ssa(value) -> bool:
    return isinstance(value, Symbol) and str(value).startswith("%")


def _name(value) -> bool:
    return isinstance(value, (str, Symbol)) and not _ssa(value) and str(value) != ""


def _safe_dump(value) -> str:
    try:
        return dumps(value)
    except (TypeError, ValueError) as exc:
        raise DialectError(f"value cannot be lowered: {value!r}") from exc


def _check_arg(kind: str, value, line: int, seen: set[str]) -> None:
    if kind == "state":
        if not _ssa(value):
            raise DialectError("state operand must be an SSA result like %s0", line)
        if str(value)[1:] not in seen:
            raise DialectError(f"use before definition: {value}", line)
    elif kind in ("name", "label"):
        if not _name(value):
            raise DialectError(f"{kind} must be a non-empty symbol or string", line)
        _safe_dump(value)
    elif kind == "list":
        if not isinstance(value, list):
            raise DialectError("expected a list argument", line)
    elif kind == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            raise DialectError("expected an integer argument", line)
    elif kind == "bool":
        if not (value is True or value is False or
                (isinstance(value, Symbol) and str(value) in ("true", "false"))):
            raise DialectError("expected true or false", line)
    else:
        raise AssertionError(kind)


def verify(module: Module) -> Module:
    seen: set[str] = set()
    for op in module.ops:
        spec = OPS[op.name]
        if len(op.args) != len(spec.args):
            raise DialectError(
                f"space.{op.name} expects {len(spec.args)} arguments, got {len(op.args)}",
                op.line)
        if op.annotation is not None and op.annotation != SPACE_TYPE:
            raise DialectError(f"unsupported result type {op.annotation!r}", op.line)
        if spec.result and not op.result:
            raise DialectError(f"space.{op.name} requires an SSA result", op.line)
        if not spec.result and op.result:
            raise DialectError(f"space.{op.name} has no result", op.line)
        if op.result:
            name = op.result[1:]
            if name in seen:
                raise DialectError(f"duplicate SSA result {op.result}", op.line)
        for kind, value in zip(spec.args, op.args):
            _check_arg(kind, value, op.line, seen)
        if op.name == "run":
            budget = op.args[1]
            if budget < 0 or budget > 20000:
                raise DialectError("run budget must be in 0..20000", op.line)
        if op.result:
            seen.add(op.result[1:])
    return module


def _lit(value) -> str:
    return "'" + _safe_dump(value)


def _var(value: Symbol) -> str:
    return "dialect-" + str(value)[1:]


def lower(module: Module) -> str:
    verify(module)
    lines: list[str] = [
        f";;; lowered from space dialect module @{module.name}",
        ";;; Maru remains the reference interpreter and proof checker.",
    ]
    for op in module.ops:
        a = op.args
        if op.name == "new":
            expr = "(s79-new)"
        elif op.name == "define":
            expr = f"(d79-define {_var(a[0])} {_lit(a[1])} {_lit(a[2])} {_lit(a[3])})"
        elif op.name == "use":
            expr = f"(d79-use {_var(a[0])} {_lit(a[1])} {_lit(a[2])} {_lit(a[3])})"
        elif op.name == "prove":
            expr = f"(s79-proof-job {_var(a[0])} {_lit(a[1])} {_lit(a[2])})"
        elif op.name == "program":
            expr = f"(s79-program-job {_var(a[0])} {_lit(a[1])} {_lit(a[2])})"
        elif op.name == "interpolate":
            expr = (f"(i79-interpolate {_var(a[0])} {_lit(a[1])} {_lit(a[2])} "
                    f"{_lit(a[3])} {_lit(a[4])})")
        elif op.name == "beth":
            expr = (f"(i79-beth {_var(a[0])} {_lit(a[1])} {_lit(a[2])} "
                    f"{_lit(a[3])} {_lit(a[4])})")
        elif op.name == "run":
            expr = f"(s79-run {_var(a[0])} {a[1]})"
        elif op.name == "resume":
            flag = a[2] if a[2] is True or a[2] is False else str(a[2])
            expr = f"(s79-program-resume {_var(a[0])} {_lit(a[1])} {str(flag).lower()})"
        elif op.name == "dump":
            lines.append(f"(dump (list {_lit(a[1])} {_var(a[0])})) (print \"\\n\")")
            continue
        elif op.name == "job":
            lines.append(f"(dump (list {_lit(a[1])} (s79-job {_var(a[0])} {_lit(a[2])}))) "
                         "(print \"\\n\")")
            continue
        elif op.name == "definitions":
            lines.append(f"(dump (list {_lit(a[1])} (dlm-nth {_var(a[0])} 12))) (print \"\\n\")")
            continue
        else:
            raise AssertionError(op.name)
        if op.result:
            lines.append(f"(define {_var(op.result)} {expr})")
        else:
            lines.append(expr)
    return "\n".join(lines) + "\n"


def format_module(module: Module) -> str:
    """Canonical dialect text; SSA operands are not S-expression symbols."""
    verify(module)
    lines = [f"space.module @{module.name} {{"]
    for op in module.ops:
        prefix = f"{op.result} = " if op.result else ""
        args = " ".join(str(arg) if kind == "state" else _safe_dump(arg)
                        for kind, arg in zip(OPS[op.name].args, op.args))
        suffix = f" : {SPACE_TYPE}" if OPS[op.name].result else ""
        lines.append(f"  {prefix}space.{op.name}" + (f" {args}" if args else "") + suffix)
    lines.append("}")
    return "\n".join(lines) + "\n"


def parse_file(path: str | Path) -> Module:
    return verify(parse(Path(path).read_text(encoding="utf-8")))


def run_file(path: str | Path) -> str:
    source = lower(parse_file(path))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".l", encoding="utf-8") as driver:
        driver.write(source)
        driver.flush()
        try:
            proc = subprocess.run(
                [str(ROOT / "scripts/run.sh"), "proof", driver.name],
                capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("lowered Maru exceeded 120 seconds") from exc
    if proc.returncode:
        raise RuntimeError(f"lowered Maru failed ({proc.returncode}):\n{proc.stderr[:4000]}\n{proc.stdout[:4000]}")
    return proc.stdout


def explain(module: Module) -> str:
    verify(module)
    rows = [f"module @{module.name}"]
    for op in module.ops:
        result = f"{op.result} = " if op.result else ""
        rows.append(f"  {op.line:4d} {result}space.{op.name} "
                    f"effects={','.join(op.effects)}")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("verify", "lower", "run", "explain", "format"):
        p = sub.add_parser(name)
        p.add_argument("file")
    ns = parser.parse_args(argv)
    try:
        module = parse_file(ns.file)
        if ns.cmd == "verify":
            print(f"verified @{module.name}: {len(module.ops)} operations")
        elif ns.cmd == "lower":
            print(lower(module), end="")
        elif ns.cmd == "run":
            print(run_file(ns.file), end="")
        elif ns.cmd == "explain":
            print(explain(module))
        elif ns.cmd == "format":
            print(format_module(module), end="")
    except (DialectError, OSError, RuntimeError) as exc:
        print(f"space-dialect: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
