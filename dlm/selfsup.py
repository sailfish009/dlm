"""Module 10: DLM-native self-supervision (regime B: logic SSL).

This is **not** a module of surface pretexts.  The unlabeled resource is the
theory itself (KB / rules / proofs), and the **trusted kernel (C) is the
correctness criterion**.  Following the design (NOTE.md Part IV), the target of
every pretext is the **evaluation result**, never the original text -- so the
learned object is *logic*, not *form*.

Two ledgers are deliberately kept apart:

* **SSL-L** (logic side): ``closure_mask_examples`` (derive-or-not),
  ``minimal_pairs`` (schema-violating permutation / sign flip -- logical edits
  that change entailment), ``rule_removal_examples`` (redundancy delta),
  ``rule_composition_examples`` (a composed rule must not extend the closure),
  ``proof_holes`` (reconstruct a proof's hidden premise).  All labels come from
  the kernel.  **This does not fix NL grounding.**
* **SSL-NL** (language side): :class:`RejectionSelfTrainer` -- needs sentence
  pairs, and accepts a pair only if the kernel already proves it, so it can only
  reinforce what the KB entails and cannot invent vocabulary grounding.

What is learned here is an **untrusted proposer** (seam B'/D): a dependency-free
``FeatureScorer`` over structural features (predicate, arity, argument equality
pattern).  It ranks candidates; it never asserts.  The evaluation protocol is
fixed (NOTE.md Sec.22): soundness first, then held-out derivation completeness,
then proof cost, against no-SSL / surface-SSL / shuffled-KB controls.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from random import Random
from typing import Any, Iterable, List, Optional, Tuple

from .convert import Ingestor
from .engine import Retriever, closure, entails, holds, prove
from .kb import KnowledgeBase
from .kernel import Proof
from .logic import Atom, Const, Literal, Rule, Var
from .unify import Subst, apply_atom, unify

__all__ = [
    "Example",
    "Pair",
    "evaluate",
    "closure_mask_examples",
    "minimal_pairs",
    "rule_removal_examples",
    "compose_rules",
    "rule_composition_examples",
    "proof_holes",
    "features",
    "FeatureScorer",
    "train",
    "ScorerRetriever",
    "proof_cost",
    "recall_at_k",
    "soundness",
    "flip_labels",
    "scramble_constants",
    "ssl_l_examples",
    "RejectionSelfTrainer",
]


# -- the label: a kernel verdict, never the source text --------------------
@dataclass(frozen=True)
class Example:
    """One pretext item.  ``label`` is what the trusted kernel says, not text."""

    kind: str
    target: object
    label: object
    meta: Tuple[Any, ...] = ()


@dataclass(frozen=True)
class Pair:
    """A positive and a kernel-inequivalent negative (a *logical* minimal pair)."""

    positive: Literal
    negative: Literal
    mode: str

    def as_examples(self) -> Tuple[Example, ...]:
        return (
            Example("minimal_pair", self.positive, True, (self.mode, "positive")),
            Example("minimal_pair", self.negative, False, (self.mode, "negative")),
        )


def evaluate(kb: KnowledgeBase, literal: Literal) -> bool:
    """The trusted correctness criterion for a literal (kernel C)."""
    return holds(kb, literal)


# -- pretext 1: closure-mask (derive-or-not) -------------------------------
def closure_mask_examples(
    kb: KnowledgeBase,
    *,
    negatives: Optional[int] = None,
    exclude: Iterable[Atom] = (),
    rng: Optional[Random] = None,
) -> Tuple[Example, ...]:
    """Positive = atoms in the closure; negative = schema-violating permutations.

    ``exclude`` is the **leakage guard**: held-out evaluation atoms must not
    appear in the training pretext (NOTE.md Sec.22.5).
    """
    held = set(exclude)
    positives = [
        Example("closure_mask", Literal(a), True, ("positive",))
        for a in sorted(closure(kb), key=str)
        if a not in held
    ]
    pool: List[Atom] = []
    for a in sorted(closure(kb), key=str):
        if a.arity < 2:
            continue
        for perm in permutations(a.args):
            if perm == a.args:
                continue
            cand = Atom(a.pred, tuple(perm))
            if cand not in held and not entails(kb, cand):
                pool.append(cand)
    pool = sorted(set(pool), key=str)
    if rng is not None:
        rng.shuffle(pool)
    if negatives is not None:
        pool = pool[:negatives]
    negatives_ex = [
        Example("closure_mask", Literal(a), False, ("negative",)) for a in pool
    ]
    return tuple(positives + negatives_ex)


# -- pretext 2: logical minimal pairs --------------------------------------
def minimal_pairs(
    kb: KnowledgeBase,
    *,
    mode: str = "permutation",
    atoms: Optional[Iterable[Atom]] = None,
) -> Tuple[Pair, ...]:
    """Logical (not surface) minimal pairs whose entailment actually changes.

    ``permutation`` reorders arguments without a schema (changes entailment);
    ``sign`` flips the sign of a literal.  A candidate that stays entailed is
    dropped -- it is not a valid negative.
    """
    src = list(atoms) if atoms is not None else sorted(closure(kb), key=str)
    out: List[Pair] = []
    seen = set()
    for a in src:
        if mode == "permutation":
            if a.arity < 2:
                continue
            for perm in permutations(a.args):
                if perm == a.args:
                    continue
                cand = Literal(Atom(a.pred, tuple(perm)))
                if not holds(kb, cand) and cand not in seen:
                    seen.add(cand)
                    out.append(Pair(Literal(a), cand, "permutation"))
        elif mode == "sign":
            neg = Literal(a, negated=True)
            if not kb.is_negated(a) and neg not in seen:
                seen.add(neg)
                out.append(Pair(Literal(a), neg, "sign"))
        else:
            raise ValueError(f"unknown minimal-pair mode {mode!r}")
    return tuple(out)


# -- pretext 3: rule-removal redundancy ------------------------------------
def rule_removal_examples(kb: KnowledgeBase) -> Tuple[Example, ...]:
    """Removing a rule: does the closure stay the same?  (redundancy delta)."""
    before = closure(kb)
    out: List[Example] = []
    for rule in kb.rules():
        after = closure(kb.copy().remove_rule(rule))
        delta = frozenset(before - after)
        out.append(Example("rule_removal", rule, len(delta) == 0, (delta,)))
    return tuple(out)


# -- pretext 4: rule composition (soundness of a proposed rule) ------------
def _rename(rule: Rule, tag: str) -> Rule:
    mapping: Subst = {v: Var(f"{tag}{v.name}") for v in rule.variables()}
    if not mapping:
        return rule
    return Rule(
        apply_atom(rule.head, mapping),
        tuple(apply_atom(b, mapping) for b in rule.body),
    )


def compose_rules(r1: Rule, r2: Rule) -> Tuple[Rule, ...]:
    """Resolve a body atom of ``r2`` against ``r1``'s head (bounded resolution)."""
    r2r = _rename(r2, "c")
    out: List[Rule] = []
    for i, body_atom in enumerate(r2r.body):
        if body_atom.pred != r1.head.pred or body_atom.arity != r1.head.arity:
            continue
        s = unify(body_atom, r1.head, {})
        if s is None:
            continue
        body = tuple(
            apply_atom(x, s) for j, x in enumerate(r2r.body) if j != i
        ) + tuple(apply_atom(x, s) for x in r1.body)
        if not body:
            continue
        try:
            rule = Rule(apply_atom(r2r.head, s), body)
        except (TypeError, ValueError):
            continue
        if rule not in out:
            out.append(rule)
    return tuple(out)


