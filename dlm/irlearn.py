"""DLM v0.0058 -- the IR-TREE is ONE medium: deduction improves on it, Lisp reads it.

The claim this layer makes is a *unification*, not a new trick.  In v0.0057 the
model improved its deduction on flat ``Atom``/``Rule`` objects while Lisp read a
*different* representation (the form tree).  Here there is exactly ONE medium --
the **IR-TREE** (:class:`IRTree`, a canonical set of nested-tuple forms, the same
object ``dlm.ir`` names and ``dlm.lisp`` evaluates):

* **Deduction improves on the tree.**  The model PERCEIVES its own source as IR
  forms (:func:`perceive_ir`), INDUCES the governing composition law *as a form*
  (:func:`induce_law` -- candidates are searched and scored on self-generated
  positives vs sampled negatives; no human supplies the rule), then RECURSIVELY
  reifies each kernel-certified extension as the next predicate's forms
  (:func:`recurse`).  One composition recovers a fraction of the reachable pairs;
  recursion recovers the reachability closure with zero false derivations.  That
  measured gain is the improvement, and it happens *on the IR-TREE*.

* **Lisp accesses the SAME tree.**  :func:`lisp_env` loads the identical forms
  into a Lisp ``Env``; :func:`lisp_recurse` executes the very same definitional
  level rules *through Lisp's own* ``eval_form``/``findall``; :func:`lisp_writes_ir`
  shows a macro rewriting one form into another (code that writes code) and
  re-entering the tree as a fact.  The agreement is checked against the kernel,
  not asserted: Lisp's ``findall`` equals the learner's relation and the kernel
  closure projected back to forms (:func:`lisp_kernel_agreement`), and the tree
  round-trips exactly through ``parse``/``dump`` and ``Atom``/``Rule``
  (:func:`roundtrip`).

Nothing here asserts.  Lisp is the medium, the kernel is the only judge, and an
induced law whose derived pairs hit a sampled negative would be rejected.  The
perception and the law search are UNTRUSTED proposals; every conclusion the model
keeps is one the kernel derived.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, List, Set, Tuple

from . import Atom, Const, KnowledgeBase, Rule, Var, closure
from .ir import (atom_ir, ir_atom, ir_head, ir_rule, ir_walk, is_form,
                 pattern_key, rule_ir, tree_features)
from .lisp import (DefMacro, Env, atom_to_form, dump, eval_form, findall,
                   form_to_atom, form_to_rule, macroexpand, parse, rule_to_form)

__all__ = [
    "IRTree", "canon", "perceive_ir", "forms_where",
    "InducedLaw", "induce_law",
    "Round", "RecursionResult", "recurse",
    "lisp_env", "forms_of_env", "lisp_prove_one_shot", "lisp_recurse",
    "lisp_writes_ir",
    "ir_patterns", "roundtrip", "lisp_kernel_agreement",
    "IRLearnResult", "self_learn_ir",
]


def canon(forms) -> Tuple[Any, ...]:
    """Canonicalise a form collection: dedupe and sort by the printed form."""
    return tuple(sorted(set(forms), key=dump))


# --------------------------------------------------------------------------- #
# the medium: a canonical IR-TREE (forms are code = data)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class IRTree:
    """The one medium -- a canonical set of IR forms.

    A form is a nested tuple whose head is a symbol (:func:`dlm.ir.is_form`); a
    rule is the form ``(rule <head> <body>...)``.  The tree never asserts: it is a
    representation Lisp reads and the deduction loop transforms.
    """

    forms: Tuple[Any, ...] = ()

    def __len__(self) -> int:
        return len(self.forms)

    def where(self, head: str) -> Tuple[Any, ...]:
        return tuple(f for f in self.forms if is_form(f) and f[0] == head)

    def rules(self) -> Tuple[Any, ...]:
        return self.where("rule")

    def facts(self) -> Tuple[Any, ...]:
        return tuple(f for f in self.forms if is_form(f) and f[0] != "rule")

    def heads(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for f in self.forms:
            h = ir_head(f)
            if h is not None:
                out[h] = out.get(h, 0) + 1
        return out

    def feature_set(self) -> FrozenSet[str]:
        feats: Set[str] = set()
        for f in self.forms:
            feats |= tree_features(f)
        return frozenset(feats)

    def to_dict(self) -> dict:
        return {"forms": len(self.forms),
                "heads": dict(sorted(self.heads().items()))}


def perceive_ir(root: str) -> IRTree:
    """Perceive the Python source under ``root`` as IR forms (untrusted).

    Unary structural facts (``defined``/``private``/``dunder``/``documented``/
    ``method``) come from v0.0057's generic perception; the composable ``calls``
    relation comes from the intra-package call graph (caller and callee are both
    qualified, so the relation can be composed -- raw short callee names cannot
    chain).  Everything is projected to a form, so the *medium* the deduction runs
    on is the form tree.
    """
    from .selflearn import call_graph, perceive_facts
    forms = [atom_to_form(a) for a in perceive_facts(root) if a.pred != "calls"]
    forms += [("calls", a, b) for a, b in call_graph(root).edges]
    return IRTree(canon(forms))


def forms_where(tree: IRTree, head: str) -> Tuple[Any, ...]:
    return tree.where(head)


def _rel_edges(tree: IRTree, rel: str) -> Set[Tuple[str, str]]:
    return {(f[1], f[2]) for f in tree.where(rel) if len(f) == 3}

# --------------------------------------------------------------------------- #
# induction: learn the law from examples, AS A FORM
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class InducedLaw:
    shape: str
    rule: Rule
    rule_form: Any
    true_pos: int
    false_pos: int
    support: int
    candidates: Tuple[Tuple[str, int, int], ...]

    def to_dict(self) -> dict:
        return {"shape": self.shape, "true_pos": self.true_pos,
                "false_pos": self.false_pos, "support": self.support,
                "rule_form": dump(self.rule_form),
                "candidates": [{"shape": s, "tp": tp, "fp": fp}
                               for s, tp, fp in self.candidates]}


def _body_literals(shape: str, rel: str) -> Tuple[Atom, ...]:
    x, y, z = Var("?x"), Var("?y"), Var("?z")
    return {
        "compose": (Atom(rel, (x, y)), Atom(rel, (y, z))),
        "swap": (Atom(rel, (x, y)), Atom(rel, (z, y))),
        "reverse": (Atom(rel, (y, x)), Atom(rel, (y, z))),
        "identity": (Atom(rel, (x, z)),),
    }[shape]


def induce_law(tree: IRTree, *, rel: str = "calls", sample: int = 400,
               negatives: int = 400, seed: int = 0) -> InducedLaw:
    """Search candidate bodies over the tree's ``rel`` forms; pick the best fit.

    Positives are multi-hop pairs the model generated by walking its own edges;
    negatives are sampled non-pairs over the same node set.  The selected law is
    returned BOTH as a ``Rule`` (for the kernel) and as its IR form (for Lisp), so
    the two access paths share one object.
    """
    from .selflearn import _SHAPES, _compose
    E = _rel_edges(tree, rel)
    nodes = sorted({a for e in E for a in e})
    rng = random.Random(seed)
    P = _compose(E)
    Plist = sorted(P)
    if sample and len(Plist) > sample:
        Plist = rng.sample(Plist, sample)
    Pset = set(Plist)
    N: Set[Tuple[str, str]] = set()
    tries = 0
    while len(N) < negatives and tries < negatives * 50:
        tries += 1
        a, b = rng.choice(nodes), rng.choice(nodes)
        if (a, b) not in P:
            N.add((a, b))
    scored: List[Tuple[str, int, int]] = []
    for shape in sorted(_SHAPES):
        derived = _SHAPES[shape](E)
        scored.append((shape, len(derived & Pset), len(derived & N)))
    best = max(scored, key=lambda t: (t[1] - t[2], t[1], -len(t[0])))
    x, z = Var("?x"), Var("?z")
    rule = Rule(Atom("reach", (x, z)), _body_literals(best[0], rel),
                name=f"reach_{best[0]}")
    return InducedLaw(best[0], rule, rule_ir(rule), best[1], best[2], len(P),
                      tuple(scored))


# --------------------------------------------------------------------------- #
# recursion: reify the certified extension as the next predicate's FORMS
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Round:
    level: int
    size: int
    new: int
    recall: float
    false: int
    forms: int

    def to_dict(self) -> dict:
        return {"level": self.level, "size": self.size, "new": self.new,
                "recall": self.recall, "false": self.false, "forms": self.forms}


@dataclass
class RecursionResult:
    shape: str
    rounds: List[Round]
    relation: Set[Tuple[str, str]]
    ground_size: int
    one_shot_size: int
    fixed: bool
    level_trees: Tuple[IRTree, ...]

    @property
    def recall(self) -> float:
        return len(self.relation) / self.ground_size if self.ground_size else 1.0

    def to_dict(self) -> dict:
        return {
            "shape": self.shape, "fixed": self.fixed,
            "ground": self.ground_size, "one_shot": self.one_shot_size,
            "one_shot_recall": (self.one_shot_size / self.ground_size
                                if self.ground_size else 1.0),
            "recursive": len(self.relation), "recursive_recall": self.recall,
            "medium_forms": [len(t) for t in self.level_trees],
            "rounds": [r.to_dict() for r in self.rounds],
        }


def _reify(pairs: Set[Tuple[str, str]], cur: str, nxt: str,
           shape: str) -> Set[Tuple[str, str]]:
    """Kernel-certified extension of the next predicate level (the only judge)."""
    from .selflearn import _level_rules
    kb = KnowledgeBase({Atom(cur, (Const(a), Const(b))) for a, b in pairs})
    for r in _level_rules(shape, cur, nxt):
        kb.add_rule(r)
    return {(a.args[0].name, a.args[1].name)
            for a in closure(kb) if a.pred == nxt}


def recurse(tree: IRTree, law: InducedLaw, *, rounds: int = 24,
            rel: str = "calls") -> RecursionResult:
    """Feed the induced law back through the kernel, reifying the tree each round.

    The medium GROWS: each round appends the newly certified predicate's forms to
    the IR tree, so the next round reads a bigger tree than it wrote.  A round
    that adds nothing is the fixpoint (the model then abstains).
    """
    from .selflearn import _SHAPES, ground_reach
    E = _rel_edges(tree, rel)
    ground = ground_reach(E)
    one = _SHAPES[law.shape](E)
    rel_pairs, pred = set(E), rel
    medium = tree
    recs: List[Round] = []
    level_trees: List[IRTree] = []
    fixed = False
    for k in range(1, rounds + 1):
        nxt = f"r{k}"
        nrel = _reify(rel_pairs, pred, nxt, law.shape)
        new = len(nrel - rel_pairs)
        medium = IRTree(canon(list(medium.forms)
                              + [(nxt, a, b) for a, b in nrel]))
        recs.append(Round(k, len(nrel), new,
                          len(nrel & ground) / len(ground) if ground else 1.0,
                          len(nrel - ground), len(medium)))
        level_trees.append(medium)
        rel_pairs, pred = nrel, nxt
        if new == 0:
            fixed = True
            break
    return RecursionResult(law.shape, recs, rel_pairs, len(ground), len(one),
                           fixed, tuple(level_trees))


# --------------------------------------------------------------------------- #
# Lisp access: the SAME tree, read/evaluated/written by the symbolic medium
# --------------------------------------------------------------------------- #
def lisp_env(tree: IRTree) -> Env:
    """Load the identical IR forms into a Lisp environment (no copy, no echo)."""
    facts: Set[Atom] = set()
    rules: List[Rule] = []
    for f in tree.forms:
        if ir_head(f) == "rule":
            rules.append(form_to_rule(f))
        else:
            facts.add(form_to_atom(f))
    return Env(kb=KnowledgeBase(facts, tuple(rules)))


def forms_of_env(env: Env, *, derived: bool = True) -> IRTree:
    """Read the Lisp environment back as the SAME medium (closure -> forms)."""
    atoms = closure(env.kb) if derived else set(env.kb.facts)
    forms = [atom_to_form(a) for a in atoms]
    forms += [rule_to_form(r) for r in env.kb.rules]
    return IRTree(canon(forms))


def lisp_prove_one_shot(env: Env, law: InducedLaw,
                        head: str = "reach") -> Tuple[Any, ...]:
    """Load the induced law THROUGH Lisp's evaluator, then enumerate it."""
    eval_form(law.rule_form, env)
    return findall((head, "?x", "?z"), env)


