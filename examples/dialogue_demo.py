"""Grounded dialogue demo (v0.0003, W4).

End-to-end proof that the loop is assembled, not just the parts:

    ChainGrounder([GrammarGrounder(T1), CharNgramGrounder(lexical T2)])
        -> DialogueSession (DecisionEngine + proof + template verbalizer)

Shows, in order:
  * a rule is LEARNED by symbolic induction (not gradient training)
  * a conversation: query -> proof, tell -> KB growth, then a new deduction
  * unseen phrasing falls through T1 to the lexical T2 (which may be wrong)
  * out-of-domain language ABSTAINS instead of guessing

Run: PYTHONPATH=. python3 examples/dialogue_demo.py
"""
from __future__ import annotations

from dlm import (
    ChainGrounder,
    DialogueSession,
    GrammarGrounder,
    KnowledgeBase,
    Pattern,
    fact,
    rule,
)
from dlm.dialogue import ABSTAIN, REJECT
from dlm.generalize import induce_rules
from dlm.grounder_learn import CharNgramGrounder, synthesize_pairs
from dlm.terms import Var

TRAIN = [
    Pattern("is {x} a parent of {y}", "parent({x},{y})"),
    Pattern("{x} is a parent of {y}", "parent({x},{y})"),
    Pattern("is {x} a grandparent of {y}", "grandparent({x},{y})"),
    Pattern("is {x} an ancestor of {y}", "ancestor({x},{y})"),
    Pattern("is {x} a sibling of {y}", "sibling({x},{y})"),
]
ENTITIES = ("alice", "bob", "carol", "dave")


def build_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]:
        kb.add_fact(fact("parent", a, b))
    x, y, z = Var("x"), Var("y"), Var("z")
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, y), name="anc_base"))
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, z),
                     fact("ancestor", z, y), name="anc_step"))
    return kb


def build_session() -> DialogueSession:
    kb = build_kb()
    grounder = ChainGrounder([
        GrammarGrounder(TRAIN),
        CharNgramGrounder(synthesize_pairs(TRAIN, ENTITIES, seed=0)),
    ])
    return DialogueSession(kb, grounder)


def main() -> None:
    kb = build_kb()

    print("== step 1: DLM LEARNS a rule (induction, not gradient training) ==")
    positives = [fact("grandparent", "alice", "carol"), fact("grandparent", "bob", "dave")]
    negatives = [fact("grandparent", "carol", "alice"), fact("grandparent", "dave", "alice")]
    for r in induce_rules(kb, positives, negatives, max_body=2):
        kb.add_rule(r)
        print(f"  induced: {r}")

    s = DialogueSession(
        kb,
        ChainGrounder([
            GrammarGrounder(TRAIN),
            CharNgramGrounder(synthesize_pairs(TRAIN, ENTITIES, seed=0)),
        ]),
    )

    print("\n== step 2: CONVERSATION (ground -> prove/assert -> template reply) ==")
    turns = [
        ("Is alice a grandparent of carol?", "ask"),
        ("Is dave an ancestor of alice?", "ask"),
        ("dave is a parent of erin", "tell"),          # KB grows
        ("Is carol an ancestor of erin?", "ask"),      # deduction uses the new fact
        ("is alice the mother of bob", "ask"),         # unseen phrasing -> lexical T2
        ("does berlin like cake", "ask"),              # out of domain -> abstain
    ]
    for utterance, intent in turns:
        reply = s.ask(utterance) if intent == "ask" else s.tell(utterance)
        tag = "" if reply.kind not in (ABSTAIN, REJECT) else " [abstained]"
        print(f"user> {utterance}")
        print(f"  DLM: {reply.text}{tag}")
        if reply.grounding is not None and reply.grounding.ok:
            print(f"       (grounded via {reply.grounding.source}, "
                  f"provenance={reply.provenance})")
        print()

    print("== honest notes ==")
    print("  conversation = ground -> proof -> template; there is NO generation and")
    print("                 the only variable text is a rendering of the proof tree")
    print("  learning     = symbolic rule induction + KB growth (no neural training)")
    print("  ceiling      = the grounder's. Unseen phrasing falls to the lexical T2,")
    print("                 which can ground the WRONG atom and then proofs are sound")
    print("                 but about the wrong thing (NEGATIVE_LEDGER NL-6).")
    print("  safety       = ungrounded input abstains; contradiction is rejected.")


if __name__ == "__main__":
    main()