def rule_composition_examples(kb: KnowledgeBase) -> Tuple[Example, ...]:
    """A composed rule is *sound* iff adding it does not extend the closure."""
    before = closure(kb)
    out: List[Example] = []
    for r1 in kb.rules():
        for r2 in kb.rules():
            for composed in compose_rules(r1, r2):
                bigger = kb.copy().add_rule(composed)
                out.append(
                    Example(
                        "rule_composition",
                        composed,
                        closure(bigger) == before,
                        (r1, r2),
                    )
                )
    return tuple(out)


# -- pretext 5: proof-hole (reconstruct a hidden premise) ------------------
def _holes(proof: Proof) -> List[Example]:
    out: List[Example] = []
    for premise in proof.premises:
        out.extend(_holes(premise))
    if proof.rule is not None and proof.premises:
        for i, hidden in enumerate(proof.premises):
            given = tuple(str(p.atom) for j, p in enumerate(proof.premises) if j != i)
            out.append(Example("proof_hole", proof.atom, hidden.atom, (given, i)))
    return out


def proof_holes(
    kb: KnowledgeBase, *, atoms: Optional[Iterable[Atom]] = None
) -> Tuple[Example, ...]:
    """For each proof node, hide one premise; the kernel supplies the answer."""
    src = list(atoms) if atoms is not None else sorted(closure(kb), key=str)
    out: List[Example] = []
    for a in src:
        proof = prove(kb, a)
        if proof is not None:
            out.extend(_holes(proof))
    return tuple(out)


