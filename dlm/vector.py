"""DLM v0.0026 -- a grounded representation vector for one IR tree (untrusted).

v0.0025 tried to place IR trees in a learned 3D lattice over *hashed* features.
The model could not read the result: a hashed code has no named coordinates and a
lattice cell is an opaque prototype.  This module fixes the representation half.

An IR tree maps to a **symbolic vector** whose every coordinate is a *named
symbol the model already knows* -- a role plus a token taken from the tree -- and
which reverses exactly back to the tree.  No hashing, no lost order, no opaque
dims::

    tree  --tree_vector-->  SymbolVector  --vector_tree-->  tree   (exact inverse)

A ``SymbolVector`` is sparse and interpretable.  Its coordinates print as
``rel[0]=born``, ``subj[0]=alan``, ``order=0`` ... so a person or the model can
read it.  Adding vectors *bundles* trees (superposition) and ``restrict(role)``
*unbinds* one role, so composing many trees is a later step built on this same
algebra.

The model understands the vector because its coordinates are exactly the
structural symbols the reader/kernel already uses (:func:`dlm.ssl.tree_features`):
the vector reads as logic and only ever *proposes*; the kernel still asserts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from dlm import Form, SexpError, Sym, dump, parse
from dlm.ssl import ir_form, ir_get, is_ir, tree_features

__all__ = [
    "ROLES",
    "Symbol",
    "SymbolVector",
    "tree_vector",
    "vector_tree",
    "vector_symbols",
    "vector_features",
    "vector_form",
    "vector_from_form",
    "vector_sexp",
    "vector_from_sexp",
    "Basis",
    "encode",
    "decode",
    "bundle",
    "restrict",
]

#: The declared role axes of the representation, in canonical order.
ROLES: Tuple[str, ...] = ("name", "rel", "subj", "obj", "order", "extra")
_ROLE_INDEX: Dict[str, int] = {r: i for i, r in enumerate(ROLES)}


@dataclass(frozen=True)
class Symbol:
    """One named coordinate of the representation: ``role[index]=token``."""

    role: str
    index: int
    token: str

    def __post_init__(self) -> None:
        if self.role not in _ROLE_INDEX:
            raise ValueError(f"unknown role {self.role!r}; expected one of {ROLES}")
        if self.index < 0:
            raise ValueError(f"index must be >= 0, got {self.index}")
        if not isinstance(self.token, str):
            raise TypeError(f"token must be a str, got {self.token!r}")

    def key(self) -> str:
        if self.role in ("name", "order"):
            return f"{self.role}={self.token}"
        return f"{self.role}[{self.index}]={self.token}"

    def __str__(self) -> str:
        return self.key()

    def sort_key(self) -> Tuple[int, int, str]:
        return (_ROLE_INDEX[self.role], self.index, self.token)


@dataclass(frozen=True)
class SymbolVector:
    """A sparse, ordered, grounded vector: symbols plus their weights.

    The symbols are sorted by :meth:`Symbol.sort_key`, so iteration is
    deterministic without relying on dict order.
    """

    symbols: Tuple[Symbol, ...]
    weights: Tuple[float, ...] = ()

    def __post_init__(self) -> None:
        syms = tuple(self.symbols)
        weights = (1.0,) * len(syms) if not self.weights else tuple(float(w) for w in self.weights)
        if len(weights) != len(syms):
            raise ValueError(f"{len(syms)} symbols but {len(weights)} weights")
        pairs = sorted(zip(syms, weights), key=lambda sw: sw[0].sort_key())
        object.__setattr__(self, "symbols", tuple(s for s, _ in pairs))
        object.__setattr__(self, "weights", tuple(w for _, w in pairs))

    def __len__(self) -> int:
        return len(self.symbols)

    def items(self) -> Tuple[Tuple[Symbol, float], ...]:
        return tuple(zip(self.symbols, self.weights))

    def explain(self) -> Tuple[Tuple[str, float], ...]:
        """The vector as readable ``(symbol, weight)`` pairs."""
        return tuple((str(s), round(w, 6)) for s, w in zip(self.symbols, self.weights))

    def restrict(self, role: str) -> "SymbolVector":
        """Unbind one role: the sub-vector for ``role`` only."""
        if role not in _ROLE_INDEX:
            raise ValueError(f"unknown role {role!r}")
        keep = [(s, w) for s, w in zip(self.symbols, self.weights) if s.role == role]
        return SymbolVector(tuple(s for s, _ in keep), tuple(w for _, w in keep))

    def tokens(self, role: Optional[str] = None) -> Tuple[str, ...]:
        return tuple(s.token for s in self.symbols if role is None or s.role == role)

    def roles(self) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(s.role for s in self.symbols))

    def __add__(self, other: "SymbolVector") -> "SymbolVector":
        return bundle(self, other)


def _vector(pairs: Iterable[Tuple[Symbol, float]]) -> SymbolVector:
    """Merge equal symbols (summing weights) and sort into canonical order."""
    merged: Dict[str, Tuple[Symbol, float]] = {}
    for sym, w in pairs:
        key = sym.key()
        if key in merged:
            s0, w0 = merged[key]
            merged[key] = (s0, w0 + float(w))
        else:
            merged[key] = (sym, float(w))
    ordered = sorted(merged.values(), key=lambda sw: sw[0].sort_key())
    return SymbolVector(tuple(s for s, _ in ordered), tuple(w for _, w in ordered))


def bundle(a: SymbolVector, b: SymbolVector) -> SymbolVector:
    """Superpose two trees: union of coordinates, weights added."""
    return _vector(list(zip(a.symbols, a.weights)) + list(zip(b.symbols, b.weights)))


def restrict(v: SymbolVector, role: str) -> SymbolVector:
    """Unbind one role of ``v`` (see :meth:`SymbolVector.restrict`)."""
    return v.restrict(role)


# ============================================================================
# tree <-> vector (exact, grounded)
# ============================================================================
def tree_vector(tree: Form) -> SymbolVector:
    """Encode one IR tree as a grounded symbolic vector (interpretable, lossless)."""
    if not is_ir(tree):
        raise SexpError(f"not an ir tree: {tree!r}")
    pairs: List[Tuple[Symbol, float]] = []
    name = str(tree[1])
    if name and name != "-":
        pairs.append((Symbol("name", 0, name), 1.0))
    for role, head in (("rel", "rel"), ("subj", "subj"), ("obj", "obj")):
        for i, tok in enumerate(ir_get(tree, head)):
            pairs.append((Symbol(role, i, str(tok)), 1.0))
    pairs.append((Symbol("order", 0, str(tree[5])), 1.0))
    for j, extra in enumerate(tree[6:]):
        pairs.append((Symbol("extra", j, dump(extra)), 1.0))
    return _vector(pairs)


def _sequence(vector: SymbolVector, role: str) -> Tuple[str, ...]:
    pairs = sorted((s.index, s.token) for s in vector.symbols if s.role == role)
    indices = [i for i, _ in pairs]
    if indices != list(range(len(indices))):
        raise SexpError(f"{role} indices are not contiguous 0..n-1: {pairs!r}")
    return tuple(t for _, t in pairs)


def vector_tree(v: SymbolVector) -> Form:
    """Decode a symbolic vector back to the exact IR tree (inverse of tree_vector)."""
    if not isinstance(v, SymbolVector):
        raise SexpError(f"not a SymbolVector: {v!r}")
    name, order, extras = "-", 0, []
    for s in v.symbols:
        if s.role == "name":
            name = s.token
        elif s.role == "order":
            try:
                order = int(s.token)
            except ValueError as exc:
                raise SexpError(f"bad order token {s.token!r}") from exc
        elif s.role == "extra":
            forms = parse(s.token)
            if len(forms) != 1:
                raise SexpError(f"bad extra token {s.token!r}")
            extras.append(forms[0])
    base = ir_form(_sequence(v, "rel"), _sequence(v, "subj"), _sequence(v, "obj"), order, name)
    return base + tuple(extras)


def vector_symbols(v: SymbolVector) -> Tuple[str, ...]:
    """The coordinates as readable strings: ``rel[0]=born`` ..."""
    return tuple(str(s) for s in v.symbols)


def vector_features(v: SymbolVector) -> Tuple[str, ...]:
    """Named features a reader/kernel can consume (role+token, and role lengths).

    These are the *same* structural symbols :func:`dlm.ssl.tree_features` exposes
    -- the representation does not invent a private vocabulary -- so the model can
    reason over the vector directly.
    """
    feats: List[str] = [f"{s.role}={s.token}" for s in v.symbols]
    for role in ("rel", "subj", "obj"):
        feats.append(f"{role}_len={len(v.restrict(role))}")
    return tuple(feats)


# ============================================================================
# one form -- a vector serialises like atoms, rules and theories
# ============================================================================
def vector_form(v: SymbolVector) -> Form:
    """``(vec (sym <role> <index> <weight> <token>) ...)`` -- one S-expr tree."""
    parts: List[Form] = [Sym("vec")]
    for s, w in zip(v.symbols, v.weights):
        parts.append((Sym("sym"), Sym(s.role), Sym(str(s.index)), Sym(repr(float(w))), s.token))
    return tuple(parts)


def vector_from_form(form: Form) -> SymbolVector:
    """Read a ``(vec ...)`` form back into a :class:`SymbolVector`."""
    if not isinstance(form, tuple) or not form or form[0] != Sym("vec"):
        raise SexpError(f"not a vec form: {form!r}")
    pairs: List[Tuple[Symbol, float]] = []
    for node in form[1:]:
        if not isinstance(node, tuple) or len(node) != 5 or node[0] != Sym("sym"):
            raise SexpError(f"not a sym node: {node!r}")
        try:
            role, index, weight, token = str(node[1]), int(str(node[2])), float(str(node[3])), str(node[4])
        except ValueError as exc:
            raise SexpError(f"bad sym node: {node!r}") from exc
        pairs.append((Symbol(role, index, token), weight))
    return _vector(pairs)


def vector_sexp(v: SymbolVector) -> str:
    """Canonical S-expr text of the vector."""
    return dump(vector_form(v))


def vector_from_sexp(text: str) -> SymbolVector:
    """Parse exactly one ``(vec ...)`` form into a :class:`SymbolVector`."""
    forms = parse(text)
    if len(forms) != 1:
        raise SexpError(f"expected exactly one vec form, got {len(forms)}")
    return vector_from_form(forms[0])


# ============================================================================
# a fixed basis: the same vector, now as dense named coordinates
# ============================================================================
@dataclass(frozen=True)
class Basis:
    """A fixed, ordered list of symbols -- a coordinate system for the vectors.

    Every coordinate has a name (its :class:`Symbol`), so a dense encoding is
    still *grounded*: the model can look up coordinate ``i`` and read which
    symbol it is.  This is what a hashed code cannot offer.
    """

    symbols: Tuple[Symbol, ...]

    def __post_init__(self) -> None:
        syms = tuple(self.symbols)
        if len({s.key() for s in syms}) != len(syms):
            raise ValueError("basis has duplicate symbols")
        object.__setattr__(self, "symbols", tuple(sorted(syms, key=lambda s: s.sort_key())))

    def __len__(self) -> int:
        return len(self.symbols)

    def index(self) -> Dict[str, int]:
        return {s.key(): i for i, s in enumerate(self.symbols)}

    def index_of(self, sym: Symbol) -> int:
        try:
            return self.index()[sym.key()]
        except KeyError as exc:
            raise SexpError(f"symbol {sym} is outside the basis") from exc

    @classmethod
    def of(cls, vectors: Iterable[SymbolVector]) -> "Basis":
        """Build the sorted union of every symbol seen in ``vectors``."""
        seen: Dict[str, Symbol] = {}
        for v in vectors:
            for s in v.symbols:
                seen.setdefault(s.key(), s)
        return cls(tuple(seen.values()))


def encode(v: SymbolVector, basis: Basis) -> Tuple[float, ...]:
    """Dense coordinates of ``v`` over ``basis`` (a named coordinate per index)."""
    idx = basis.index()
    out = [0.0] * len(basis)
    for s, w in zip(v.symbols, v.weights):
        i = idx.get(s.key())
        if i is None:
            raise SexpError(f"symbol {s} is outside the basis")
        out[i] = float(w)
    return tuple(out)


def decode(dense: Sequence[float], basis: Basis) -> SymbolVector:
    """Sparse grounded vector of dense ``coordinates`` over ``basis``."""
    if len(dense) != len(basis):
        raise SexpError(f"expected {len(basis)} coordinates, got {len(dense)}")
    pairs = [(s, float(w)) for s, w in zip(basis.symbols, dense) if float(w) != 0.0]
    return _vector(pairs)
