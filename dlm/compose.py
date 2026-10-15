"""DLM v0.0047 -- compositional / architectural / analogical abstraction (untrusted).

v0.0041 (:mod:`dlm.generalize`) mines conjunctions of *unary subject features*
(``backpropagates(X) ∧ optimizes(X)``).  That is propositional: one subject, no
structure.  This layer climbs the abstraction ladder:

* **L5 composition** -- patterns over *relational structure* with interface
  variables (``calls(X,Y), calls(Y,Z)``: "X delegates to a routine that itself
  calls things").  A pattern is a conjunctive query; its extension on a program
  is the set of X that satisfy it.
* **L6 architecture** -- recurring *ordered* motifs in a program's operation
  pipelines (the forward-pass skeleton).
* **L9 transfer/analogy** -- the same patterns evaluated on held-out programs.

Nothing here asserts truth: a pattern is a *hypothesis* and the kernel decides
whether it fires when the pattern is used.  Candidates are proposed, then kept
only if non-degenerate and irredundant w.r.t. the single-literal baselines.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import Atom, Const, Var

__all__ = [
    "Pattern", "pattern_candidates", "pattern_extension", "induce_patterns",
    "motifs", "pattern_key", "is_connected",
]

VARS = ("X", "Y", "Z")
# Structural relations the corpus shares.  (predicate, arity)
STRUCTURAL_RELATIONS = [("calls", 2), ("before", 2), ("step_of", 2),
                        ("creates", 2), ("method_of", 2), ("defines", 2)]


@dataclass(frozen=True)
class Pattern:
    body: Tuple[Tuple[str, Tuple[str, ...]], ...]   # ((pred, (vars...)), ...)

    def literals(self) -> List[str]:
        return [f"{p}(" + ",".join(a) + ")" for p, a in self.body]


def pattern_key(p: Pattern) -> str:
    return ";".join(p.literals())


def _lit_templates(relations, *, require_x: bool = False) -> List[Tuple[str, Tuple[str, ...]]]:
    out: List[Tuple[str, Tuple[str, ...]]] = []
    for pred, arity in relations:
        for args in product(VARS, repeat=arity):
            if require_x and "X" not in args:
                continue
            out.append((pred, args))
    return out


def pattern_candidates(relations=STRUCTURAL_RELATIONS, *, max_body: int = 2,
                       max_lits: int = 64) -> List[Pattern]:
    """Propose bounded CONNECTED conjunctive patterns that mention X (deterministic).

    Auxiliary literals that do not mention X (e.g. ``calls(Y,Z)``) are allowed:
    they are what makes a body *compositional* rather than a pair of facts about X.
    """
    lits = _lit_templates(relations)
    if len(lits) > max_lits:
        lits = lits[:max_lits]
    out: List[Pattern] = []
    for r in range(2, max_body + 1):
        for combo in combinations(lits, r):
            if len(set(combo)) < r:                 # no literal repeated
                continue
            if not any("X" in args for _p, args in combo):
                continue
            counts: Dict[str, int] = {}
            for _p, args in combo:
                for v in set(args):
                    counts[v] = counts.get(v, 0) + 1
            if not any(c >= 2 for c in counts.values()):   # must be connected
                continue
            out.append(Pattern(tuple(combo)))
    return out


def is_connected(p: Pattern) -> bool:
    """True when a variable is shared by two literals (a real composition,
    e.g. ``calls(X,Y),calls(Y,Z)``), not merely two facts about X."""
    seen: Dict[str, int] = {}
    for _pred, args in p.body:
        for v in set(args):
            seen[v] = seen.get(v, 0) + 1
    return any(v != "X" and c >= 2 for v, c in seen.items())


def _sat(body, facts, init: Dict[str, Const]) -> Optional[Dict[str, Const]]:
    by_pred: Dict[str, list] = {}
    for a in facts:
        by_pred.setdefault(a.pred, []).append(a)

    def rec(i: int, s: Dict[str, Const]):
        if i == len(body):
            return dict(s)
        pred, args = body[i]
        for a in by_pred.get(pred, ()):
            if len(a.args) != len(args):
                continue
            s2, ok = dict(s), True
            for name, g in zip(args, a.args):
                if name in s2:
                    if s2[name] != g.name:
                        ok = False
                        break
                else:
                    s2[name] = g.name
            if ok:
                r = rec(i + 1, s2)
                if r is not None:
                    return r
        return None

    return rec(0, dict(init))


def pattern_extension(p: Pattern, facts: Iterable[Atom]) -> Tuple[str, ...]:
    """Constants c for which ``body`` is satisfiable with X := c (sorted)."""
    facts = list(facts)
    domain = sorted({t.name for a in facts for t in a.args})
    hits = [c for c in domain if _sat(p.body, facts, {"X": c}) is not None]
    return tuple(hits)


def _ext_tuple(p: Pattern, kb_facts: Dict[str, Iterable[Atom]]) -> Tuple:
    return tuple(pattern_extension(p, kb_facts[n]) for n in sorted(kb_facts))


def induce_patterns(kb_facts: Dict[str, Iterable[Atom]], *, min_support: int = 3,
                    max_body: int = 2, max_patterns: int = 8) -> List[Pattern]:
    """Keep non-degenerate, irredundant patterns recurring across >= min_support programs."""
    programs = sorted(kb_facts)
    facts = {n: list(kb_facts[n]) for n in programs}
    cands = pattern_candidates(max_body=max_body)
    singles = {_ext_tuple(Pattern((lit,)), facts)
               for lit in _lit_templates(STRUCTURAL_RELATIONS, require_x=True)}
    best: Dict[Tuple, Pattern] = {}
    for p in cands:
        ext = _ext_tuple(p, facts)
        support = sum(1 for e in ext if e)
        if support < min_support or not any(ext):
            continue
        if ext in singles:                                # degenerate vs one relation
            continue
        red = False
        for i in range(len(p.body)):                      # irredundant?
            if _ext_tuple(Pattern(p.body[:i] + p.body[i + 1:]), facts) == ext:
                red = True
                break
        if red:
            continue
        if ext not in best or (len(p.body), pattern_key(p)) < (
                len(best[ext].body), pattern_key(best[ext])):
            best[ext] = p
    ordered = sorted(best.items(),
                     key=lambda kv: (0 if is_connected(kv[1]) else 1,
                                     -len({v for _p, args in kv[1].body for v in args}),
                                     -sum(1 for e in kv[0] if e),
                                     len(kv[1].body), pattern_key(kv[1])))
    return [p for _ext, p in ordered[:max_patterns]]


def motifs(pipelines: Dict[str, Sequence[str]], *, min_len: int = 2, max_len: int = 4,
           min_support: int = 2, top: int = 8) -> List[dict]:
    """Recurring contiguous operation subsequences across programs (L6)."""
    counts: Dict[Tuple[str, ...], int] = {}
    for name, pipe in pipelines.items():
        seen = set()
        for L in range(min_len, max_len + 1):
            for i in range(len(pipe) - L + 1):
                g = tuple(pipe[i:i + L])
                if g not in seen:
                    seen.add(g)
                    counts[g] = counts.get(g, 0) + 1
    ranked = [(g, c) for g, c in counts.items() if c >= min_support]
    ranked.sort(key=lambda t: (-t[1], -len(t[0]), t[0]))
    return [{"ops": list(g), "support": c} for g, c in ranked[:top]]


def transfer_patterns(patterns: Sequence[Pattern],
                      facts_by_prog: Dict[str, Iterable[Atom]]) -> Dict[str, dict]:
    """Apply the (corpus-induced) patterns to held-out programs (L9)."""
    out: Dict[str, dict] = {}
    for idx, p in enumerate(patterns):
        out[f"pattern{idx}"] = {
            "literals": p.literals(),
            "hits": {n: list(pattern_extension(p, facts_by_prog[n])) for n in sorted(facts_by_prog)},
        }
    return out