"""Tests for the v0.0018 fused core: Clause / Theory / learn / solve / forms."""
import pytest

from dlm import (
    Atom, Const, Rule, Var, SexpError,
    Clause, Theory, learn, solve, head_subsumes, subsumes,
    clause_to_form, clause_from_form,
    theory_to_form, theory_from_form, theory_sexp, theory_from_sexp,
)

X, Y, Z = Var("x"), Var("y"), Var("z")


def base_rule():
    return Rule(Atom("ancestor", (X, Y)), (Atom("parent", (X, Y)),), "base")


def rec_rule():
    return Rule(
        Atom("ancestor", (X, Y)),
        (Atom("ancestor", (X, Z)), Atom("parent", (Z, Y))),
        "rec",
    )


def decoy_rule():
    return Rule(Atom("ancestor", (X, Y)), (Atom("parent", (Y, X)),), "decoy")


# -- Clause ---------------------------------------------------------------
def test_clause_holds_rule_and_weight():
    c = Clause(base_rule(), 0.5)
    assert c.weight == 0.5 and c.name == "base"
    assert isinstance(c.rule, Rule)


def test_clause_name_falls_back_to_form():
    c = Clause(Rule(Atom("p", (X,)), (Atom("q", (X,)),)))
    assert c.name.startswith("(rule")


@pytest.mark.parametrize("bad", [("not-a-rule", 0.0), (base_rule(), "x"), (base_rule(), True)])
def test_clause_rejects_bad_input(bad):
    with pytest.raises(TypeError):
        Clause(*bad)


# -- one-way subsumption --------------------------------------------------
def test_head_subsumes_binds_pattern_only():
    assert head_subsumes(base_rule(), Atom("ancestor", (Const("a"), Const("b"))))
    assert not head_subsumes(base_rule(), Atom("parent", (Const("a"), Const("b"))))


def test_subsumes_does_not_collapse_rule_variables():
    # pattern body parent(?y,?x) vs rule body parent(?x,?y): one-way -> no match
    assert not subsumes(decoy_rule(), base_rule())
    assert subsumes(rec_rule(), rec_rule())
    assert not subsumes(rec_rule(), base_rule())


def test_subsumes_matches_distinct_body_atoms():
    assert subsumes(rec_rule(), rec_rule())


# -- Theory ---------------------------------------------------------------
def test_theory_views_and_params():
    t = Theory("a", (Clause(base_rule(), 1.0), Clause(rec_rule(), 2.0)))
    assert t.params == 2
    assert t.names() == ("base", "rec")
    assert t.rules() == (base_rule(), rec_rule())
    assert t.weights() == {"base": 1.0, "rec": 2.0}


def test_theory_score_and_features_on_atom():
    t = Theory("a", (Clause(base_rule(), 1.0), Clause(rec_rule(), 2.0)))
    atom = Atom("ancestor", (Const("a"), Const("b")))
    assert t.matched(atom) == ("base", "rec")
    assert t.features(atom) == ("bias", "base", "rec")
    assert t.score(atom) == 3.0


def test_theory_matches_rules_by_shape():
    t = Theory("a", (Clause(rec_rule(), 1.0), Clause(decoy_rule(), -1.0)))
    assert t.matched(rec_rule()) == ("rec",)
    assert t.matched(decoy_rule()) == ("decoy",)


def test_theory_to_kb_installs_only_structure():
    t = Theory("a", (Clause(base_rule(), 99.0),))
    kb = t.to_kb()
    assert kb.rules() == (base_rule(),) and 99.0 not in {0.0}
    assert len(kb.facts()) == 0


def test_theory_sorted_and_with_weights():
    t = Theory("a", (Clause(base_rule(), 0.0), Clause(rec_rule(), 2.0)))
    assert [c.name for c in t.sorted().clauses] == ["rec", "base"]
    moved = t.with_weights({"base": -1.0})
    assert moved.weights()["base"] == -1.0 and moved.weights()["rec"] == 2.0


# -- learn ----------------------------------------------------------------
def test_learn_separates_by_shape():
    t = Theory("a", (Clause(rec_rule(), 0.0), Clause(decoy_rule(), 0.0)))
    learned, updates = learn(t, [(rec_rule(), decoy_rule())], epochs=5, lr=0.5)
    assert updates >= 1
    assert learned.score(rec_rule()) > learned.score(decoy_rule())
    assert learned.weights()["rec"] > 0 > learned.weights()["decoy"]


def test_learn_no_update_when_already_ordered():
    t = Theory("a", (Clause(rec_rule(), 1.0), Clause(decoy_rule(), -1.0)))
    _, updates = learn(t, [(rec_rule(), decoy_rule())], epochs=5)
    assert updates == 0


# -- solve: the kernel gate ----------------------------------------------
def chain_kb():
    from dlm import KnowledgeBase
    kb = KnowledgeBase()
    kb.add_fact(Atom("parent", (Const("a"), Const("b"))))
    kb.add_fact(Atom("parent", (Const("b"), Const("c"))))
    kb.add_rule(base_rule())
    kb.add_rule(rec_rule())
    return kb


def test_solve_chooses_a_provable_candidate():
    kb = chain_kb()
    cands = [Atom("ancestor", (Const("a"), Const("c"))), Atom("ancestor", (Const("c"), Const("a")))]
    d = solve(kb, Theory("a", ()), cands)
    assert d.chosen is not None and not d.abstained and d.proof is not None


def test_solve_abstains_when_nothing_provable():
    kb = chain_kb()
    d = solve(kb, Theory("a", ()), [Atom("ancestor", (Const("c"), Const("a")))])
    assert d.abstained and d.proof is None


def test_weights_cannot_force_an_unprovable_assert():
    kb = chain_kb()
    # a huge weight on the decoy rank must not make the reversed atom provable
    t = Theory("a", (Clause(decoy_rule(), 1e9),))
    d = solve(kb, t, [Atom("ancestor", (Const("c"), Const("a")))])
    assert d.abstained


# -- one form -------------------------------------------------------------
def test_clause_form_roundtrip():
    for c in (Clause(base_rule(), 0.5), Clause(rec_rule(), -2.0)):
        assert clause_from_form(clause_to_form(c)) == c


def test_clause_form_without_name_or_weight():
    c = Clause(Rule(Atom("p", (X,)), (Atom("q", (X,)),)))
    got = clause_from_form(clause_to_form(c))
    assert got.rule == c.rule and got.weight == 0.0


def test_theory_form_and_sexp_roundtrip():
    t = Theory("ancestor", (Clause(base_rule(), 0.25), Clause(rec_rule(), 0.75)))
    assert theory_from_form(theory_to_form(t)) == t
    assert theory_from_sexp(theory_sexp(t)) == t


def test_theory_form_rejects_bad_input():
    with pytest.raises(SexpError):
        theory_from_form(("nope",))
    with pytest.raises(SexpError):
        clause_from_form(("clause", (Atom("p", (X,)))))
