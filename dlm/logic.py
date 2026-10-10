"""Semantic normal form: the function-free target of sentence -> logic conversion.

This is the foundation of v0.0006. Four ideas, taken directly from the design
note, are the whole of it:

  1. The atomic unit is a predicate applied to **roles** (a frame), not a bag of
     words. "A calls B" and "B calls A" are different atoms.
  2. The normal form is **function-free**: an atom's arguments are only constants
     and variables. A relative or embedded clause is *flattened* into extra
     atoms, never nested.
  3. A predicate's **schema** (arity + role order) is the general, transferable
     part. The predicate *symbol* is the instance; the schema is what recurs
     across domains.
  4. Anything that cannot be normalized is **abstained on, never guessed**.

    sentence --(reader, module 3)--> Frame --(normalize)--> Literal
                                      pred + {role: filler}    Atom + sign

Negation is not a derivable symbol in Horn logic, so it is carried as a `sign`
on a `Literal` (and later kept in a side table), not as a predicate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple, Union

__all__ = [
    "Const",
    "Var",
    "Term",
    "Atom",
    "Literal",
    "Rule",
    "Schema",
    "Frame",
    "SchemaRegistry",
]


# -- terms -----------------------------------------------------------------
@dataclass(frozen=True)
class Const:
    """A constant (an individual, a named entity)."""

    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Var:
    """A logical variable. ``?`` is added only in the string form."""

    name: str

    def __str__(self) -> str:
        return "?" + self.name


Term = Union[Const, Var]


# -- atoms and literals ----------------------------------------------------
@dataclass(frozen=True)
class Atom:
    """A function-free atom: a predicate applied to ordered terms."""

    pred: str
    args: Tuple[Term, ...] = ()

    def __post_init__(self) -> None:
        for a in self.args:
            if not isinstance(a, (Const, Var)):
                raise TypeError(
                    f"function-free: an atom argument must be Const or Var, got {a!r}"
                )

    @property
    def arity(self) -> int:
        return len(self.args)

    def is_ground(self) -> bool:
        return all(isinstance(a, Const) for a in self.args)

    def variables(self) -> Tuple[Var, ...]:
        return tuple(a for a in self.args if isinstance(a, Var))

    def __str__(self) -> str:
        return "(" + " ".join((self.pred, *(str(a) for a in self.args))) + ")"


@dataclass(frozen=True)
class Literal:
    """A normalized atom with a sign. ``negated=True`` is the *statement* "not atom".

    Horn logic cannot derive a negative, so the sign is metadata the engine and
    the KB side table use; it is not itself an atom.
    """

    atom: Atom
    negated: bool = False

    @property
    def sign(self) -> int:
        return -1 if self.negated else 1

    def is_ground(self) -> bool:
        return self.atom.is_ground()

    def __str__(self) -> str:
        return f"(not {self.atom})" if self.negated else str(self.atom)


# -- rules: the general laws -----------------------------------------------
@dataclass(frozen=True)
class Rule:
    """A definite Horn rule: ``head :- body``.

    ``body`` is a conjunction of positive atoms (function-free Horn). Negation is
    not part of a rule body; explicit negatives live in the KB side table. A
    rule is *safe*: every head variable must occur in a positive body atom, so
    forward chaining can ground the head.
    """

    head: Atom
    body: Tuple[Atom, ...] = ()
    name: Optional[str] = None

    def __post_init__(self) -> None:
        for b in self.body:
            if not isinstance(b, Atom):
                raise TypeError(f"a rule body must be atoms, got {b!r}")
        if not self.body:
            raise ValueError("a rule needs a non-empty body (use a fact instead)")
        head_vars = set(self.head.variables())
        body_vars = set()
        for b in self.body:
            body_vars.update(b.variables())
        if not head_vars <= body_vars:
            missing = head_vars - body_vars
            raise ValueError(f"unsafe rule: head variables not in body: {missing}")

    def variables(self) -> Tuple[Var, ...]:
        out = list(self.head.variables())
        for b in self.body:
            for v in b.variables():
                if v not in out:
                    out.append(v)
        return tuple(out)

    def __str__(self) -> str:
        parts = ["rule"]
        if self.name is not None:
            parts.append(self.name)
        parts.append(str(self.head))
        parts.extend(str(b) for b in self.body)
        return "(" + " ".join(parts) + ")"


# -- schema: the general part ----------------------------------------------
@dataclass(frozen=True)
class Schema:
    """A predicate's arity and role order. This is what generalizes between domains.

    The position of a role in ``roles`` is the position of its filler in the
    atom. Roles are what make argument order meaningful.
    """

    pred: str
    roles: Tuple[str, ...]

    def __post_init__(self) -> None:
        if len(set(self.roles)) != len(self.roles):
            raise ValueError(f"duplicate roles in schema for {self.pred!r}: {self.roles}")

    @property
    def arity(self) -> int:
        return len(self.roles)

    def index_of(self, role: str) -> int:
        """Position of ``role`` in the atom, or -1 if the schema has no such role."""
        try:
            return self.roles.index(role)
        except ValueError:
            return -1


# -- frame: the surface read -----------------------------------------------
@dataclass(frozen=True)
class Frame:
    """A predicate-argument frame read from a sentence.

    ``slots`` maps roles to fillers and is deliberately unordered: the schema
    decides the final argument order. A frame is *not yet* an atom -- it is the
    proposal that :meth:`SchemaRegistry.normalize` accepts or rejects.
    """

    pred: str
    slots: Tuple[Tuple[str, Term], ...] = ()
    negated: bool = False

    def __post_init__(self) -> None:
        names = [r for r, _ in self.slots]
        if len(set(names)) != len(names):
            raise ValueError(f"duplicate roles in frame {self.pred!r}: {names}")
        for _, filler in self.slots:
            if not isinstance(filler, (Const, Var)):
                raise TypeError(
                    f"function-free: a slot filler must be Const or Var, got {filler!r}"
                )

    def roles(self) -> frozenset:
        return frozenset(r for r, _ in self.slots)

    def __str__(self) -> str:
        sign = "not " if self.negated else ""
        body = ", ".join(f"{r}={t}" for r, t in self.slots)
        return f"{sign}{self.pred}({body})"


# -- normalization: frame -> literal, or abstain ---------------------------
class SchemaRegistry:
    """Predicate schemas, and the one operation that turns a frame into a Literal.

    ``normalize`` is the trust boundary of the conversion: an unknown predicate
    or a role mismatch yields ``None`` (abstain). It never invents a role or a
    predicate, and it never reorders fillers by guesswork -- only by the schema.
    """

    def __init__(self, schemas: Iterable[Schema] = ()) -> None:
        self._by_pred: Dict[str, Schema] = {}
        for s in schemas:
            self.add(s)

    def add(self, schema: Schema) -> "SchemaRegistry":
        self._by_pred[schema.pred] = schema
        return self

    def get(self, pred: str) -> Optional[Schema]:
        return self._by_pred.get(pred)

    def known(self) -> Tuple[str, ...]:
        return tuple(sorted(self._by_pred))

    def __len__(self) -> int:
        return len(self._by_pred)

    def __contains__(self, pred: object) -> bool:
        return pred in self._by_pred

    def normalize(self, frame: Frame) -> Optional[Literal]:
        """Order a frame's fillers by the schema. ``None`` means abstain."""
        schema = self._by_pred.get(frame.pred)
        if schema is None:
            return None
        if frame.roles() != set(schema.roles):
            return None
        filled: Mapping[str, Term] = dict(frame.slots)
        args = tuple(filled[role] for role in schema.roles)
        return Literal(Atom(frame.pred, args), frame.negated)