"""Matched-arm DIALOGUE evaluation (v0.0003, W4).

Question: with the loop assembled (ground -> prove/assert -> reply), how far does
a *conversation* actually get, and is the extra lexical T2 fallback worth it?

The ONLY variable between arms is the grounder:

  t1_only   GrammarGrounder over TRAIN phrasing only (abstains on unseen)
  chain     t1_only + CharNgramGrounder lexical T2 (the adopted default fallback)

Everything else is identical: same KB, same scripted turns, the same forced
intent (`ask`/`tell`), the same deterministic verbalizer. Intent is forced so
that this measures the loop and the grounder, not a question/statement heuristic.

Gold labels are explicit (atom + verdict), not re-derived from the KB, so a
wrong grounding becomes a visible *confident-wrong* verdict rather than being
hidden by a self-consistent oracle.

Honest reporting: coverage, exact-atom accuracy, verdict accuracy, confident
wrong count, abstention rate, KB growth. Ties are ties. No "advantage" language.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dlm import (
    ChainGrounder,
    DialogueSession,
    GrammarGrounder,
    KnowledgeBase,
    Pattern,
    fact,
    rule,
)
from dlm.dialogue import ABSTAIN
from dlm.grounder_learn import CharNgramGrounder, synthesize_pairs
from dlm.interpreter import parse_atom
from dlm.terms import Var

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

ENTITIES = ("alice", "bob", "carol", "dave")

TRAIN = [
    Pattern("is {x} a parent of {y}", "parent({x},{y})"),
    Pattern("{x} is a parent of {y}", "parent({x},{y})"),
    Pattern("is {x} a grandparent of {y}", "grandparent({x},{y})"),
    Pattern("is {x} an ancestor of {y}", "ancestor({x},{y})"),
    Pattern("is {x} a sibling of {y}", "sibling({x},{y})"),
]

# (utterance, intent, gold_atom | None, gold_verdict | None, phrasing)
SCRIPT: List[Tuple[str, str, Optional[str], Optional[bool], str]] = [
    # -- train phrasing: T1 should handle these exactly --------------------
    ("is alice an ancestor of dave", "ask", "ancestor(alice,dave)", True, "train"),
    ("is dave an ancestor of alice", "ask", "ancestor(dave,alice)", False, "train"),
    ("is alice a grandparent of carol", "ask", "grandparent(alice,carol)", True, "train"),
    ("dave is a parent of erin", "tell", "parent(dave,erin)", None, "train"),
    ("is carol an ancestor of erin", "ask", "ancestor(carol,erin)", True, "train"),
    # -- unseen phrasing: T1 abstains, only the lexical T2 can respond ------
    ("does alice come before dave in the family tree", "ask", "ancestor(alice,dave)", True, "unseen"),
    ("is dave above alice in the family tree", "ask", "ancestor(dave,alice)", False, "unseen"),
    ("is alice a grandparent to carol", "ask", "grandparent(alice,carol)", True, "unseen"),
    ("is alice a brother or sister of bob", "ask", "sibling(alice,bob)", False, "unseen"),
    # -- out of domain: must abstain ---------------------------------------
    ("is berlin the capital of germany", "ask", None, None, "out_of_domain"),
    # -- negated assertion: closed-world consistency ------------------------
    ("alice is not a parent of dave", "tell", "parent(alice,dave)", None, "train"),
]

canon = lambda a: str(parse_atom(a))  # noqa: E731


def build_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]:
        kb.add_fact(fact("parent", a, b))
    x, y, z = Var("x"), Var("y"), Var("z")
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, y), name="anc_base"))
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, z),
                     fact("ancestor", z, y), name="anc_step"))
    kb.add_rule(rule(fact("grandparent", x, y), fact("parent", x, z),
                     fact("parent", z, y), name="gp"))
    return kb


def make_grounder(arm: str):
    t1 = GrammarGrounder(TRAIN)
    if arm == "t1_only":
        return t1
    if arm == "chain":
        lexical = CharNgramGrounder(synthesize_pairs(TRAIN, ENTITIES, seed=0))
        return ChainGrounder([t1, lexical])
    raise ValueError(arm)


def run_arm(arm: str) -> Dict[str, object]:
    session = DialogueSession(build_kb(), make_grounder(arm))
    rows: List[Dict[str, object]] = []
    added_total = 0
    for utterance, intent, gold_atom, gold_verdict, phrasing in SCRIPT:
        reply = session.ask(utterance) if intent == "ask" else session.tell(utterance)
        g = reply.grounding
        grounded = bool(g is not None and g.ok)
        exact: Optional[bool] = None
        if gold_atom is not None:
            exact = bool(grounded and canon(str(g.atom)) == canon(gold_atom))
        verdict_ok: Optional[bool] = None
        if gold_verdict is not None:
            verdict_ok = bool(reply.derivable == gold_verdict)
        confident_wrong = bool(
            grounded and gold_verdict is not None
            and reply.derivable is not None and reply.derivable != gold_verdict
        )
        added_total += int(reply.added)
        rows.append({
            "utterance": utterance,
            "intent": intent,
            "phrasing": phrasing,
            "kind": reply.kind,
            "grounded": grounded,
            "ground_source": getattr(g, "source", "") if grounded else "",
            "atom": str(g.atom) if grounded else "",
            "gold_atom": gold_atom,
            "exact": exact,
            "derivable": reply.derivable,
            "gold_verdict": gold_verdict,
            "verdict_ok": verdict_ok,
            "confident_wrong": confident_wrong,
            "added": bool(reply.added),
            "provenance": reply.provenance,
        })

    n = len(rows)
    graded_exact = [r for r in rows if r["gold_atom"] is not None]
    graded_verdict = [r for r in rows if r["gold_verdict"] is not None]
    grounded_rows = [r for r in rows if r["grounded"]]
    answered = [r for r in grounded_rows if r["derivable"] is not None]
    metrics = {
        "n_turns": n,
        "coverage": round(len(grounded_rows) / n, 4),
        "abstention_rate": round(sum(r["kind"] == ABSTAIN for r in rows) / n, 4),
        "exact_atom_accuracy": round(
            sum(r["exact"] for r in graded_exact) / max(1, len(graded_exact)), 4),
        "verdict_accuracy": round(
            sum(r["verdict_ok"] for r in graded_verdict) / max(1, len(graded_verdict)), 4),
        "verdict_accuracy_when_grounded": round(
            sum(r["verdict_ok"] for r in graded_verdict if r["grounded"])
            / max(1, sum(1 for r in graded_verdict if r["grounded"])), 4),
        "confident_wrong": int(sum(r["confident_wrong"] for r in rows)),
        "answered_turns": len(answered),
        "kb_facts_added": added_total,
        "by_phrasing": {},
    }
    for ph in ("train", "unseen", "out_of_domain"):
        grp = [r for r in rows if r["phrasing"] == ph]
        if not grp:
            continue
        gem = [r for r in grp if r["gold_atom"] is not None]
        metrics["by_phrasing"][ph] = {
            "n": len(grp),
            "coverage": round(sum(r["grounded"] for r in grp) / len(grp), 4),
            "exact_atom_accuracy": round(
                sum(r["exact"] for r in gem) / max(1, len(gem)), 4),
            "confident_wrong": int(sum(r["confident_wrong"] for r in grp)),
        }
    return {"arm": arm, "metrics": metrics, "turns": rows}


def judge(arms: Dict[str, Dict[str, object]]) -> str:
    """Pre-registered: survival requires the fallback to not ADD confident-wrong."""
    t1 = arms["t1_only"]["metrics"]
    ch = arms["chain"]["metrics"]
    if ch["confident_wrong"] > t1["confident_wrong"]:
        return "control_favored"          # the fallback answers more, but wrongly
    if ch["coverage"] > t1["coverage"] and ch["verdict_accuracy"] >= t1["verdict_accuracy"]:
        return "fallback_helps"
    return "tie"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ARTIFACTS / "dialogue_eval.json"))
    args = ap.parse_args()

    arms = {a: run_arm(a) for a in ("t1_only", "chain")}
    verdict = judge(arms)

    print(f"{'arm':<9} {'cov':>6} {'exact':>7} {'verdict':>8} {'conf_wrong':>11} {'abstain':>8}")
    for a, res in arms.items():
        m = res["metrics"]
        print(f"{a:<9} {m['coverage']:>6.3f} {m['exact_atom_accuracy']:>7.3f} "
              f"{m['verdict_accuracy']:>8.3f} {m['confident_wrong']:>11d} "
              f"{m['abstention_rate']:>8.3f}")
    print(f"\njudgment: {verdict}")
    print("note: 'exact' is over turns with a gold atom; 'confident_wrong' counts")
    print("      grounded turns whose verdict is wrong (a sound proof of the wrong atom).")

    payload = {
        "version": "0.0.3",
        "script": "scripts/dialogue_eval (scripted, intent forced)",
        "n_turns": len(SCRIPT),
        "single_variable": "grounder",
        "judgment": verdict,
        "arms": {a: res["metrics"] for a, res in arms.items()},
        "turn_rows": {a: res["turns"] for a, res in arms.items()},
        "notes": [
            "intent is forced with ask/tell, so this measures the loop + grounder",
            "gold atoms/verdicts are explicit, so wrong grounding is visible",
            "verdict_accuracy counts an abstention as an incorrect verdict (end-to-end use)",
            "verdict_accuracy_when_grounded excludes abstentions",
            "closed-world negation is an assumption, not a theorem",
            "SMALL-N CAVEAT: n_turns is 11 (4 unseen). 'fallback_helps' means only:",
            "  on this scripted set the lexical fallback added coverage without adding",
            "  any confident-wrong verdict. It is NOT a claim about general dialogue.",
            "no text generation; replies are templates + a proof rendering",
        ],
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()