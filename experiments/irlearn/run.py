#!/usr/bin/env python3
"""experiments/irlearn -- ONE medium for deduction and Lisp: the IR-TREE (v0.0058).

Subject: the DLM package itself.  In v0.0057 the model improved its deduction on
flat ``Atom``/``Rule`` objects while Lisp read a *different* representation.  Here
the medium is unified:

1. PERCEIVE  the model's own source as IR forms (:func:`dlm.irlearn.perceive_ir`)
             -- a canonical form tree, the SAME object ``dlm.ir`` names and
             ``dlm.lisp`` evaluates.
2. INDUCE    the governing composition law AS a form (:func:`induce_law`), by
             searching candidate bodies and scoring them on self-generated
             positives vs sampled negatives.
3. RECURSE   feed the induced law back through the kernel, reifying each certified
             extension as the next predicate's forms (:func:`recurse`); the medium
             GROWS round by round until the reachability fixpoint.
4. LISP      load the identical forms into a Lisp ``Env`` and EXECUTE the same
             level rules through ``eval_form``/``findall``; check Lisp's
             conclusions equal the kernel's, that the tree round-trips exactly,
             and that a macro can WRITE a new form back into the same tree.

Nothing is asserted here; the kernel decides every fact.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

try:                                            # package import
    from dlm.ir import pattern_key, is_form
    from dlm.irlearn import (forms_of_env, lisp_env, perceive_ir, self_learn_ir)
    from dlm.lisp import dump
    from dlm.selflearn import call_graph
except ImportError:                             # direct script
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from dlm.ir import pattern_key, is_form
    from dlm.irlearn import (forms_of_env, lisp_env, perceive_ir, self_learn_ir)
    from dlm.lisp import dump
    from dlm.selflearn import call_graph

VERSION = "0.0.58"


def run(root: str, *, rounds: int = 24) -> dict:
    r = self_learn_ir(root, rounds=rounds)
    tree, law, rec = r.tree, r.law, r.recursion
    graph = call_graph(root)
    one = rec.to_dict()["one_shot_recall"]

    # alpha-renaming invariance: two laws equal up to variable names share a key
    a = ("rule", ("r1", "?a", "?b"), ("calls", "?a", "?c"), ("calls", "?c", "?b"))
    b = ("rule", ("r1", "?x", "?y"), ("calls", "?x", "?z"), ("calls", "?z", "?y"))
    c = ("rule", ("r1", "?a", "?b"), ("calls", "?a", "?b"))
    pattern_invariant = (pattern_key(a) == pattern_key(b)
                         and pattern_key(a) != pattern_key(c))

    lisp_base = forms_of_env(lisp_env(tree), derived=False)
    best_gap = law.true_pos - law.false_pos
    others = [tp - fp for s, tp, fp in law.candidates if s != law.shape]

    verdicts = {
        "ir_tree_is_the_medium": (len(tree) > 0
                                  and all(is_form(f) for f in tree.forms)
                                  and len(tree.where("calls")) == len(graph.edges)),
        "law_induced_on_the_tree": (law.shape == "compose" and law.false_pos == 0
                                    and law.true_pos > 0),
        "induction_discriminates": best_gap > max(others, default=-1),
        "recursion_improves_deduction": (rec.recall - one) > 0.1,
        "recursive_reaches_closure": rec.recall >= 0.999 and rec.fixed,
        "no_false_derivations": all(rd.false == 0 for rd in rec.rounds),
        "medium_grows": len(r.medium) > len(tree),
        "lisp_reads_ir_tree": tuple(lisp_base.forms) == tuple(tree.forms),
        "lisp_evaluates_induced_law": bool(r.lisp["one_shot_match"]),
        "lisp_findall_matches_kernel": bool(r.lisp["final_match"]
                                            and r.lisp["kernel_match"]),
        "lisp_writes_ir": (is_form(r.written) and r.written_in_env
                           and dump(r.written) == "(r1 probe_a probe_b)"),
        "ir_roundtrip_exact": bool(r.roundtrip["read_dump_exact"]
                                   and r.roundtrip["projection_exact"]),
        "pattern_key_invariant": pattern_invariant,
    }

    result = {
        "version": VERSION,
        "graph": graph.to_dict(),
        "tree": tree.to_dict(),
        "law": law.to_dict(),
        "recursion": rec.to_dict(),
        "lisp": dict(r.lisp),
        "roundtrip": dict(r.roundtrip),
        "written": dump(r.written),
        "written_in_env": r.written_in_env,
        "patterns": len(r.patterns),
        "medium": r.medium.to_dict(),
    }
    result["verdicts"] = verdicts
    result["all_ok"] = all(verdicts.values())
    return result


def _fmt(rep: dict) -> str:
    g, t, law, rec = rep["graph"], rep["tree"], rep["law"], rep["recursion"]
    lp, rt = rep["lisp"], rep["roundtrip"]
    lines = []
    lines.append(f"irlearn v{VERSION}  source=dlm  graph: {g['nodes']} nodes, {g['edges']} edges")
    lines.append(f"  medium    : IR-TREE {t['forms']} forms  heads={t['heads']}")
    lines.append(f"  law(form) : {law['shape']}  tp={law['true_pos']} fp={law['false_pos']}")
    lines.append(f"              {law['rule_form']}")
    lines.append(f"              candidates: " +
                 ", ".join(f"{c['shape']}:{c['tp']}/{c['fp']}" for c in law["candidates"]))
    lines.append(f"  deduction : one_shot recall={rec['one_shot_recall']:.3f}  "
                 f"recursive recall={rec['recursive_recall']:.3f}  fixed={rec['fixed']}")
    for rd in rec["rounds"]:
        lines.append(f"              round {rd['level']}: size={rd['size']} new={rd['new']} "
                     f"recall={rd['recall']:.3f} false={rd['false']} medium={rd['forms']}")
    lines.append(f"  lisp      : reads IR-TREE, evaluates law one_shot_match={lp['one_shot_match']}, "
                 f"findall final_match={lp['final_match']} kernel_match={lp['kernel_match']} "
                 f"({lp['lisp_final']} pairs, {lp['lisp_levels']} levels)")
    lines.append(f"  roundtrip : read/dump exact={rt['read_dump_exact']} "
                 f"atom/rule projection exact={rt['projection_exact']}")
    lines.append(f"  macro     : wrote {rep['written']} into the same tree "
                 f"(in_env={rep['written_in_env']})")
    ok = "PASS" if rep["all_ok"] else "FAIL"
    lines.append(f"  verdicts  : " + ", ".join(f"{k}={'T' if v else 'F'}"
                 for k, v in rep["verdicts"].items()) + f"  -> {ok}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="IR-TREE as one medium: deduction improves on it, Lisp reads it")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", "..", "dlm"))
    ap.add_argument("--rounds", type=int, default=24)
    ap.add_argument("--json", default="")
    ap.add_argument("--offline", action="store_true",
                    help="no network is ever used (accepted for harness parity)")
    args, _ = ap.parse_known_args(argv)

    root = os.path.abspath(args.root)
    rep = run(root, rounds=args.rounds)

    # determinism check: a second identical run must agree on the whole medium
    rep2 = run(root, rounds=args.rounds)
    rep["verdicts"]["deterministic"] = (rep2["law"] == rep["law"]
                                        and rep2["recursion"] == rep["recursion"]
                                        and rep2["lisp"] == rep["lisp"]
                                        and rep2["roundtrip"] == rep["roundtrip"])
    rep["all_ok"] = all(rep["verdicts"].values())

    print(_fmt(rep))
    if args.json:
        out = os.path.abspath(args.json)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, indent=2, sort_keys=True)
        print(f"report: {out}")
    return 0 if rep["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())