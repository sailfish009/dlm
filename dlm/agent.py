"""DLM v0.0054 -- the autonomous reader/agent (untrusted): the model as subject.

The model is half deductive kernel and half automation.  Before this version the
automation -- reduce a program, search the web for the knowledge it lacks, acquire
facts, re-close, read the result -- lived in the *experiment*.  That made the
model a library the harness drives.  Here the subject is the model: :class:`Reader`
owns the loop, and an experiment only supplies the GIVEN, domain-specific
vocabulary (a reducer, bridge/gist rules, cue lexicons, a signature builder).

The loop is closed by the kernel, never by a human:

    1. PERCEIVE   source --reduce--> function-free Horn facts          (config)
    2. ACQUIRE    facts' symbols --web search--> ``meaning`` facts     (dlm.acquire)
    3. SEARCH     gist reports a HOLE --web search--> ``dataset_of``   (dlm.acquire)
    4. INDUCE     learn a structural law from the reduction           (dlm.ground)
    5. CLOSE      kernel closure under bridges + gists + law (+ D5/D7a)
    6. READ       leveled N1..N9 narrative, every sentence certified  (dlm.narrative)

A round produces facts the kernel accepts; the next round can use them.  The
agent abstains (no fact) wherever the web cannot supply a premise, so replay is
deterministic and nothing is invented.  ``run_loop`` repeats the acquire/close/read
cycle over a sequence of sources and stops on a policy -- the self-supervised
half of the model's improvement, needing no labels and no human.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from . import Atom, Const, KnowledgeBase, Rule, Var, closure
from .acquire import (EntityVocabulary, SymbolVocabulary,
                      acquire_domain_entities, acquire_symbol_meanings,
                      dataset_candidates, domain_facts, meaning_facts,
                      symbol_candidates)
from .closedworld import candidate_facts
from .equality import absence_rule_equality, same_kind_facts, symbols_in, uses_layer_rules
from .gist import EXTERNAL_PREDICATES, external_holes
from .ground import Ground, learn
from .lisp import form_to_rule
from .narrative import analyze_sentences, reading

__all__ = ["Reader", "atom_of", "astr", "induce_transitive", "collect_loop",
           "StopPolicy"]

_STRUCT_GROUND = Ground(())


def atom_of(fact: tuple) -> Atom:
    return Atom(fact[0], tuple(Const(x) for x in fact[1:]))


def astr(a: Atom) -> str:
    return "(" + " ".join([a.pred] + [t.name for t in a.args]) + ")"


def _chain_rule(pred: str) -> Rule:
    """The GIVEN recursion shape a law is induced over (e.g. transitivity)."""
    x, y, z = Var("?x"), Var("?y"), Var("?z")
    return Rule(Atom(pred, (x, z)),
                (Atom(pred, (x, y)), Atom(pred, (y, z))))


def transitive_closure(base: set, pred: str = "calls") -> set:
    """The full closure of a binary predicate under its GIVEN chain rule."""
    kb = KnowledgeBase({a for a in base if a.pred == pred})
    kb.add_rule(_chain_rule(pred))
    return closure(kb)


def _negatives(positives: set, universe: Sequence[str], pred: str = "calls",
               limit: Optional[int] = None) -> list:
    have = {(a.args[0].name, a.args[1].name) for a in positives}
    out = []
    for x in universe:
        for z in universe:
            if x == z or (x, z) in have:
                continue
            out.append(Atom(pred, (Const(x), Const(z))))
            if limit is not None and len(out) >= limit:
                return out
    return out


def induce_transitive(base: set, structural: Sequence[str], *, pred: str = "calls",
                      max_body: int = 2, extra_vars: int = 2, max_rules: int = 4
                      ) -> tuple:
    """Induce a general law over a binary predicate from one reduction.

    Positives are the predicate's chain closure; negatives are the full
    complement over the observed universe; the induction sees only the
    STRUCTURAL predicates (no acquired meaning leaks into the law search).  A
    general (pronominal) rule is a promise over an open universe, so every new
    referent is a fresh, non-self-referential test.
    """
    rel = {a for a in base if a.pred == pred}
    positives = transitive_closure(base, pred)
    universe = sorted({t.name for a in rel for t in a.args})
    negs = _negatives(positives, universe, pred)
    struct = {a for a in base if a.pred in set(structural)}
    res = learn(_STRUCT_GROUND, struct, positives, negs,
                max_body=max_body, extra_vars=extra_vars, max_rules=max_rules)
    return res, positives


@dataclass
class StopPolicy:
    """When the self-supervised loop stops.  Every field is a named reason."""
    max_rounds: int = 4
    min_new_facts: int = 1

    def decide(self, round_index: int, new_facts: int) -> Optional[str]:
        if round_index + 1 >= self.max_rounds:
            return "max_rounds"
        if new_facts < self.min_new_facts:
            return "saturated"
        return None


@dataclass
class Reader:
    """The autonomous subject: perceive -> acquire -> induce -> close -> read.

    Only the GIVEN, domain-specific pieces are supplied by the caller.  Every
    capability the loop uses (web access, search, acquisition, induction, the
    kernel, the reading) is a model layer.
    """
    perceive: Callable[[str, str], dict]
    symbol_vocab: SymbolVocabulary = field(default_factory=SymbolVocabulary)
    entity_vocab: EntityVocabulary = field(default_factory=EntityVocabulary)
    bridges: Callable[[], List[tuple]] = lambda: []
    gists: Callable[[], List[tuple]] = lambda: []
    structural: Sequence[str] = ()
    signature_builder: Optional[Callable[[Dict[str, str], List[tuple]], object]] = None
    causal: Optional[Callable[[set], set]] = None
    entity_phrases: Mapping[str, str] = field(default_factory=dict)
    law_pred: str = "calls"
    know_world: bool = True
    symbol_version: int = 1
    domain_version: int = 1

    # -- helpers -----------------------------------------------------------
    def _atom(self, fact: tuple) -> Atom:
        return atom_of(tuple(fact))

    def _causal_atoms(self, base: set) -> set:
        return self.causal(base) if self.causal is not None else set()

    def _kb(self, base: set, rules: Sequence[Rule], *, close_world: bool) -> KnowledgeBase:
        kb = KnowledgeBase(base)
        for f in self.bridges():
            kb.add_rule(form_to_rule(f))
        for r in self.gists():
            kb.add_rule(r)
        for r in rules:
            kb.add_rule(r)
        if close_world and self.know_world:
            kb.add_facts(candidate_facts())
            kb.add_facts(same_kind_facts(symbols_in(kb.facts)))
            for r in uses_layer_rules():
                kb.add_rule(r)
            kb.add_rule(absence_rule_equality())
        return kb

    # -- the loop ----------------------------------------------------------
    def run(self, src: str, module: str = "main", cache_dir: str = "cache",
            offline: bool = True, knowledge: dict = None,
            domain: dict = None, close_world: bool = True) -> dict:
        """One perceive -> acquire -> search -> induce -> close -> read pass."""
        # 1. PERCEIVE
        ext = self.perceive(src, module)
        labels, pipelines = ext["labels"], ext["pipelines"]
        facts = [tuple(f) for f in ext["facts"]]

        # 2. ACQUIRE symbol meanings (the model searches for what the code omits)
        if knowledge is None:
            cand_syms = symbol_candidates(ext["facts"], labels)
            knowledge = acquire_symbol_meanings(
                cand_syms, labels, cache_dir, self.symbol_vocab,
                version=self.symbol_version, offline=offline)
        meanings = knowledge["meanings"]

        base = {self._atom(f) for f in ext["facts"]}
        base |= {self._atom(f) for f in meaning_facts(meanings)}
        causal = self._causal_atoms(base)

        # 3. SEARCH for the premise no reading of the code can supply
        cands = dataset_candidates(facts, labels, self.entity_vocab.dataset_hints,
                                   self.entity_vocab.dataset_word)
        holes = external_holes(facts, cands)
        if domain is None:
            domain = acquire_domain_entities(
                {h: cands[h] for h in holes}, cache_dir,
                self.entity_vocab, version=self.domain_version, offline=offline)
        entities = domain.get("entities", {}) if isinstance(domain, dict) else dict(domain)
        dfacts_list = [tuple(f) for f in domain_facts(entities)]
        dfacts = [self._atom(f) for f in dfacts_list]

        sig = (self.signature_builder(meanings, dfacts_list)
               if self.signature_builder is not None else None)

        base_kb = base | set(dfacts)

        # 4. INDUCE the structural law from the reduction itself
        res, positives = induce_transitive(base_kb, self.structural,
                                           pred=self.law_pred)

        # 5. CLOSE under bridges + gists + law (+ D5/D7a)
        kb = self._kb(base_kb, res.experience.rules, close_world=close_world)
        closed = (closure(kb, sig) if sig is not None else closure(kb)) | causal

        # 6. READ
        sentences = reading(closed, labels, pipelines, module=module,
                            meanings=meanings, entity_phrases=self.entity_phrases)
        return {
            "ext": ext, "labels": labels, "pipelines": pipelines, "facts": facts,
            "knowledge": knowledge, "meanings": meanings,
            "base": base, "causal": causal, "cands": cands, "holes": holes,
            "domain": domain, "entities": entities, "dfacts_list": dfacts_list,
            "sig": sig, "base_kb": base_kb, "closed": closed, "kb": kb,
            "res": res, "positives": positives,
            "sentences": sentences,
            "sentence_analysis": analyze_sentences(sentences, closed),
        }

    def run_loop(self, sources: Sequence[str], *, module: str = "main",
                 cache_dir: str = "cache", offline: bool = True,
                 policy: StopPolicy = None) -> dict:
        """Self-supervised improvement over a sequence of sources.

        Each round perceives a source, acquires whatever it lacks, and closes.
        The loop reports, per round, the kernel-approved facts and the acquired
        gaps; it stops on a NAMED policy reason (``saturated`` when a round adds
        no new fact).  No labels, no human -- the kernel is the only judge.
        """
        policy = policy or StopPolicy()
        seen: set = set()
        rounds = []
        stop = None
        for i, src in enumerate(sources):
            p = self.run(src, module=module, cache_dir=cache_dir, offline=offline)
            new = {a for a in p["base"] if astr(a) not in seen}
            seen |= {astr(a) for a in p["base"]}
            rounds.append({"round": i, "source": src,
                           "facts": len(p["base"]), "new_facts": len(new),
                           "acquired": len(p["meanings"]),
                           "holes": list(p["holes"]),
                           "sentences": len(p["sentences"]),
                           "certified": p["sentence_analysis"]["certified"]})
            stop = policy.decide(i, len(new))
            if stop:
                break
        return {"rounds": rounds, "stop": stop,
                "total_facts": len(seen), "rounds_run": len(rounds)}

    # -- self-evaluation + weakness-targeted improvement (v0.0056) ----------
    def rules_for(self, p: dict) -> tuple:
        """The whole theory this reader closed with: bridges + gists + learned law."""
        rules = [form_to_rule(f) for f in self.bridges()]
        rules += list(self.gists())
        rules += list(p["res"].experience.rules)
        return tuple(rules)

    def assess(self, p: dict, *, external=EXTERNAL_PREDICATES, targets=None,
               evidence=None):
        """Snapshot the model's ability: which deduction targets it proves / lacks.

        Read off the kernel closure only (``p['closed']``); nothing is asserted.
        """
        from .ability import ability_profile
        return ability_profile(self.rules_for(p), p["closed"], facts=p["base"],
                               external=external, targets=targets,
                               evidence=evidence)

    def self_improve(self, p: dict, *, acquire, external=EXTERNAL_PREDICATES,
                     **kw):
        """Assess -> ask -> acquire(web) -> re-close -> re-assess, to a stop.

        ``acquire(weak_spot)`` is the only side-effecting seam; it must return
        facts with provenance and abstain (empty) when evidence is missing.  The
        theory (bridges + gists + learned law) is held fixed, so only acquired
        facts change.
        """
        from .curriculum import run_curriculum
        rules = self.rules_for(p)
        causal = set(p.get("causal", ()))

        def close(fs):
            kb = KnowledgeBase({a for a in fs})
            for r in rules:
                kb.add_rule(r)
            return closure(kb) | causal

        return run_curriculum(p["base"], rules, acquire=acquire, external=external,
                              close=close, **kw)


def collect_loop(reader: Reader, sources: Sequence[str], **kw) -> dict:
    return reader.run_loop(sources, **kw)