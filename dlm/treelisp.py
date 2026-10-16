"""A bounded, non-authoritative Scheme-like controller over typed IR-TREEs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from . import kernel
from .ir import Form, children, field, head, loads, node_id, walk
from .learn import (choice, commit_transition, evaluate, learn_round, noul, rank,
                    stop_status)


class EvalError(ValueError):
    pass


@dataclass
class _Fuel:
    left: int

    def spend(self):
        self.left -= 1
        if self.left < 0:
            raise EvalError("fuel-exhausted")


def _truth(value: Form) -> bool:
    return value not in (False, None, (), ("noul",))


def _pattern(pattern: Form, value: Form, env: dict[str, Form]) -> bool:
    if isinstance(pattern, str) and pattern.startswith("?"):
        name = pattern[1:]
        if name in env:
            return env[name] == value
        env[name] = value
        return True
    if pattern == "_":
        return True
    if isinstance(pattern, tuple) and isinstance(value, tuple):
        return len(pattern) == len(value) and all(
            _pattern(left, right, env) for left, right in zip(pattern, value))
    return pattern == value


def _select(tree: Form, pattern: Form) -> Form:
    matches = []
    for value in walk(tree):
        bindings: dict[str, Form] = {}
        if _pattern(pattern, value, bindings):
            matches.append(("match", *(("bind", key, bindings[key])
                                        for key in sorted(bindings))))
    return ("matches", *matches)


def evaluate_expr(expr: Form, state: Form, env: Mapping[str, Form] | None = None,
                  fuel: int = 10000) -> Form:
    remaining = _Fuel(fuel)

    def ev(value: Form, scope: dict[str, Form]) -> Form:
        remaining.spend()
        if not isinstance(value, tuple):
            return scope.get(value, value) if isinstance(value, str) else value
        op = head(value)
        args = children(value)
        if op == "quote":
            if len(args) != 1:
                raise EvalError("quote expects one value")
            return args[0]
        if op == "if":
            if len(args) != 3:
                raise EvalError("if expects condition, true and false branches")
            return ev(args[1] if _truth(ev(args[0], scope)) else args[2], scope)
        if op == "begin":
            result: Form = None
            for arg in args:
                result = ev(arg, scope)
            return result
        if op == "let":
            if len(args) != 2 or not isinstance(args[0], tuple) or args[0][0] != "bindings":
                raise EvalError("let expects (bindings (bind NAME EXPR)...) and a body")
            local = dict(scope)
            for binding in args[0][1:]:
                if (not isinstance(binding, tuple) or len(binding) != 3
                        or binding[0] != "bind" or not isinstance(binding[1], str)):
                    raise EvalError("malformed binding")
                local[binding[1]] = ev(binding[2], local)
            return ev(args[1], local)
        if op == "match":
            if len(args) < 2:
                raise EvalError("match expects a value and cases")
            subject = ev(args[0], scope)
            for case in args[1:]:
                if not isinstance(case, tuple) or len(case) != 3 or case[0] != "case":
                    raise EvalError("malformed match case")
                bindings: dict[str, Form] = {}
                if _pattern(case[1], subject, bindings):
                    return ev(case[2], {**scope, **bindings})
            return ("noul",)
        if op == "equal?":
            return len(args) == 2 and ev(args[0], scope) == ev(args[1], scope)
        if op == "not":
            return not _truth(ev(args[0], scope))
        if op == "and":
            return all(_truth(ev(arg, scope)) for arg in args)
        if op == "or":
            return any(_truth(ev(arg, scope)) for arg in args)
        if op == "list":
            return ("list", *(ev(arg, scope) for arg in args))
        if op == "head":
            return head(ev(args[0], scope))
        if op == "children":
            return ("children", *children(ev(args[0], scope)))
        if op == "field":
            tree = ev(args[0], scope)
            name = ev(args[1], scope)
            if not isinstance(name, str):
                raise EvalError("field name must be a symbol")
            return field(tree, name)
        if op == "select":
            return _select(ev(args[0], scope), ev(args[1], scope))
        if op == "node-id":
            return node_id(ev(args[0], scope))

        # Capability-limited DLM operations. None directly asserts a fact or rule.
        if op == "state":
            return state
        if op == "run-programs":
            from .language import execute_programs
            return ("candidates", *execute_programs(state))
        if op == "candidates":
            return field(state, "candidates")
        if op == "rank":
            actions = field(state, "candidates")[1:] if not args else tuple(
                ev(args[0], scope)[1:])
            return ("ranked", *rank(state, actions))
        if op == "choice":
            return choice(state)
        if op == "noul":
            if len(args) != 1:
                raise EvalError("noul expects one candidate")
            return noul(state, ev(args[0], scope))
        if op == "score":
            if len(args) != 1:
                raise EvalError("score expects a list of levels")
            from .learn import ordinal_score
            levels = ev(args[0], scope)
            return ordinal_score(state, levels[1:])
        if op == "query":
            if len(args) != 1:
                raise EvalError("query expects one atom")
            return kernel.query(state, ev(args[0], scope))
        if op == "prove":
            if len(args) != 1:
                raise EvalError("prove expects one atom")
            return kernel.state_prove(state, ev(args[0], scope))
        if op == "test-rule":
            if len(args) != 1:
                raise EvalError("test-rule expects one candidate")
            return evaluate(state, ev(args[0], scope))
        if op == "step":
            budget = int(ev(args[0], scope)) if args else 64
            return learn_round(state, budget=budget)
        if op == "stop-status":
            return stop_status(state)
        raise EvalError(f"unknown or forbidden TreeLisp operation: {op}")

    return ev(expr, dict(env or {}))


def run(program: str | Form, state: Form, *, fuel: int = 10000) -> Form:
    """Evaluate one command and commit only a valid IR transition."""
    expression = loads(program) if isinstance(program, str) else program
    value = evaluate_expr(expression, state, fuel=fuel)
    if isinstance(value, tuple) and value and value[0] == "transition":
        after = commit_transition(state, value)
        return ("repl-result", ("value", value), ("state", after))
    return ("repl-result", ("value", value), ("state", state))
