"""The Lisp seam (DLM v0.0029, NOTE 81).

Question.  v0.0020-v0.0028 built eyes, memory, a proposer, a vector, an executor
and control -- but every bridge between the S-expr *substrate* and the kernel was
a named, one-directional function.  There was no unified evaluation, no code
pattern matcher, no macro, no readable proof, and perception (the IR tree) and
reasoning (the kernel) were disjoint.  This experiment exercises the six seams
added by ``dlm/lisp.py`` -- and checks the honest boundary: the kernel stays
function-free and only ``query`` ever reaches it.

Demonstrations (all deterministic, no human labels)::

    1 eval     a whole program (facts + rules + queries) evaluated by one call
    2 match    a code pattern matched against a code tree (bindings, wildcard)
    3 macro    a macro generates a clause that the kernel then uses to prove
    4 source   a theory is emitted, re-read, and required equal; the selfsup loop
               is re-entered through its own source and stays stable
    5 proof    a certificate is emitted as a term, re-read and re-verified
    6 tree     an IR tree (a non-logic dialect) is reified into facts and queried

Run::

    PYTHONPATH=. python experiments/lisp/run.py
    PYTHONPATH=. python experiments/lisp/run.py --quick --json reports/lisp.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dlm import Atom, Const, KnowledgeBase, Proof, SexpError, Sym, dump, prove  # noqa: E402
from dlm import atom_to_form, form_to_atom  # noqa: E402
from dlm.ssl import ir_form  # noqa: E402
from dlm.selfsup import Task  # noqa: E402
import dlm.lisp as lisp  # noqa: E402
from dlm.lisp import (  # noqa: E402
    Env,
    eval_sexp,
    expand_source,
    form_to_proof,
    match_form,
    proof_to_form,
    query_tree,
    run_source_loop,
    source_roundtrip,
    theory_source,
    tree_atoms,
    verify_form,
)


# ============================================================================
# helpers
# ============================================================================
def _chain_kb(nodes: int) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(nodes - 1):
        kb.add_fact(Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


def _program(nodes: int) -> str:
    """A whole program written as source: facts, two rules, one query."""
    lines = [f"(fact (e n{i} n{i + 1}))" for i in range(nodes - 1)]
    lines += [
        "(rule step (t ?x ?y) (e ?x ?y))",
        "(rule rec (t ?x ?y) (e ?x ?z) (t ?z ?y))",
        f"(query (t n0 n{nodes - 1}))",
    ]
    return "\n".join(lines)


def _exact_pairs(nodes: Sequence[int], distance: int) -> List[Tuple[int, int]]:
    ns = set(nodes)
    return sorted((a, a + distance) for a in nodes if a + distance in ns)


def _atom(pred: str, a: int, b: int) -> Atom:
    return Atom(pred, (Const(f"n{a}"), Const(f"n{b}")))


def _task(kb: KnowledgeBase, pred: str, distance: int, train: Sequence[int], test: Sequence[int]) -> Task:
    pos = sorted((_atom(pred, a, b) for a, b in _exact_pairs(train, distance)), key=str)
    hit = set(_exact_pairs(train, distance))
    pairs = [(a, b) for a in train for b in train if a != b]
    neg = sorted((_atom(pred, a, b) for a, b in pairs if (a, b) not in hit), key=str)
    held_pos = sorted((_atom(pred, a, b) for a, b in _exact_pairs(test, distance)), key=str)
    held_neg = sorted(
        (_atom(pred, a, b) for a, b in pairs if abs(a - b) != distance),
        key=str,
    )
    return Task(pred, kb, tuple(pos), tuple(neg), tuple(held_pos), tuple(held_neg))


def _mini_tasks(nodes: int) -> List[Task]:
    kb = _chain_kb(nodes)
    train = list(range(nodes))
    test = list(range(nodes))
    return [_task(kb, "t0", 2, train, test), _task(kb, "t1", 4, train, test)]


# ============================================================================
# 1. one program, one evaluator
# ============================================================================
def demo_eval(nodes: int) -> dict:
    env = Env()
    results = eval_sexp(_program(nodes), env)
    queries = [r for r in results if isinstance(r, Proof)]
    return {
        "forms": len(results),
        "facts": sum(1 for k, _ in env.events if k == "fact"),
        "rules": sum(1 for k, _ in env.events if k == "rule"),
        "queries": len(queries),
        "proved": sum(1 for q in queries if q is not None),
    }


def demo_abstain() -> bool:
    try:
        eval_sexp("(frobnicate 1 2)", Env())
    except lisp.EvalError:
        return True
    return False


# ============================================================================
# 2. the code algebra matches trees, not just flat atoms
# ============================================================================
def demo_match() -> dict:
    same = match_form((Sym("?op"), Sym("?a"), Sym("?a")), (Sym("+"), Sym("x"), Sym("x")))
    clash = match_form((Sym("?a"), Sym("?a")), (Sym("x"), Sym("y")))
    wild = match_form((Sym("f"), Sym("_"), Sym("?z")), (Sym("f"), Sym("anything"), Sym("q")))
    return {
        "consistent": same is not None and same["?a"] == Sym("x"),
        "clash_rejected": clash is None,
        "wildcard_binds_only_z": wild is not None and set(wild) == {"?z"},
    }


# ============================================================================
# 3. code that writes code
# ============================================================================
def demo_macro(nodes: int) -> dict:
    env = Env()
    kb = _chain_kb(nodes)
    env.kb = kb
    eval_sexp(
        "(defmacro chain-rule (?name ?edge) (clause ?name 1.0 (t ?x ?y) (?edge ?x ?y)))",
        env,
    )
    before = expand_source("(chain-rule c_step e)", env.macros)
    (clause,) = eval_sexp("(chain-rule c_step e)", env)
    # the generated clause is a real rule the kernel can use
    kb2 = env.theory.to_kb(env.kb)
    proof = None if clause is None else prove(kb2, _atom("t", 0, 1))
    return {
        "expansion": before,
        "clause_name": clause.name if clause is not None else None,
        "generated_rule_proves": proof is not None,
    }


# ============================================================================
# 4. source round-trip and the loop through its own source
# ============================================================================
def demo_source(nodes: int) -> dict:
    env = Env()
    (theory,) = eval_sexp(
        "(theory t (clause c_step 1.0 (t ?x ?y) (e ?x ?y)))", env
    )
    text = theory_source(theory)
    stable = source_roundtrip(theory)
    loop = run_source_loop(_mini_tasks(nodes), name="lisp_source", budget=4000, seed=0)
    return {
        "theory_source": text,
        "single_theory_stable": stable,
        "loop_rounds": loop.loop.rounds,
        "loop_params": loop.loop.theory.params,
        "loop_false_assert": loop.loop.false_assert,
        "loop_mean_held_coverage": round(loop.loop.mean_held_coverage, 6),
        "loop_source_stable": loop.stable,
    }


# ============================================================================
# 5. a certificate as a term
# ============================================================================
def demo_proof(nodes: int) -> dict:
    env = Env()
    results = eval_sexp(_program(nodes), env)
    proof = next(r for r in results if isinstance(r, Proof) and r is not None)
    form = proof_to_form(proof)
    reread = form_to_proof(form)
    tampered = (Sym("proof"), (Sym("t"), Sym("n0"), Sym("n99")), form[2])
    return {
        "proof_form": dump(form),
        "reread_equal": reread == proof,
        "verify_original": verify_form(form, env.kb),
        "verify_tampered": verify_form(tampered, env.kb),
    }


# ============================================================================
# 6. perception -> proof: an IR tree becomes provable facts
# ============================================================================
def demo_tree() -> dict:
    tree = ir_form(rel=["born"], subject=["alan"], obj=["london"], order=0, name="alan")
    atoms = tree_atoms(tree)
    # the tree is deliberately not logic: the kernel cannot read it as an atom
    try:
        form_to_atom(tree)
        not_logic = False
    except SexpError:
        not_logic = True
    proof = query_tree(tree, (Sym("leaf"), Sym("tree.2.1"), Sym("born")))
    return {
        "tree": dump(tree),
        "atoms": len(atoms),
        "tree_is_not_logic": not_logic,
        "leaf_query_proved": proof is not None,
        "leaf_proof_atom": str(proof.atom) if proof is not None else None,
    }


# ============================================================================
# report
# ============================================================================
def verdict(out: Dict[str, object]) -> List[Tuple[str, bool]]:
    ev, ma, mc = out["eval"], out["match"], out["macro"]
    so, pr, tr = out["source"], out["proof"], out["tree"]
    return [
        ("one evaluator runs a whole program", ev["queries"] == 1 and ev["proved"] == 1),
        ("an unknown head abstains (no guessing)", out["abstain"] is True),
        ("a code pattern matches a code tree", ma["consistent"] and ma["clash_rejected"] and ma["wildcard_binds_only_z"]),
        ("a macro generates a usable clause", mc["generated_rule_proves"] and mc["clause_name"] == "c_step"),
        ("a theory round-trips through source", so["single_theory_stable"] is True),
        ("the loop re-enters through its own source", so["loop_source_stable"] is True and so["loop_false_assert"] == 0),
        ("a proof is a term that re-verifies", pr["reread_equal"] and pr["verify_original"] and not pr["verify_tampered"]),
        ("an IR tree is reified and proved about", tr["tree_is_not_logic"] and tr["leaf_query_proved"]),
    ]


def run(nodes: int) -> dict:
    out: Dict[str, object] = {
        "config": {"nodes": nodes, "layer": "dlm/lisp.py"},
        "eval": demo_eval(nodes),
        "abstain": demo_abstain(),
        "match": demo_match(),
        "macro": demo_macro(nodes),
        "source": demo_source(nodes),
        "proof": demo_proof(nodes),
        "tree": demo_tree(),
    }
    checks = verdict(out)
    out["verdict"] = [{"check": c, "ok": bool(ok)} for c, ok in checks]
    out["all_pass"] = all(ok for _, ok in checks)
    return out


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="DLM v0.0029 Lisp seam demo")
    ap.add_argument("--nodes", type=int, default=8)
    ap.add_argument("--quick", action="store_true", help="fewer nodes")
    ap.add_argument("--json", type=str, default=None)
    args = ap.parse_args(argv)
    nodes = 6 if args.quick else args.nodes
    out = run(nodes)
    if args.json:
        path = Path(args.json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
