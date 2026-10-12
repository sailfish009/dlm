"""Tests for dlm/explain.py -- the v0.0030 explanation / abstraction layer
(description length, proof-carrying hypotheses, abstraction, exact compression,
re-checkable explanations)."""
from __future__ import annotations

import ast
import pathlib

import pytest

from dlm import Atom, Clause, Const, KnowledgeBase, Proof, Rule, Theory, Var
from dlm.explain import (
    Explanation,
    Provenance,
    abstract_theory,
    certify,
    certify_from_tasks,
    clause_literals,
    closure_preserved,
    compress,
    counterfactual,
    description_length,
    explain,
    minimal_explanation,
    profile,
    proof_rule_names,
    redundant,
    summarize,
    verify_explanation,
)

REPO = pathlib.Path(__file__).resolve().parents[1]


# -- fixtures --------------------------------------------------------------
def _E(a, b):
    return Atom("e", (a, b))


def _A(a, b):
    return Atom("anc", (a, b))


def _lemma_theory() -> Theory:
    """A theory with known, kernel-verified redundancy: ``two``/``three`` are
    entailed by ``direct`` + ``rec`` (derivable lemmas)."""
    x, y, z, w = Var("x"), Var("y"), Var("z"), Var("w")
    return Theory(
        "anc",
        (
            Clause(Rule(_A(x, y), (_E(x, y),), "cdirect"), 0.0),
            Clause(Rule(_A(x, y), (_A(x, z), _E(z, y)), "crec"), 0.0),
            Clause(Rule(_A(x, y), (_E(x, z), _E(z, y)), "ctwo"), 0.0),
            Clause(Rule(_A(x, y), (_E(x, z), _E(z, w), _E(w, y)), "cthree"), 0.0),
        ),
    )


def _chain_kb(n: int = 8) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(n):
        kb.add_fact(_E(Const(f"n{i}"), Const(f"n{i + 1}")))
    return kb


# -- 1. description length -------------------------------------------------
def test_clause_literals_counts_head_and_body():
    x, y = Var("x"), Var("y")
    c = Clause(Rule(_A(x, y), (_E(x, y),), "c"), 0.0)
    assert clause_literals(c) == 2


def test_profile_counts_clauses_literals_vocabulary():
    p = profile(_lemma_theory())
    assert p.clauses == 4
    assert p.literals == 12  # (1+1)+(1+2)+(1+2)+(1+3)
    assert p.vocabulary == (("anc", 2), ("e", 2))
    assert p.description_length == 16
    assert p.review_budget == 18
    assert description_length(_lemma_theory()) == 16


def test_profile_to_dict_serialises_vocabulary():
    d = profile(_lemma_theory()).to_dict()
    assert d["vocabulary"] == ["anc/2", "e/2"]
    assert d["description_length"] == 16


# -- 2. proof-carrying hypotheses ------------------------------------------
def test_certify_records_derivations_for_every_clause():
    theory = _lemma_theory()
    prov = certify(theory, {"cdirect": (Atom("anc", (Const("a"), Const("b"))),)})
    assert prov.names() == ("cdirect", "crec", "cthree", "ctwo")
    assert prov.get("cdirect").support == ("(anc a b)",)
    assert prov.get("crec").support == ()
    assert prov.missing(theory) == ()


def test_certify_of_marks_unknown_clauses():
    theory = _lemma_theory()
    prov = certify(theory, {"cdirect": ()})
    prov.table.pop("crec")
    entries = prov.of(theory)
    by_name = {e["name"]: e for e in entries}
    assert by_name["crec"]["known"] is False
    assert by_name["cdirect"].get("known", True) is True  # recorded


def test_certify_from_tasks_witnesses_composed_clauses():
    # grow a small composition theory and confirm each clause gets witnesses
    from dlm.selfsup import StopPolicy, Task, run_loop

    kb = _chain_kb(40)
    tasks = []
    for r, dist in enumerate((2, 4, 8, 16), start=1):
        pred = f"t{r}"
        train = list(range(0, 20))
        pos = sorted(
            (Atom(pred, (Const(f"n{a}"), Const(f"n{a + dist}"))) for a in train if a + dist in train),
            key=str,
        )
        held = tuple(
            Atom(pred, (Const(f"n{a}"), Const(f"n{a + dist}")))
            for a in range(20, 40 - dist)
        )
        tasks.append(Task(pred, kb, tuple(pos), tuple(), held, tuple()))
    result = run_loop(
        tasks,
        mode="learn",
        policy=StopPolicy(max_rounds=len(tasks), stop_on_no_proposal=False),
        name="selfsup",
        budget=20000,
        seed=0,
    )
    prov = certify_from_tasks(result.theory, tasks)
    assert prov.missing(result.theory) == ()
    for c in result.theory.clauses:
        assert len(prov.get(c.name).support) > 0


# -- 3. abstraction --------------------------------------------------------
def test_abstract_theory_groups_by_head_and_covers_all_clauses():
    theory = _lemma_theory()
    abst = abstract_theory(theory)
    assert [m.name for m in abst.modules] == ["anc"]
    assert abst.modules[0].size == 4
    assert sum(m.size for m in abst.modules) == theory.params
    assert abst.modules[0].predicates == ("anc", "e")


def test_abstraction_review_budget_and_dict():
    abst = abstract_theory(_lemma_theory())
    assert abst.review_budget == 1 + 16
    assert abst.profile.clauses == 4
    d = abst.to_dict()
    assert d["modules"][0]["clauses"] == ["cdirect", "crec", "cthree", "ctwo"]


def test_abstract_theory_rejects_unknown_grouping():
    with pytest.raises(ValueError):
        abstract_theory(_lemma_theory(), by="body")