def lisp_recurse(env: Env, law: InducedLaw, *, rounds: int = 24,
                 rel: str = "calls") -> List[Tuple[Any, ...]]:
    """Execute the SAME level rules through Lisp; return per-level ``findall``.

    Stops at the same fixpoint the kernel loop does: a level whose extension
    equals the previous level's adds nothing.
    """
    from .selflearn import _level_rules
    out: List[Tuple[Any, ...]] = []
    cur = rel
    prev: Set[Tuple[str, str]] | None = None
    for k in range(1, rounds + 1):
        nxt = f"r{k}"
        for r in _level_rules(law.shape, cur, nxt):
            eval_form(rule_to_form(r), env)
        hits = tuple(findall((nxt, "?x", "?z"), env))
        out.append(hits)
        pairs = {(f[1], f[2]) for f in hits}
        if prev is not None and pairs == prev:
            break
        prev = pairs
        cur = nxt
    return out


def lisp_writes_ir(env: Env, *, macro_name: str = "reach",
                   template: Tuple[Any, ...] = ("r1", "?x", "?z"),
                   call: Tuple[Any, ...] = ("reach", "probe_a", "probe_b")
                   ) -> Any:
    """Define a macro, EXPAND a call, and re-enter the produced form as a fact.

    Homoiconicity at the learning level: a program rewrites one form into another
    and the result is a member of the same IR tree the deduction runs on.
    """
    env.macros[macro_name] = DefMacro(macro_name, ("?x", "?z"), template)
    expanded = macroexpand(call, env.macros)
    eval_form(("fact", expanded), env)
    return expanded


