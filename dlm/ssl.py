"""Module: IR-SSL -- language self-supervision over an intermediate representation.

The language layer never touches logic directly.  Text and atoms meet at an
explicit **intermediate representation** (IR).  The canonical IR is a plain
**symbol tree** -- a ``Form``, the very same type atoms, rules and theories are
serialised to::

    (ir <name> (rel <cue>...) (subj <tok>...) (obj <tok>...) <order>)

The ``Frame`` dataclass is only a *view* over that tree (``ir_from_form``); a
reader may learn straight off the tree (``reader_tree_features``), so adding a
head to the vocabulary adds features without editing any feature table::

    sentence --frame_of/ir_of--> IR tree --rank--> Atom   (reading, NL -> logic)
    Atom --rank--> IR tree --render--> sentence           (realizing, logic -> NL)

In the tree, ``rel`` are the relational *cue* tokens -- the wording that selects
the predicate -- while ``subj``/``obj`` are argument-name tokens, or ``probe``
in a masked / de-identified view.  ``order`` records which mention came first.
Because the cue and the arguments are separated in the IR, a reader can be
trained on *wording* alone, which stops it collapsing onto an entity's majority
predicate.

Both directions are untrusted, dependency-free linear rankers.  Super
vision has exactly two label sources, and neither is human:

* **reading** -- distant supervision + the kernel.  A frame is anchored to a web
  fact; a candidate atom is positive iff the kernel entails it, every sibling is
  a negative.
* **realizing** -- bidirectional consistency.  A frame for an atom is positive
  iff the *current reader* reads it back to the same predicate.

Neither head asserts.  The trusted kernel still decides; IR-SSL only orders.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from random import Random
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import Atom, Const, Form, SexpError, Sym, dump, parse

__all__ = [
    "MASK", "Frame", "FRAMES", "content_tokens", "frame_of", "render",
    "reader_features", "surface_features", "realizer_features",
    "LinearRanker", "IrReader", "IrRealizer", "IrSupervisor",
    "aligned_examples", "supporting_sentence",
    "reader_recall_at_1", "macro_recall_at_1", "majority_baseline",
    "roundtrip_rate",
    "frame_to_form", "frame_from_form", "frame_sexp", "frame_from_sexp",
    # -- the symbol tree is the IR (v0.0023) -----------------------------
    "IR_HEAD", "ir_form", "is_ir", "ir_children", "ir_get", "ir_of",
    "ir_from_form", "ir_paths", "tree_features", "reader_tree_features",
    "aligned_tree_examples",
]

# The token substituted for an argument name in a masked / de-identified frame.
MASK = "probe"

_STOP = frozenset(
    {
        "the", "a", "an", "of", "in", "on", "at", "to", "for", "by", "with", "from",
        "is", "are", "was", "were", "am", "be", "been", "being", "and", "or", "but",
        "as", "that", "this", "these", "those", "it", "its", "he", "she", "they",
        "them", "his", "her", "their", "also", "who", "which", "where", "when",
        "one", "two", "has", "have", "had", "not", "no", "than", "then", "into",
        "during", "after", "over", "under", "while", "known", "using", "used",
    }
)


# ============================================================================
# 1. the intermediate representation
# ============================================================================
@dataclass(frozen=True)
class Frame:
    """A predicate-agnostic relational frame -- the IR.

    ``rel`` are the relational cue tokens, ``subject``/``obj`` the argument name
    tokens (or ``MASK``), ``order`` 0 when the subject mention precedes the
    object.  ``name`` is a surface-frame id when the frame comes from ``FRAMES``;
    it is empty for a frame extracted from a sentence.
    """

    rel: Tuple[str, ...]
    subject: Tuple[str, ...] = ()
    obj: Tuple[str, ...] = ()
    order: int = 0
    name: str = ""

    def mask_object(self) -> "Frame":
        if not self.obj:
            return self
        return Frame(self.rel, self.subject, (MASK,), self.order, self.name)

    def deidentify(self) -> "Frame":
        subj = (MASK,) if self.subject else ()
        obj = (MASK,) if self.obj else ()
        return Frame(self.rel, subj, obj, self.order, self.name)

    @property
    def subject_seen(self) -> bool:
        return bool(self.subject) and self.subject != (MASK,)

    @property
    def object_seen(self) -> bool:
        return bool(self.obj) and self.obj != (MASK,)

    def key(self) -> Tuple:
        return (self.rel, self.subject, self.obj, self.order, self.name)

    def __str__(self) -> str:
        return frame_sexp(self)


def _symbol_tokens(name: object) -> Tuple[str, ...]:
    return tuple(p for p in str(name).lower().replace("-", "_").split("_") if p)


@lru_cache(maxsize=8192)
def content_tokens(sentence: str) -> Tuple[str, ...]:
    """Lowercase content tokens: the surface evidence the reader may use."""
    words = re.findall(r"[a-z0-9]+", sentence.lower())
    return tuple(w for w in words if w not in _STOP)


def _order(toks: Sequence[str], subj: Sequence[str], objt: Sequence[str]) -> int:
    si = min((i for i, t in enumerate(toks) if t in subj), default=-1)
    oi = min((i for i, t in enumerate(toks) if t in objt), default=-1)
    if si < 0 or oi < 0:
        return 0
    return 0 if si <= oi else 1


@lru_cache(maxsize=65536)
def frame_of(
    sentence: str,
    subject: object = None,
    obj: object = None,
    mask: str = "",
    name: str = "",
) -> Frame:
    """Build the IR frame of a sentence anchored at ``(subject, obj)``.

    ``mask`` is ``""`` (keep both names), ``"obj"`` (mask the object -- the
    cue-only view) or ``"all"`` (de-identified: mask both arguments).  Argument
    tokens are removed from the cue set, so ``rel`` is the relational wording.
    """
    toks = content_tokens(sentence)
    subj = _symbol_tokens(subject) if subject is not None else ()
    objt = _symbol_tokens(obj) if obj is not None else ()
    used = set(subj) | set(objt)
    rel = tuple(t for t in toks if t not in used)
    order = _order(toks, subj, objt)
    subj_view = (MASK,) if (mask == "all" and subj) else subj
    obj_view = (MASK,) if (mask in ("obj", "all") and objt) else objt
    return Frame(rel, subj_view, obj_view, order, name)


def render(frame: Frame, atom: Atom) -> str:
    """Render ``atom`` through a surface frame: subject + cue phrase + object."""
    args = [str(a).replace("_", " ") for a in atom.args]
    subj = args[0] if args else ""
    obj = " ".join(args[1:]) if len(args) > 1 else ""
    phrase = " ".join(frame.rel) if frame.rel else "relates to"
    return " ".join(x for x in (subj, phrase, obj) if x)


# Surface frames for the realizing direction (atom -> IR).  A cue phrase is only
# useful if the reader learns to map it back to the predicate; the realizer
# discovers that by round-trip, not from a generation corpus.
FRAMES: Tuple[Frame, ...] = tuple(
    Frame(rel=rel, subject=(MASK,), obj=(MASK,), name=name)
    for name, rel in (
        ("is_a", ("a",)),
        ("instance_of", ("an", "instance", "of")),
        ("subclass_of", ("a", "kind", "of")),
        ("located_in", ("located", "in")),
        ("born_in", ("born", "in")),
        ("occupation", ("worked", "as")),
        ("country", ("part", "of")),
        ("part_of", ("a", "part", "of")),
    )
)


# ============================================================================
# 2. IR features (what each untrusted head may look at)
# ============================================================================
def reader_features(frame: Frame, atom: Atom) -> Tuple[str, ...]:
    """Features of ``(frame, atom)`` for the reading head.

    The decisive features are predicate-conditioned cue features
    (``pred=birthplace&cue=born``): they let the reader learn which wording
    selects which relation, instead of the predicate-blind overlap a surface
    baseline can see.
    """
    pred = atom.pred
    feats: List[str] = [
        "bias",
        f"pred={pred}",
        f"arity={atom.arity}",
        f"pred={pred}&order={frame.order}",
        f"pred={pred}&subj_seen={int(frame.subject_seen)}",
        f"pred={pred}&obj_seen={int(frame.object_seen)}",
    ]
    for w in frame.rel:
        if w == MASK:
            continue
        feats.append(f"cue={w}")
        feats.append(f"pred={pred}&cue={w}")
    return tuple(feats)


def surface_features(frame: Frame, atom: Atom) -> Tuple[str, ...]:
    """Predicate-blind features: the surface baseline cannot see ``pred``."""
    feats: List[str] = ["bias", f"arity={atom.arity}"]
    for w in frame.rel:
        if w != MASK:
            feats.append(f"cue={w}")
    return tuple(feats)


def realizer_features(atom: Atom, frame: Frame) -> Tuple[str, ...]:
    """Features of ``(atom, frame)`` for the realizing head."""
    pred = atom.pred
    feats: List[str] = ["bias", f"pred={pred}", f"frame={frame.name}"]
    for w in frame.rel:
        feats.append(f"cue={w}")
        feats.append(f"pred={pred}&cue={w}")
    return tuple(feats)


# ============================================================================
# 3. the untrusted rankers (order only)
# ============================================================================
class LinearRanker:
    """A perceptron over ``(feature -> weight)``.  It can only order items."""

    def __init__(self, weights: Optional[Dict[str, float]] = None, *, lr: float = 0.1) -> None:
        self.weights: Dict[str, float] = dict(weights or {})
        self.lr = float(lr)
        self.updates = 0

    def score(self, feats: Iterable[str]) -> float:
        return sum(self.weights.get(f, 0.0) for f in feats)

    def bump(self, feats: Iterable[str], delta: float) -> None:
        for f in feats:
            self.weights[f] = self.weights.get(f, 0.0) + self.lr * delta

    def rank(self, items: Sequence, featfn) -> List:
        return sorted(items, key=lambda it: (-self.score(featfn(it)), str(it)))

    def update(self, pos_feats: Iterable[str], neg_feats: Iterable[str]) -> bool:
        """One hard-negative perceptron step (pushes positives above negatives)."""
        pf, nf = tuple(pos_feats), tuple(neg_feats)
        if self.score(pf) <= self.score(nf):
            self.bump(pf, 1.0)
            self.bump(nf, -1.0)
            self.updates += 1
            return True
        return False

    def top_features(self, n: int = 12) -> List[Tuple[str, float]]:
        return sorted(self.weights.items(), key=lambda kv: (-abs(kv[1]), kv[0]))[:n]


class IrReader:
    """A learned ``Frame -> Atom`` proposer.  Ranks candidates; never asserts."""

    def __init__(self, ranker=None, *, lr: float = 0.1, features=reader_features) -> None:
        self.ranker = ranker if ranker is not None else LinearRanker(lr=lr)
        self.features = features

    def score(self, frame: Frame, atom: Atom) -> float:
        return self.ranker.score(self.features(frame, atom))

    def rank(self, frame: Frame, atoms: Iterable[Atom]) -> List[Atom]:
        return self.ranker.rank(list(atoms), lambda a: self.features(frame, a))

    def update(self, frame: Frame, positive: Atom, negative: Atom) -> bool:
        return self.ranker.update(
            self.features(frame, positive), self.features(frame, negative)
        )

    @property
    def trained(self) -> bool:
        return self.ranker.updates > 0

    def top_features(self, n: int = 12) -> List[Tuple[str, float]]:
        return self.ranker.top_features(n)


class IrRealizer:
    """A learned ``Atom -> Frame`` proposer.  Ranks frames; never asserts."""

    def __init__(self, ranker=None, *, lr: float = 0.1, frames: Sequence[Frame] = FRAMES) -> None:
        self.ranker = ranker if ranker is not None else LinearRanker(lr=lr)
        self.frames = tuple(frames)

    def score(self, atom: Atom, frame: Frame) -> float:
        return self.ranker.score(realizer_features(atom, frame))

    def rank(self, atom: Atom) -> List[Frame]:
        return self.ranker.rank(self.frames, lambda f: realizer_features(atom, f))

    def update(self, atom: Atom, positive: Frame, negative: Frame) -> bool:
        return self.ranker.update(
            realizer_features(atom, positive), realizer_features(atom, negative)
        )

    def top_features(self, n: int = 12) -> List[Tuple[str, float]]:
        return self.ranker.top_features(n)


# ============================================================================
# 4. distant supervision: align a fact to its supporting sentence
# ============================================================================
def _long_tokens(name: object, min_token_len: int) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9]+", str(name).lower()) if len(t) >= min_token_len]


def supporting_sentence(
    sentences: Sequence[str],
    subject: object,
    obj: object,
    *,
    min_token_len: int = 3,
) -> Optional[str]:
    """The first sentence that mentions the object (and subject) tokens, else None.

    A fact belongs to the sentence that expresses it, not to every sentence of a
    document.  Without this alignment one sentence becomes a positive for all of
    a document's predicates and the cue -> predicate map is unlearnable.
    """
    obj_toks = _long_tokens(obj, min_token_len)
    subj_toks = _long_tokens(subject, min_token_len)
    if not obj_toks:
        return None
    for sentence in sentences:
        low = sentence.lower()
        if all(t in low for t in obj_toks) and (not subj_toks or all(t in low for t in subj_toks)):
            return sentence
    return None


def aligned_examples(
    sentences: Sequence[str],
    facts: Iterable[object],
    predicates: Sequence[str],
    *,
    mask: str = "obj",
    min_token_len: int = 3,
) -> List[Tuple[Frame, Tuple[Atom, ...], Tuple[Atom, ...]]]:
    """Build IR examples from ``facts`` (objects with ``.pred``/``.subj``/``.obj``).

    Every example is ``(frame, (positive,), candidates)`` where the candidates
    share the masked arguments and differ only by predicate, so a softmax /
    SupCon objective over them is well defined.  ``mask="all"`` de-identifies.
    """
    preds = tuple(dict.fromkeys(predicates))
    out: List[Tuple[Frame, Tuple[Atom, ...], Tuple[Atom, ...]]] = []
    for fact in facts:
        pred = getattr(fact, "pred", None)
        if pred not in preds:
            continue
        subj, obj = getattr(fact, "subj", None), getattr(fact, "obj", None)
        sentence = supporting_sentence(sentences, subj, obj, min_token_len=min_token_len)
        if sentence is None:
            continue
        frame = frame_of(sentence, subj, obj, mask)
        consts = (Const(str(subj)), Const(str(obj)))
        positive = Atom(pred, consts)
        candidates = tuple(Atom(p, consts) for p in preds)
        out.append((frame, (positive,), candidates))
    return out


# ============================================================================
# 5. bidirectional-consistency supervision (no human labels)
# ============================================================================
def _softmax(scores: Sequence[float], temperature: float = 1.0) -> List[float]:
    if not scores:
        return []
    t = max(1e-6, float(temperature))
    hi = max(scores)
    exps = [(s - hi) / t for s in scores]
    m = max(exps)
    vals = [math.exp(e - m) for e in exps]
    total = sum(vals) or 1.0
    return [v / total for v in vals]


class IrSupervisor:
    """Train both IR heads with distant supervision + round-trip consistency."""

    def __init__(self, reader=None, realizer=None, *, lr: float = 0.1) -> None:
        self.reader = reader if reader is not None else IrReader(lr=lr)
        self.realizer = realizer if realizer is not None else IrRealizer(lr=lr)

    def fit_reader(
        self,
        examples: Sequence[Tuple[Frame, Sequence[Atom], Sequence[Atom]]],
        *,
        epochs: int = 8,
        seed: int = 0,
        scramble: bool = False,
        objective: str = "perceptron",
        temperature: float = 0.2,
    ) -> "IrSupervisor":
        """Train the reader on kernel-labelled examples (labels are not human)."""
        rng = Random(seed)
        data = list(examples)
        for _ in range(max(0, int(epochs))):
            rng.shuffle(data)
            for frame, positives, candidates in data:
                cands = list(candidates)
                if not cands:
                    continue
                if scramble:
                    take = max(1, len(positives))
                    positives = [cands[rng.randrange(len(cands))] for _ in range(min(take, len(cands)))]
                pset = set(positives)
                negatives = [a for a in cands if a not in pset]
                if not positives or not negatives:
                    continue
                if objective == "softmax":
                    probs = _softmax([self.reader.score(frame, a) for a in cands], temperature)
                    q = [1.0 / len(positives) if a in pset else 0.0 for a in cands]
                    for atom, p, target in zip(cands, probs, q):
                        delta = target - p
                        if abs(delta) > 1e-9:
                            self.reader.ranker.bump(self.reader.features(frame, atom), delta)
                            self.reader.ranker.updates += 1
                    continue
                for p in positives:
                    best = max(negatives, key=lambda n: self.reader.score(frame, n))
                    self.reader.update(frame, p, best)
        return self

    def _reads_back(self, atom: Atom, frame: Frame, predicates: Sequence[str]) -> bool:
        preds = list(dict.fromkeys([atom.pred, *predicates]))
        cands = [Atom(p, atom.args) for p in preds]
        ranked = self.reader.rank(frame, cands)
        return bool(ranked) and ranked[0].pred == atom.pred

    def fit_realizer(
        self,
        atoms: Sequence[Atom],
        *,
        predicates: Sequence[str],
        epochs: int = 8,
        seed: int = 0,
    ) -> "IrSupervisor":
        """Train the realizer by round-trip consistency with the current reader."""
        rng = Random(seed)
        preds = tuple(dict.fromkeys(predicates))
        for _ in range(max(0, int(epochs))):
            order = list(atoms)
            rng.shuffle(order)
            for atom in order:
                ranked = self.realizer.rank(atom)
                positives, negatives = [], []
                for frame in ranked:
                    (positives if self._reads_back(atom, frame, preds) else negatives).append(frame)
                if not positives or not negatives:
                    continue
                best_neg = max(negatives, key=lambda f: self.realizer.score(atom, f))
                for frame in positives:
                    self.realizer.update(atom, frame, best_neg)
        return self


# ============================================================================
# 6. metrics (honest, per-predicate aware)
# ============================================================================
def reader_recall_at_1(
    reader: IrReader,
    examples: Sequence[Tuple[Frame, Sequence[Atom], Sequence[Atom]]],
) -> float:
    """Fraction of examples whose top-1 candidate is a positive."""
    hit = total = 0
    for frame, positives, candidates in examples:
        if not positives:
            continue
        total += 1
        ranked = reader.rank(frame, candidates)
        if ranked and ranked[0] in set(positives):
            hit += 1
    return hit / total if total else 0.0


def macro_recall_at_1(
    reader: IrReader,
    examples: Sequence[Tuple[Frame, Sequence[Atom], Sequence[Atom]]],
) -> float:
    """Recall@1 averaged per positive predicate (immune to class imbalance)."""
    by: Dict[str, List[int]] = defaultdict(list)
    for frame, positives, candidates in examples:
        for atom in positives:
            ranked = reader.rank(frame, candidates)
            by[atom.pred].append(1 if ranked and ranked[0] in set(positives) else 0)
    if not by:
        return 0.0
    return sum(sum(v) / len(v) for v in by.values()) / len(by)


def majority_baseline(
    examples: Sequence[Tuple[Frame, Sequence[Atom], Sequence[Atom]]],
) -> float:
    """Accuracy of always predicting the most frequent positive predicate."""
    counts: Dict[str, int] = defaultdict(int)
    total = 0
    for _frame, positives, _candidates in examples:
        for atom in positives:
            counts[atom.pred] += 1
            total += 1
    if not total:
        return 0.0
    return max(counts.values()) / total


def roundtrip_rate(
    realizer: IrRealizer,
    reader: IrReader,
    atoms: Sequence[Atom],
    predicates: Sequence[str],
    *,
    k: int = 1,
) -> float:
    """Conversation fidelity: fraction of atoms a top-``k`` frame reads back."""
    atoms = list(atoms)
    if not atoms:
        return 0.0
    preds = list(dict.fromkeys(predicates))
    hits = 0
    for atom in atoms:
        for frame in realizer.rank(atom)[:k]:
            cands = [Atom(p, atom.args) for p in preds]
            ranked = reader.rank(frame, cands)
            if ranked and ranked[0].pred == atom.pred:
                hits += 1
                break
    return hits / len(atoms)


# ============================================================================
# 7. one form: an IR frame serialises exactly like atoms/rules/theories
# ============================================================================
def frame_to_form(frame: Frame) -> tuple:
    """The IR tree of a frame view (delegates to :func:`ir_form`)."""
    return ir_form(frame.rel, frame.subject, frame.obj, frame.order, frame.name)


def frame_from_form(form) -> Frame:
    """The frame *view* of an IR tree (delegates to :func:`ir_from_form`)."""
    return ir_from_form(form)


def frame_sexp(frame: Frame) -> str:
    return dump(frame_to_form(frame))


def frame_from_sexp(text: str) -> Frame:
    forms = parse(text)
    if not forms:
        raise SexpError("empty ir text")
    return frame_from_form(forms[0])


# ============================================================================
# 8. the symbol tree *is* the IR (a frame is just a view)
# ============================================================================
# The IR is a ``Form`` -- the same tree type atoms/rules/theories use.  The
# grammar is head-addressed, so a decoder never depends on position and a new
# head may be appended without breaking anything:
#
#   (ir <name> (rel <tok>...) (subj <tok>...) (obj <tok>...) <order> <head>...)
#
# ``name`` is ``-`` when unnamed, ``<order>`` is 0/1, an argument token of
# ``probe`` means masked / de-identified, and any ``<head>...`` are optional
# vocabulary extensions.  Learning walks the tree directly
# (:func:`reader_tree_features`), so the feature set grows with the vocabulary.
IR_HEAD = Sym("ir")


def ir_form(
    rel: Iterable[object] = (),
    subject: Iterable[object] = (),
    obj: Iterable[object] = (),
    order: int = 0,
    name: object = "",
) -> Form:
    """Build the canonical IR tree -- the single place its shape is defined."""
    return (
        IR_HEAD,
        Sym(str(name) if name else "-"),
        (Sym("rel"), *(Sym(str(t)) for t in rel)),
        (Sym("subj"), *(Sym(str(t)) for t in subject)),
        (Sym("obj"), *(Sym(str(t)) for t in obj)),
        Sym(str(int(order))),
    )


def is_ir(form: object) -> bool:
    """True when ``form`` is a well-formed ``(ir ...)`` tree (extras allowed)."""
    return (
        isinstance(form, tuple)
        and len(form) >= 6
        and form[0] == IR_HEAD
        and all(isinstance(form[i], tuple) and form[i] for i in (2, 3, 4))
        and str(form[2][0]) == "rel"
        and str(form[3][0]) == "subj"
        and str(form[4][0]) == "obj"
    )


def ir_children(tree: Form, head: object) -> Tuple[Form, ...]:
    """Direct children of ``tree`` whose own head symbol is ``head``.

    Head-addressed, not positional: a new head can be inserted into the grammar
    without breaking the decoder.
    """
    if not isinstance(tree, tuple):
        return ()
    want = str(head)
    return tuple(
        node
        for node in tree[1:]
        if isinstance(node, tuple) and node and str(node[0]) == want
    )


def ir_get(tree: Form, head: object, default: Tuple = ()) -> Tuple:
    """Tokens of the first child headed ``head`` (``default`` when absent)."""
    kids = ir_children(tree, head)
    return tuple(kids[0][1:]) if kids else default


def ir_of(
    sentence: str,
    subject: object = None,
    obj: object = None,
    mask: str = "",
    name: str = "",
) -> Form:
    """IR tree of ``sentence`` at ``(subject, obj)`` -- surface straight to tree."""
    return frame_to_form(frame_of(sentence, subject, obj, mask, name))


def ir_from_form(form: Form) -> Frame:
    """The ``Frame`` view of an IR tree (head-addressed, order-independent)."""
    if not is_ir(form):
        raise SexpError(f"not an ir tree: {form!r}")
    name = "" if str(form[1]) == "-" else str(form[1])
    return Frame(
        tuple(str(t) for t in ir_get(form, "rel")),
        tuple(str(t) for t in ir_get(form, "subj")),
        tuple(str(t) for t in ir_get(form, "obj")),
        int(str(form[5])),
        name,
    )


def _walk_tree(tree: Form, path: Tuple[str, ...] = ()):
    """Yield ``(kind, path, value)`` pre-order; ``kind`` is ``node`` or ``leaf``."""
    if isinstance(tree, tuple):
        head = str(tree[0]) if tree else "-"
        here = path + (head,)
        yield ("node", here, head)
        for child in tree[1:]:
            yield from _walk_tree(child, here)
    else:
        yield ("leaf", path, str(tree))


def ir_paths(tree: Form) -> Tuple[Tuple[str, ...], ...]:
    """Pre-order head paths of every node in the tree (its skeleton)."""
    return tuple(path for kind, path, _ in _walk_tree(tree) if kind == "node")


def tree_features(tree: Form) -> Tuple[str, ...]:
    """Structural features read off the tree itself: node presence + leaf values.

    Nothing here names ``rel``/``subj``/``obj``, so any head in the vocabulary --
    including one added later -- contributes features automatically.  This is the
    payoff of making the symbol tree the IR instead of a fixed field tuple.
    """
    feats: List[str] = []
    for kind, path, value in _walk_tree(tree):
        if kind == "node":
            feats.append("node=" + "/".join(path))
        else:
            feats.append("leaf=" + "/".join(path) + "=" + value)
    return tuple(feats)


def reader_tree_features(tree: Form, atom: Atom) -> Tuple[str, ...]:
    """Reader features read straight off the IR tree, predicate-conditioned."""
    pred = atom.pred
    feats: List[str] = ["bias", f"pred={pred}", f"arity={atom.arity}"]
    for f in tree_features(tree):
        feats.append(f)
        feats.append(f"pred={pred}&{f}")
    return tuple(feats)


def aligned_tree_examples(
    sentences: Sequence[str],
    facts: Iterable[object],
    predicates: Sequence[str],
    *,
    mask: str = "obj",
    min_token_len: int = 3,
) -> List[Tuple[Form, Tuple[Atom, ...], Tuple[Atom, ...]]]:
    """Like :func:`aligned_examples` but keeps the IR as a tree, not a view."""
    out: List[Tuple[Form, Tuple[Atom, ...], Tuple[Atom, ...]]] = []
    preds = tuple(dict.fromkeys(predicates))
    for fact in facts:
        pred = getattr(fact, "pred", None)
        if pred not in preds:
            continue
        subj, obj = getattr(fact, "subj", None), getattr(fact, "obj", None)
        sentence = supporting_sentence(sentences, subj, obj, min_token_len=min_token_len)
        if sentence is None:
            continue
        tree = ir_of(sentence, subj, obj, mask)
        consts = (Const(str(subj)), Const(str(obj)))
        positive = Atom(pred, consts)
        candidates = tuple(Atom(p, consts) for p in preds)
        out.append((tree, (positive,), candidates))
    return out