def test_summarize_has_profile_and_modules():
    s = summarize(_lemma_theory())
    assert s["profile"]["clauses"] == 4
    assert s["modules"] == [{"name": "anc", "size": 4, "predicates": ["anc", "e"]}]
    assert s["review_budget"] == 17


# -- 4. exact compression --------------------------------------------------
def test_compress_drops_derivable_lemmas_only():
    theory = _lemma_theory()
    kb = _chain_kb()
    comp = compress(theory, kb)
    assert set(comp.dropped) == {"ctwo", "cthree"}
    assert {c.name for c in comp.theory.clauses} == {"cdirect", "crec"}
    assert comp.saved > 0
    assert comp.after.description_length < comp.before.description_length


def test_compress_is_exact():
    theory = _lemma_theory()
    kb = _chain_kb()
    comp = compress(theory, kb)
    assert closure_preserved(theory, comp.theory, kb)


def test_redundant_matches_compress_dropped():
    theory = _lemma_theory()
    kb = _chain_kb()
    assert set(redundant(theory, kb)) == set(compress(theory, kb).dropped)


def test_removing_an_essential_clause_is_not_preserved():
    theory = _lemma_theory()
    kb = _chain_kb()
    essential = Theory("anc", tuple(c for c in theory.clauses if c.name != "crec"))
    assert not closure_preserved(theory, essential, kb)
    # the recursive witness itself is behaviour-preserving on a chain (the
    # twohop lemma compensates) -- but the fully minimal pair is required.
    assert closure_preserved(theory, compress(theory, kb).theory, kb)


def test_compression_keeps_held_coverage_identical():
    from dlm import closure

    theory = _lemma_theory()
    kb = _chain_kb()
    goals = [_A(Const(f"n{i}"), Const(f"n{i + 3}")) for i in range(5)]
    before = closure(theory.to_kb(kb))
    after = closure(compress(theory, kb).theory.to_kb(kb))
    assert all(g in before for g in goals)
    assert all(g in after for g in goals)
    assert all((g in before) == (g in after) for g in goals)


# -- 5. explanation --------------------------------------------------------
def test_explain_returns_a_recheckable_proof():
    theory = compress(_lemma_theory(), _chain_kb()).theory
    kb = _chain_kb()
    goal = _A(Const("n0"), Const("n5"))
    ex = explain(kb, theory, goal)
    assert isinstance(ex, Explanation)
    assert ex.proved
    assert isinstance(ex.proof, Proof)
    assert set(ex.clauses) == {"cdirect", "crec"}
    assert ex.proof_length > 1
    assert verify_explanation(kb, theory, ex)


def test_explain_attaches_provenance():
    theory = _lemma_theory()
    kb = _chain_kb()
    prov = certify(theory, {"cdirect": (_A(Const("n0"), Const("n1")),)})
    ex = explain(kb, theory, _A(Const("n0"), Const("n1")), provenance=prov)
    assert ex.provenance[0]["name"] == "cdirect"
    assert ex.provenance[0]["support"] == ["(anc n0 n1)"]


def test_explain_unknown_goal_is_not_proved():
    ex = explain(_chain_kb(), _lemma_theory(), _A(Const("n5"), Const("n0")))
    assert not ex.proved
    assert ex.proof is None
    assert ex.proof_length == 0


def test_tampered_explanation_is_rejected():
    theory = _lemma_theory()
    kb = _chain_kb()
    ex = explain(kb, theory, _A(Const("n0"), Const("n3")))
    tampered = Explanation(
        ex.goal, ex.proved, ex.proof, ("cdirect",), ex.proof_length, ex.provenance
    )
    assert not verify_explanation(kb, theory, tampered)


def test_counterfactual_ablation():
    theory = compress(_lemma_theory(), _chain_kb()).theory
    kb = _chain_kb()
    goal = _A(Const("n0"), Const("n5"))
    assert counterfactual(kb, theory, goal, drop=["crec"]) is False
    assert counterfactual(kb, theory, goal, drop=["ctwo"]) is True  # already dropped


def test_minimal_explanation_is_smaller_and_sound():
    theory = _lemma_theory()
    kb = _chain_kb()
    goal = _A(Const("n0"), Const("n2"))
    full = explain(kb, theory, goal)
    minimal = minimal_explanation(kb, theory, goal)
    assert set(minimal.clauses) <= set(full.clauses)
    assert minimal.proof is not None
    assert verify_explanation(kb, theory, minimal)


def test_proof_rule_names_distinct_first_seen():
    theory = _lemma_theory()
    kb = _chain_kb()
    proof = explain(kb, theory, _A(Const("n0"), Const("n4"))).proof
    names = proof_rule_names(proof)
    assert len(names) == len(set(names))
    assert names[0] == "crec"


# -- trust boundary & determinism ------------------------------------------
def test_core_does_not_import_explain():
    tree = ast.parse((REPO / "dlm" / "__init__.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(not a.name.endswith("explain") for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert "explain" not in (node.module or "")


def test_explain_imports_only_the_core_at_module_level():
    tree = ast.parse((REPO / "dlm" / "explain.py").read_text())
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level > 0:
            assert node.module in (None, "deductive"), (node.module, node.level)
        else:
            assert not (node.module or "").startswith("dlm"), node.module


def test_determinism():
    theory = _lemma_theory()
    kb = _chain_kb()
    first = compress(theory, kb).to_dict()
    second = compress(theory, kb).to_dict()
    assert first == second
    goal = _A(Const("n0"), Const("n5"))
    assert explain(kb, theory, goal).to_dict() == explain(kb, theory, goal).to_dict()