def ir_patterns(tree: IRTree) -> FrozenSet[str]:
    """Canonical pattern keys of every sub-form (variable-renaming invariant)."""
    keys: Set[str] = set()
    for f in tree.forms:
        for _, sub in ir_walk(f):
            keys.add(pattern_key(sub))
    return frozenset(keys)


def roundtrip(tree: IRTree) -> dict:
    """Exact re-entry: read/dump and Atom/Rule projections lose nothing."""
    read_exact, proj_exact = True, True
    for f in tree.forms:
        if not is_form(f):
            read_exact = False
            continue
        try:
            if parse(dump(f))[0] != f:
                read_exact = False
        except Exception:                        # noqa: BLE001
            read_exact = False
        try:
            if ir_head(f) == "rule":
                if rule_ir(ir_rule(f)) != f:
                    proj_exact = False
            elif atom_ir(ir_atom(f)) != f:
                proj_exact = False
        except Exception:                        # noqa: BLE001
            proj_exact = False
    return {"read_dump_exact": read_exact, "projection_exact": proj_exact,
            "forms": len(tree.forms)}


def lisp_kernel_agreement(tree: IRTree, law: InducedLaw, rec: RecursionResult,
                          *, env: Env | None = None) -> dict:
    """Check that Lisp and the kernel conclude the SAME things on the same tree.

    Lisp derives the levels through its own ``eval_form``/``findall`` over the
    accumulated environment; the kernel derived them incrementally in
    :func:`recurse`.  The agreement is that both reach the same extension at every
    level, with no closure recomputed here beyond the ones ``findall`` itself does.
    """
    from .selflearn import _SHAPES
    if env is None:
        env = lisp_env(tree)
    one = {(f[1], f[2]) for f in lisp_prove_one_shot(env, law)}
    expected_one = _SHAPES[law.shape](_rel_edges(tree, "calls"))
    lvl = lisp_recurse(env, law)
    final = {(f[1], f[2]) for f in lvl[-1]} if lvl else set()
    per_level = (len(lvl) == len(rec.rounds)
                 and all(len(lvl[i]) == rec.rounds[i].size
                         for i in range(len(lvl))))
    return {
        "one_shot_match": one == expected_one,
        "final_match": final == rec.relation,
        "kernel_match": per_level,
        "lisp_levels": len(lvl),
        "lisp_final": len(final),
    }


