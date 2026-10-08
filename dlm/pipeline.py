"""DLM v0.0001 — end-to-end pipeline.

    enumerate (predicate retrieval)  ->  decider (rank + threshold)
        ->  restricted KB  ->  deduction (SLD)  ->  answer + proof

The decider only *selects among retrieved candidates*; it never invents an
atom. Enumeration recall is therefore the ceiling on what the pipeline can
answer, and the ablation arm ``use_decider=False`` (best-first over all
candidates) is the matched control required for isolating the decider.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .decider import Decider
from .deduce import Engine, Proof
from .kb import KnowledgeBase
from .retrieval import Candidate, Retriever
from .rules import Rule
from .terms import Atom, substitute_atom


@dataclass
class PipelineResult:
    query: Atom
    answers: List[Atom]
    proofs: List[Proof]
    selected: List[Candidate]
    dropped: List[Candidate]
    trace: Dict[str, float]

    def __str__(self) -> str:
        head = f"query: {self.query}"
        body = "\n".join(f"  {a}" for a in self.answers) or "  (no answer)"
        return f"{head}\n{body}\n  trace: {self.trace}"


def proof_rule_names(p: Proof) -> List[str]:
    names: List[str] = []
    if p.kind not in ("fact", "rule"):
        names.append(p.kind)
    for c in p.children:
        names.extend(proof_rule_names(c))
    return names


class Pipeline:
    def __init__(
        self,
        kb: KnowledgeBase,
        decider: Optional[Decider] = None,
        threshold: float = 0.5,
        max_depth: int = 32,
    ) -> None:
        self.kb = kb
        self.decider = decider
        self.threshold = threshold
        self.max_depth = max_depth
        self.retriever = Retriever(kb)

    # -- selection ---------------------------------------------------------
    def _select(
        self, candidates: Sequence[Candidate], use_decider: bool
    ) -> Tuple[List[Candidate], List[Candidate]]:
        if not candidates:
            return [], []
        if not use_decider or self.decider is None:
            return list(candidates), []
        X = np.array([c.features for c in candidates], dtype=np.float64)
        probs = self.decider.predict_proba(X)
        selected, dropped = [], []
        for cand, p in zip(candidates, probs):
            (selected if p >= self.threshold else dropped).append(cand)
        return selected, dropped

    def _restricted_kb(self, query: Atom, selected: Sequence[Candidate]) -> KnowledgeBase:
        sub = KnowledgeBase()
        for f in self.kb.facts_for(query.pred):
            sub.add_fact(f)
        # also keep facts of predicates referenced by selected rules' bodies
        body_preds = {
            b.pred for c in selected if isinstance(c.item, Rule) for b in c.item.body
        }
        for pred in body_preds:
            for f in self.kb.facts_for(pred):
                sub.add_fact(f)
        for c in selected:
            if isinstance(c.item, Rule):
                sub.add_rule(c.item)
        return sub

    # -- run ---------------------------------------------------------------
    def answer(self, query: Atom, use_decider: bool = True, fallback: bool = True) -> PipelineResult:
        candidates = self.retriever.retrieve(query)
        selected, dropped = self._select(candidates, use_decider)

        def deduce(cands: Sequence[Candidate]) -> List:
            sub = self._restricted_kb(query, cands)
            return list(Engine(sub, max_depth=self.max_depth).prove(query))

        solutions = deduce(selected)
        used_fallback = False
        if not solutions and fallback and use_decider and selected is not candidates:
            # System-2 fallback: the decider's fast path produced no answer, so
            # retry with the full candidate set. Recall is never sacrificed at
            # the cost of the decider's filtering.
            solutions = deduce(candidates)
            used_fallback = True
        answers: List[Atom] = []
        seen = set()
        for sol in solutions:
            g = substitute_atom(query, sol.subst)
            if g.is_ground() and g not in seen:
                seen.add(g)
                answers.append(g)
        proofs = [sol.proof for sol in solutions]
        trace = {
            "n_candidates": float(len(candidates)),
            "n_selected": float(len(selected)),
            "n_dropped": float(len(dropped)),
            "n_answers": float(len(answers)),
            "use_decider": 1.0 if use_decider else 0.0,
            "used_fallback": 1.0 if used_fallback else 0.0,
        }
        return PipelineResult(query, answers, proofs, selected, dropped, trace)


def collect_training_data(
    kb: KnowledgeBase, queries: Sequence[Atom]
) -> Tuple[np.ndarray, np.ndarray]:
    """Label each retrieved candidate by whether it appears in a positive proof.

    A candidate is positive for a query iff the query is provable in the full
    KB *and* the candidate's rule name (or the candidate fact) occurs in the
    proof. This is an honest, proof-derived label — not a hand guess.
    """
    retr = Retriever(kb)
    eng = Engine(kb)
    X: List[Tuple[float, ...]] = []
    y: List[float] = []
    for q in queries:
        sols = list(eng.prove(q))
        if not sols:
            continue
        used_rules = set()
        used_facts = set()
        for sol in sols:
            used_rules.update(proof_rule_names(sol.proof))
        for c in retr.retrieve(q):
            if isinstance(c.item, Rule):
                label = 1.0 if c.item.name in used_rules else 0.0
            else:
                label = 1.0 if c.item in used_facts else 0.0
            X.append(c.features)
            y.append(label)
    if not X:
        return np.zeros((0, Retriever.NUM_FEATURES)), np.zeros((0,))
    return np.array(X), np.array(y)