# -- the learned arm: an untrusted structural scorer (seam B'/D) -----------
def features(atom: Atom) -> Tuple[str, ...]:
    """Structural features plus per-position *symbol* identity.

    Predicate, arity and argument-equality pattern are the general part; the
    ``arg{i}=<symbol>`` features are entity-level priors (they do not transfer to
    unseen individuals -- the shuffled-KB control exposes exactly that).  This is
    an untrusted proposer, so overfitting here is contained at the seam.
    """
    feats = [f"pred={atom.pred}", f"arity={atom.arity}"]
    for i, arg in enumerate(atom.args):
        feats.append(f"arg{i}={arg}" if isinstance(arg, Const) else f"arg{i}=var")
    for i in range(atom.arity):
        for j in range(i + 1, atom.arity):
            feats.append(f"eq{i}{j}" if atom.args[i] == atom.args[j] else f"neq{i}{j}")
    return tuple(feats)


class FeatureScorer:
    """A perceptron over :func:`features`.  Untrusted: it only ranks candidates."""

    def __init__(self, weights: Optional[dict] = None, *, lr: float = 0.1) -> None:
        self.weights: dict = dict(weights or {})
        self.lr = float(lr)
        self.updates = 0

    def score(self, atom: Atom, kb: Optional[KnowledgeBase] = None) -> float:
        return sum(self.weights.get(f, 0.0) for f in features(atom))

    def predict(self, atom: Atom, kb: Optional[KnowledgeBase] = None) -> bool:
        return self.score(atom, kb) > 0.0

    def update(self, atom: Atom, label: bool, kb: Optional[KnowledgeBase] = None) -> "FeatureScorer":
        y = 1.0 if label else -1.0
        if y * self.score(atom, kb) <= 0.0:
            for f in features(atom):
                self.weights[f] = self.weights.get(f, 0.0) + self.lr * y
            self.updates += 1
        return self


def train(
    scorer: FeatureScorer,
    examples: Iterable[Example],
    *,
    kb: Optional[KnowledgeBase] = None,
    epochs: int = 1,
) -> FeatureScorer:
    """Train the scorer on atom-labelled examples (labels already from C).

    The scorer ranks *atoms*, so a positive literal contributes its atom and a
    negative literal is skipped (its sign is not an atom property).
    """
    atom_examples: List[Tuple[Atom, bool]] = []
    for e in examples:
        if not isinstance(e.label, bool):
            continue
        if isinstance(e.target, Atom):
            atom_examples.append((e.target, bool(e.label)))
        elif isinstance(e.target, Literal) and not e.target.negated:
            atom_examples.append((e.target.atom, bool(e.label)))
    for _ in range(epochs):
        for atom, label in atom_examples:
            scorer.update(atom, label, kb)
    return scorer


class ScorerRetriever:
    """Seam B': rank candidate atoms by a learned scorer (untrusted ordering)."""

    def __init__(self, scorer: FeatureScorer) -> None:
        self.scorer = scorer

    def retrieve(
        self,
        kb: KnowledgeBase,
        candidates: Iterable[Atom],
        *,
        limit: Optional[int] = None,
    ) -> Tuple[Atom, ...]:
        ranked = sorted(candidates, key=lambda a: (-self.scorer.score(a, kb), str(a)))
        return tuple(ranked[:limit]) if limit is not None else tuple(ranked)


