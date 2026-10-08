"""DLM — Deductive Logic Model.

A non-generative, logic-based alternative in the LLM/VLM family:

    LLM = Large  + Language + Model   (inductive statistics)
    VLM = Vision + Language + Model
    DLM = Deductive + Logic + Model   (induction of rules + deduction)

Pipeline: enumerate candidates (predicate retrieval) -> decider ranks/selects
-> restricted KB -> SLD deduction -> answer + proof. The decider never
generates an atom; enumeration recall is the ceiling.
"""
from __future__ import annotations

from .decider import Decider, torch_decider
from .deduce import Engine, Proof, Solution
from .generalize import induce_rules, lgg_atoms
from .kb import KnowledgeBase
from .pipeline import Pipeline, PipelineResult, collect_training_data
from .retrieval import Candidate, Retriever, feature_vector
from .rules import Rule, fact, rule
from .terms import Atom, Const, Subst, Term, Var, atom, substitute_atom, unify, unify_atom

__version__ = "0.0.1"

__all__ = [
    "Atom", "Const", "Subst", "Term", "Var", "atom", "substitute_atom", "unify",
    "unify_atom", "Rule", "fact", "rule", "KnowledgeBase", "Engine", "Proof",
    "Solution", "induce_rules", "lgg_atoms", "Candidate", "Retriever",
    "feature_vector", "Decider", "torch_decider", "Pipeline", "PipelineResult",
    "collect_training_data", "__version__",
]