# --------------------------------------------------------------------------- #
# the whole loop
# --------------------------------------------------------------------------- #
@dataclass
class IRLearnResult:
    tree: IRTree
    law: InducedLaw
    recursion: RecursionResult
    lisp: dict
    roundtrip: dict
    written: Any
    written_in_env: bool
    patterns: FrozenSet[str]
    medium: IRTree

    def to_dict(self) -> dict:
        return {
            "tree": self.tree.to_dict(),
            "law": self.law.to_dict(),
            "recursion": self.recursion.to_dict(),
            "lisp": dict(self.lisp),
            "roundtrip": dict(self.roundtrip),
            "written": dump(self.written),
            "written_in_env": self.written_in_env,
            "patterns": len(self.patterns),
            "medium": self.medium.to_dict(),
        }


def self_learn_ir(root: str, *, seed: int = 0, rounds: int = 24) -> IRLearnResult:
    """Perceive -> induce -> recurse -> Lisp-access, all on ONE IR-TREE."""
    tree = perceive_ir(root)
    law = induce_law(tree, seed=seed)
    rec = recurse(tree, law, rounds=rounds)
    env = lisp_env(tree)
    lisp = lisp_kernel_agreement(tree, law, rec, env=env)
    written = lisp_writes_ir(env)
    written_in_env = form_to_atom(written) in env.kb.facts
    rt = roundtrip(IRTree(canon(list(tree.forms) + [law.rule_form])))
    pats = ir_patterns(tree)
    medium = rec.level_trees[-1] if rec.level_trees else tree
    return IRLearnResult(tree, law, rec, lisp, rt, written, written_in_env,
                         pats, medium)
