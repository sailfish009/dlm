"""Can DLM learn and converse? An honest, runnable answer.

DLM has NO neural text generation. So a "conversation" here is:
    NL front-end (deterministic)  ->  DLM decision/proof  ->  NL verbalizer (templates)
and "learning" is symbolic:
    (1) KB growth      : asserting new facts
    (2) rule induction : induce_rules() generalizes Horn rules from examples

Run: python examples/conversation_demo.py
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dlm import DecisionEngine, Engine, KnowledgeBase, fact
from dlm.generalize import induce_rules

PARENT = [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]


# -- (front-end) deterministic NL -> atom. This is a PARSER, not the model. --
_ASSERT = re.compile(r"^(\w+) is a parent of (\w+)$")
_ASK_GP = re.compile(r"^is (\w+) a grandparent of (\w+)$")


def query_atom(utterance: str):
    m = _ASK_GP.match(utterance.strip().lower().rstrip("?"))
    return fact("grandparent", m.group(1), m.group(2)) if m else None


def assert_atom(utterance: str):
    m = _ASSERT.match(utterance.strip().lower())
    return fact("parent", m.group(1), m.group(2)) if m else None


# -- (verbalizer) proof -> English. Deterministic templates, no generation. --
def verbalize(sol) -> str:
    lines = [ln.strip() for ln in sol.proof.render().splitlines()]
    return "  proof: " + " | ".join(lines)


def main() -> None:
    kb = KnowledgeBase()
    for a, b in PARENT:
        kb.add_fact(fact("parent", a, b))

    print("== turn 1: DLM LEARNS a rule (induction, not gradient training) ==")
    positives = [fact("grandparent", "alice", "carol"), fact("grandparent", "bob", "dave")]
    negatives = [fact("grandparent", "carol", "alice"), fact("grandparent", "dave", "alice")]
    learned = induce_rules(kb, positives, negatives, max_body=2)
    for r in learned:
        kb.add_rule(r)
        print(f"  induced: {r}")
    if not learned:
        print("  (nothing induced)")

    engine = DecisionEngine(kb)
    print("\n== turn 2: DIALOGUE (symbolic Q&A + explanation) ==")
    for utterance in [
        "Is alice a grandparent of carol?",
        "Is dave a grandparent of alice?",
        "dave is a parent of erin",              # assert a fact -> KB grows
        "Is carol a grandparent of erin?",       # ask again (new fact used)
        "who likes cake?",                       # out-of-domain -> abstain
    ]:
        atom = assert_atom(utterance)
        if atom is not None:
            kb.add_fact(atom)
            print(f"user> {utterance}\n  DLM: noted {atom} (KB now {kb.num_facts} facts)")
            continue

        q = query_atom(utterance)
        if q is None:
            print(f"user> {utterance}\n  DLM: (abstain: no parser/grounding for this sentence)")
            continue

        ans = engine.noul(_noul(q))
        if ans.abstained:
            print(f"user> {utterance}\n  DLM: (abstain: could not ground the query)")
            continue
        verdict = "yes" if ans.noul > 0.5 else "no"
        print(f"user> {utterance}\n  DLM: {verdict}")
        if ans.noul > 0.5:
            sol = next(iter(Engine(kb).prove(q)), None)
            if sol is not None:
                print(verbalize(sol))

    print("\n== honest notes ==")
    print("  learning     = symbolic rule induction + KB growth (no neural training)")
    print("  conversation = parser -> proof -> template (no text generation)")
    print("  it fails on out-of-domain language, by design: it abstains instead of guessing")


def _noul(atom):
    from dlm.schema import NoulQuestion

    return NoulQuestion(instructions=str(atom))


if __name__ == "__main__":
    main()