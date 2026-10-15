"""DLM v0.0047 -- generalization + concept invention over a CORPUS (untrusted).

The abstraction in :mod:`dlm.abstract` folds recurring *rule bodies*.  This
layer abstracts the **facts**: given a corpus of programs (each a set of
ground atoms over a shared understanding vocabulary), it mines a conjunction of
subject-features that recurs across programs and **invents a predicate** for it.

The point is the north-star gap: on a *single* small program every conjunction
of understanding predicates is extensionally equal to one of them (measured:
0 genuinely new concepts), so there is nothing to generalise.  A **corpus**
makes the conjunctions non-degenerate, and the invented concept is accepted only
if it is

* irredundant (dropping any feature changes the extension),
* non-degenerate (its extension differs from every single feature),
* and it **transfers** -- the kernel re-derives the concept on a held-out
  program (:func:`transfer`), which separates a real generalisation from a
  re-description.

Nothing here asserts: the concept is a *definitional* rule and the kernel
decides truth when the rule fires.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Tuple

from . import Atom, Const, KnowledgeBase, Rule, Var, closure

__all__ = [
    "Feature", "Concept", "GeneralizationReport", "subject_features",
    "induce_concepts", "concept_instances", "transfer",
]

# A feature is a subject-parameterised literal: (predicate, (arg1, arg2, ...)).
# The subject is always ``arg0`` and is abstracted to the variable X.
Feature = Tuple[str, Tuple[str, ...]]


def _feature(atom: Atom) -> Feature:
    return (atom.pred, tuple(t.name for t in atom.args[1:]))


def subject_features(facts: Iterable[Atom]) -> Dict[str, Dict[Feature, Atom]]:
    """``{subject: {feature: atom}}`` for every atom with at least one argument."""
    out: Dict[str, Dict[Feature, Atom]] = {}
    for a in facts:
        if not a.args:
            continue
        out.setdefault(a.args[0].name, {})[_feature(a)] = a
    return out


@dataclass(frozen=True)
class Concept:
    name: str
    body: Tuple[Feature, ...]
    rule: Rule
    support: int          # subjects in the corpus whose body matches

    def arity(self) -> int:
        return len(self.body)


@dataclass
class GeneralizationReport:
    concepts: Tuple[Concept, ...]
    features: Tuple[Feature, ...]
    subjects: int

    def rules(self) -> Tuple[Rule, ...]:
        return tuple(c.rule for c in self.concepts)

    def to_dict(self) -> dict:
        return {
            "subjects": self.subjects,
            "features": len(self.features),
            "concepts": [
                {"name": c.name, "support": c.support, "body": len(c.body),
                 "literals": [f"{p}(X,{','.join(rest)})" if rest else f"{p}(X)"
                              for p, rest in c.body]}
                for c in self.concepts
            ],
        }


def _extensions(sf: Dict[str, Dict[Feature, Atom]]) -> Dict[Feature, set]:
    ext: Dict[Feature, set] = {}
    for s, feats in sf.items():
        for f in feats:
            ext.setdefault(f, set()).add(s)
    return ext


def induce_concepts(facts: Iterable[Atom], *, min_support: int = 2,
                    max_body: int = 3, max_concepts: int = 8) -> GeneralizationReport:
    """Mine irredundant, non-degenerate feature conjunctions across a corpus.

    Deterministic: candidates are ordered by (support desc, body size, literals).
    """
    facts = list(facts)
    sf = subject_features(facts)
    subjects = set(sf)
    ext = _extensions(sf)
    feats = sorted(ext)
    singles = {frozenset(ext[f]) for f in feats}
    subject_list = sorted(subjects)

    best: Dict[frozenset, Tuple[int, int, Tuple[Feature, ...]]] = {}
    for r in range(2, max_body + 1):
        for combo in combinations(feats, r):
            e = set(subject_list)
            for f in combo:
                e &= ext[f]
                if len(e) < min_support:
                    break
            if len(e) < min_support:
                continue
            key = frozenset(e)
            if key in singles:                      # == an existing single feature
                continue
            redundant = False
            for i in range(r):                       # irredundant?
                e2 = set(subject_list)
                for j, f in enumerate(combo):
                    if j != i:
                        e2 &= ext[f]
                if e2 == e:
                    redundant = True
                    break
            if redundant:
                continue
            cand = (len(e), r, combo)
            if key not in best or cand < best[key]:
                best[key] = cand

    chosen = sorted(best.values(), key=lambda t: (-t[0], t[1], t[2]))[:max_concepts]
    concepts: List[Concept] = []
    for i, (support, _r, combo) in enumerate(chosen):
        body = tuple(Atom(p, (Var("X"),) + tuple(Const(c) for c in rest))
                     for (p, rest) in combo)
        name = f"concept{i}"
        rule = Rule(Atom(name, (Var("X"),)), body, name=name)
        concepts.append(Concept(name, combo, rule, support))
    return GeneralizationReport(tuple(concepts), tuple(feats), len(subjects))


def concept_instances(concept: Concept, facts: Iterable[Atom]) -> List[str]:
    """Subjects in ``facts`` whose feature set contains the concept body."""
    sf = subject_features(facts)
    need = set(concept.body)
    return sorted(s for s, feats in sf.items() if need <= set(feats))


def transfer(concepts: Sequence[Concept], facts: Iterable[Atom]) -> Dict[str, dict]:
    """Kernel-derive each invented concept on a (held-out) program.

    Returns ``{name: {hits, subjects}}`` -- the deductive-transfer evidence.
    """
    facts = set(facts)
    kb = KnowledgeBase(facts)
    for c in concepts:
        kb.add_rule(c.rule)
    closed = closure(kb)
    subjects = sorted({a.args[0].name for a in facts})
    out: Dict[str, dict] = {}
    for c in concepts:
        hits = [s for s in subjects if Atom(c.name, (Const(s),)) in closed]
        out[c.name] = {"hits": len(hits), "subjects": hits}
    return out