# -- evaluation protocol (NOTE.md Sec.22) -----------------------------------
def proof_cost(proof: Proof) -> int:
    """Number of nodes in a certificate (smaller = cheaper derivation)."""
    return 1 + sum(proof_cost(p) for p in proof.premises)


def recall_at_k(
    retriever: Retriever,
    kb: KnowledgeBase,
    candidates: Iterable[Atom],
    truths: Iterable[Atom],
    k: int,
) -> float:
    """Held-out derivation completeness: fraction of truths in the top ``k``."""
    truths = list(truths)
    if not truths:
        return 1.0
    got = set(retriever.retrieve(kb, candidates, limit=k))
    return len(got & set(truths)) / len(truths)


def soundness(examples: Iterable[Example], kb: KnowledgeBase) -> bool:
    """Every atom/literal label must equal the kernel verdict (soundness first)."""
    for e in examples:
        if isinstance(e.target, Atom) and isinstance(e.label, bool):
            if entails(kb, e.target) != e.label:
                return False
        elif isinstance(e.target, Literal) and isinstance(e.label, bool):
            if evaluate(kb, e.target) != e.label:
                return False
    return True


# -- controls (NOTE.md Sec.21) ---------------------------------------------
def flip_labels(examples: Iterable[Example]) -> Tuple[Example, ...]:
    """Surface-SSL control: ignore the kernel and invert every boolean label."""
    return tuple(
        Example(e.kind, e.target, not e.label, e.meta)
        if isinstance(e.label, bool)
        else e
        for e in examples
    )


def scramble_constants(kb: KnowledgeBase, *, rng: Optional[Random] = None) -> KnowledgeBase:
    """Shuffled-KB control: same shape, different individuals (structure broken)."""
    rng = rng or Random(0)
    names = sorted({a.name for f in kb.facts() for a in f.args if isinstance(a, Const)})
    shuffled = names[:]
    rng.shuffle(shuffled)
    ren = dict(zip(names, shuffled))

    def relabel(atom: Atom) -> Atom:
        return Atom(
            atom.pred,
            tuple(Const(ren[a.name]) if isinstance(a, Const) else a for a in atom.args),
        )

    other = KnowledgeBase()
    for f in kb.facts():
        other.add_fact(relabel(f))
    for r in kb.rules():
        other.add_rule(r)
    for n in kb.negations():
        other.add_negation(relabel(n))
    return other


# -- the two ledgers -------------------------------------------------------
def ssl_l_examples(
    kb: KnowledgeBase,
    *,
    held_out: Iterable[Atom] = (),
    negatives: Optional[int] = None,
    rng: Optional[Random] = None,
) -> Tuple[Example, ...]:
    """The **logic-side** ledger: only atoms/rules, labelled by the kernel.

    No sentence ever enters here, so it cannot fix NL grounding (NOTE.md Sec.20).
    """
    out: List[Example] = list(
        closure_mask_examples(kb, negatives=negatives, exclude=held_out, rng=rng)
    )
    for pair in minimal_pairs(kb):
        out.extend(pair.as_examples())
    out.extend(rule_removal_examples(kb))
    return tuple(out)


class RejectionSelfTrainer:
    """The **language-side** ledger (separate!).

    Needs ``(sentence, Literal)`` pairs and keeps only those the trusted kernel
    already proves; everything else is rejected.  It therefore only reinforces
    what the KB entails and **cannot invent new vocabulary grounding** -- coverage
    is bounded by the KB and by abstain.  Pairs are held externally as a corpus;
    nothing textual is retained inside the model.
    """

    def __init__(self, ingestor: Ingestor, kb: KnowledgeBase) -> None:
        self.ingestor = ingestor
        self.kb = kb
        self.accepted: List[Tuple[str, Literal]] = []
        self.rejected: List[str] = []

    def offer(self, sentence: str) -> Optional[Literal]:
        literal = self.ingestor.literal(sentence)
        if literal is None or not holds(self.kb, literal):
            self.rejected.append(sentence)
            return None
        self.accepted.append((sentence, literal))
        return literal