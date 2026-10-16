import pytest

from dlm import (Atom, Rule, closure, commit_transition, episode_ir, evaluate,
                 field, learn_round, new_state, node_id, prove, rule_to_ir, safe,
                 synthesize, verify_proof)


def A(pred, *args):
    return Atom(pred, args)


def compose():
    return Rule(A("reach", "?x", "?z"),
                (A("edge", "?x", "?y"), A("edge", "?y", "?z")))


def chain(source, a, b, c, role="train"):
    nodes = (a, b, c)
    facts = {A("edge", a, b), A("edge", b, c)}
    positive = {A("reach", a, c)}
    negative = {A("reach", x, z) for x in nodes for z in nodes if (x, z) != (a, c)}
    return episode_ir(source, facts, positive, negative, role=role)


def verdict_value(verdict, name):
    return field(verdict, name)[1]


def test_horn_kernel_and_safe_typed_rule():
    rule = compose()
    assert safe(rule)
    assert A("reach", "a", "c") in closure(
        {A("edge", "a", "b"), A("edge", "b", "c")}, (rule,))
    assert not safe(Rule(A("q", "?x"), (A("p", "?y"),)))


def test_semi_naive_frontier_reaches_recursive_fixpoint():
    base = Rule(A("reach", "?x", "?y"), (A("edge", "?x", "?y"),))
    recursive = Rule(A("reach", "?x", "?z"),
                     (A("reach", "?x", "?y"), A("edge", "?y", "?z")))
    facts = {A("edge", "a", "b"), A("edge", "b", "c"), A("edge", "c", "d")}
    closed = closure(facts, (base, recursive))
    assert A("reach", "a", "d") in closed
    assert len({atom for atom in closed if atom.pred == "reach"}) == 6


def test_proof_is_ir_and_rejects_an_absent_rule():
    facts = {A("edge", "a", "b"), A("edge", "b", "c")}
    proof = prove(facts, (compose(),), A("reach", "a", "c"))
    assert proof is not None and verify_proof(proof, facts, (compose(),))
    assert not verify_proof(proof, facts, ())


def test_synthesis_is_ir_and_contains_composition():
    state = new_state((chain("s", "a", "b", "c"),))
    actions = synthesize(state)
    assert rule_to_ir(compose()) in actions
    assert all(action[0] == "rule" for action in actions)


def test_unknown_is_not_negative_but_counterevidence_is_hard():
    rule = rule_to_ir(Rule(A("q", "?x"), (A("p", "?x"),)))
    unknown = new_state((episode_ir("u", {A("p", "a"), A("p", "b")},
                                          {A("q", "a")}, unknown={A("q", "b")}),))
    verdict = evaluate(unknown, rule)
    assert verdict_value(verdict, "useful") is True
    contradicted = new_state((episode_ir("c", {A("p", "a"), A("p", "b")},
                                               {A("q", "a")}, {A("q", "b")}),))
    verdict = evaluate(contradicted, rule)
    assert verdict_value(verdict, "useful") is False
    assert verdict_value(verdict, "false-asserts") == 1


def test_one_round_moves_axiom_not_evidence():
    episodes = (chain("a", "a", "b", "c"), chain("b", "d", "e", "f"),
                chain("held", "g", "h", "i", "validation"))
    state = new_state(episodes)
    evidence = field(state, "evidence")
    transition = learn_round(state, budget=96, min_sources=3)
    after = commit_transition(state, transition)
    assert field(after, "evidence") == evidence
    assert rule_to_ir(compose()) in field(field(after, "theory"), "experience")[1:]
    assert not field(field(after, "theory"), "ground")[1:]
    assert len(field(transition, "events")[1:]) == 1


def test_ground_conflict_abstains_without_self_revision():
    bad = rule_to_ir(Rule(A("reach", "?x", "?z"), (A("edge", "?x", "?z"),)))
    episode = episode_ir("x", {A("edge", "a", "b")},
                         contradicted={A("reach", "a", "b")})
    state = new_state((episode,), ground=(bad,))
    transition = learn_round(state)
    assert field(field(transition, "events")[1], "kind")[1] == "abstain"
    assert field(transition, "after")[1] == state


def test_counterexample_retracts_experience_through_transition():
    bad = rule_to_ir(Rule(A("reach", "?x", "?z"), (A("edge", "?x", "?z"),)))
    episode = episode_ir("x", {A("edge", "a", "b")},
                         contradicted={A("reach", "a", "b")}, role="validation")
    state = new_state((episode,), experience=(bad,))
    after = commit_transition(state, learn_round(state, budget=1))
    assert not field(field(after, "theory"), "experience")[1:]
    event = field(after, "events")[-1]
    assert bad in field(event, "retracted")[1:]
    records = field(after, "memory")[1:]
    assert any(field(record, "rule")[1] == bad
               and field(record, "status")[1] == "retracted"
               for record in records)


def test_stale_transition_cannot_commit():
    state = new_state((chain("s", "a", "b", "c"),))
    transition = learn_round(state, budget=1)
    changed = commit_transition(state, transition)
    with pytest.raises(ValueError):
        commit_transition(changed, transition)
    assert field(transition, "before")[1] == node_id(state)
