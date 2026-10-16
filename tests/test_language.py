import pytest

from dlm import (Atom, Rule, episode_ir, evaluate_expr, execute_programs, field,
                 new_state, program_origins, rule_to_ir, validate_model_state)
from dlm.ir import replace_field


def A(pred, *args):
    return Atom(pred, args)


def compose():
    return rule_to_ir(Rule(A("reach", "?x", "?z"),
                           (A("edge", "?x", "?y"), A("edge", "?y", "?z"))))


def state():
    episode = episode_ir("s", {A("edge", "a", "b"), A("edge", "b", "c")},
                         {A("reach", "a", "c")})
    return new_state((episode,))


def test_candidate_grammar_is_persisted_executable_treelisp_code():
    current = state()
    language = field(current, "language")
    assert field(language, "programs")[1:]
    assert compose() in execute_programs(current)
    assert "binary-chain" in program_origins(current, compose())
    from_repl = evaluate_expr(("run-programs",), current)
    assert compose() in from_repl[1:]


def test_removing_program_removes_its_logic_family():
    current = state()
    language = field(current, "language")
    programs = tuple(p for p in field(language, "programs")[1:]
                     if p[1] != "binary-chain")
    stats = tuple(stat for stat in field(language, "program-stats")[1:]
                  if stat[1] != "binary-chain")
    reduced_language = replace_field(language, "programs", ("programs", *programs))
    reduced_language = replace_field(reduced_language, "program-stats",
                                     ("program-stats", *stats))
    reduced = replace_field(current, "language", reduced_language)
    assert compose() not in execute_programs(reduced)


def test_controller_cannot_gain_an_assert_capability():
    current = state()
    language = field(current, "language")
    bad = replace_field(language, "controller",
                        ("controller", ("pipeline", "assert-rule")))
    with pytest.raises(ValueError, match="pipeline"):
        validate_model_state(replace_field(current, "language", bad))


def test_native_contrastive_state_persists_kernel_feedback():
    current = state()
    transition = evaluate_expr(("step", 64), current)
    after = field(transition, "after")[1]
    decision = field(after, "decision")
    assert field(decision, "updates")[1] > 0
    assert field(decision, "weights")[1:]
    assert field(decision, "replay")[1:]
    stats = field(field(after, "language"), "program-stats")[1:]
    assert any(stat[2] > 0 for stat in stats)
    assert any(stat[3] > 0 for stat in stats)
