"""DLM v0.0048 -- core-concept (gist) capture over a program (untrusted, kernel-certified).

The reduction (``experiments/mnist/extract.py``) and the acquired ``meaning`` facts
say *what the code uses and what those symbols mean individually*.  That is a pile
of concrete facts.  It is NOT yet an answer to **"what is this program?"**.

``gist.py`` adds the missing DEDUCTION: a small, GIVEN set of conceptual rules
(``GIST_FORMS``, analogous to the bridge rules in ``semantics.py``) that turn a
structural + semantic pattern into a *core concept* atom -- e.g. a program that
trains a model and instantiates a dataset records a recognizer for whatever that
dataset contains:

    recognizes(?p, ?a) :- trains(?p), builds_model(?p),
                          creates(?p, ?d), dataset_of(?d, ?a).

The only thing the rules cannot supply is the DOMAIN knowledge ``dataset_of(D, A)``
(what a dataset contains); that is what the acquirer SEARCHES for and caches
(``experiments/mnist/domain.py``).  Every gist atom the kernel can derive is a
PROPOSAL whose firing is re-checked by ``dlm.proof.verify``; the layer asserts
nothing itself and abstains when a premise is missing.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from . import Atom, Const, KnowledgeBase, Rule, Var, closure
from .lisp import form_to_rule

Form = tuple

# GIVEN conceptual rules: they connect structure + acquired meaning to a gist.
# They name no library symbol and no dataset; they are the (still hand-written)
# "head" of the reader -- the interpreter seam, like BRIDGE_FORMS.
GIST_FORMS: List[Form] = [
    # A program that trains and constructs a model is a model trainer.
    ("rule", ("trains_model", "?p"), ("trains", "?p"), ("builds_model", "?p")),
    # The strongest concept: the dataset it instantiates tells what it recognizes.
    ("rule", ("recognizes", "?p", "?a"),
     ("trains", "?p"), ("builds_model", "?p"),
     ("creates", "?p", "?d"), ("dataset_of", "?d", "?a")),
    # Supervised = it backpropagates AND updates parameters.
    ("rule", ("is_supervised", "?p"), ("backpropagates", "?p"), ("optimizes", "?p")),
]

# Strongest first.  ``strongest_concept`` returns the first one the kernel derives.
GIST_GOALS: List[str] = ["recognizes", "trains_model", "is_supervised"]

# Predicates that only ACQUIRED domain knowledge can supply (never structural).
EXTERNAL_PREDICATES = frozenset({"dataset_of", "task_of"})


def gist_forms() -> List[Form]:
    """The given conceptual rules as IR forms (no library symbol appears)."""
    return list(GIST_FORMS)


def gist_rules() -> Tuple[Rule, ...]:
    return tuple(form_to_rule(f) for f in GIST_FORMS)


def build_gist_kb(facts) -> KnowledgeBase:
    """A KB of the given facts plus the conceptual rules (ready to close)."""
    kb = KnowledgeBase(set(facts))
    for r in gist_rules():
        kb.add_rule(r)
    return kb


def concept_atoms(closed) -> List[Atom]:
    """Every derived gist atom (predicate in ``GIST_GOALS``), sorted for determinism."""
    goals = set(GIST_GOALS)
    return sorted((a for a in closed if a.pred in goals),
                  key=lambda a: (GIST_GOALS.index(a.pred), tuple(t.name for t in a.args)))


def strongest_concept(closed) -> Optional[Atom]:
    """The highest-priority concept the kernel derives, or ``None`` (abstain)."""
    atoms = concept_atoms(closed)
    return atoms[0] if atoms else None


def concept_str(a: Optional[Atom]) -> str:
    if a is None:
        return "(none)"
    return "(" + " ".join([a.pred] + [t.name for t in a.args]) + ")"


def external_holes(facts, dataset_candidates: Dict[str, str]) -> List[str]:
    """Dataset symbols the program instantiates that still lack ``dataset_of``.

    This is the *gap*: the structural reduction knows ``creates(P, D)`` but not what
    ``D`` contains, so the ``recognizes`` rule cannot fire.  Returning these is the
    untrusted reader saying "I need domain knowledge about D" -- a question, not a fact.
    """
    # facts are tuples ``(pred, *args)``: ``dataset_of(D, A)`` names D in slot 1,
    # ``creates(P, D)`` names D in slot 2.  Reading the wrong slot left the hole
    # permanently open even after the acquirer supplied the fact.
    have = {f[1] for f in facts if f[0] == "dataset_of"}
    made = {f[2] for f in facts if f[0] == "creates"}
    return sorted(d for d in dataset_candidates if d in made and d not in have)