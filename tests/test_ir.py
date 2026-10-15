"""DLM v0.0039 tests: the IR is the Form tree (read-only views/features)."""
from dlm import Atom, Const, Rule, Var
from dlm.ir import (is_form, ir_head, ir_children, ir_walk, pattern_key,
                    tree_features, subforms, ir_rule, rule_ir, ir_atom, atom_ir)
from dlm.lisp import parse


def test_form_basics_and_walk():
    f = parse("(rule (ancestor ?x ?y) (parent ?x ?z) (ancestor ?z ?y))")[0]
    assert is_form(f) and ir_head(f) == "rule"
    assert len(ir_children(f)) == 3
    paths = [p for p, _ in ir_walk(f)]
    assert paths[0] == ()                       # root first
    assert (1,) in paths and (2,) in paths and (3,) in paths
    # leaves are not forms
    assert not is_form("?x") and ir_head("?x") is None


def test_pattern_key_is_renaming_invariant():
    a = parse("(rule (h ?x ?y) (e ?x ?z) (e ?z ?y))")[0]
    b = parse("(rule (h ?p ?q) (e ?p ?r) (e ?r ?q))")[0]
    assert pattern_key(a) == pattern_key(b)
    c = parse("(rule (h ?p ?q) (e ?p ?q))")[0]
    assert pattern_key(a) != pattern_key(c)


def test_tree_features_and_subforms():
    f = parse("(rule (h ?x ?y) (e ?x ?y))")[0]
    feats = tree_features(f)
    assert "head:rule" in feats and "head:e" in feats and "sym:?x" in feats
    small = subforms(f, min_size=1)
    assert f in small and ("h", "?x", "?y") in small


def test_projection_roundtrip():
    f = parse("(rule (ancestor ?x ?y) (parent ?x ?y))")[0]
    r = ir_rule(f)
    assert rule_ir(r) == f                       # IR -> Rule -> IR
    a = ir_atom(f[1])
    assert atom_ir(a) == f[1]                    # IR -> Atom -> IR