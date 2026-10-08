"""Hybrid grounding demo (v0.0003, L5).

Shows the intended deployment stack behind ONE protocol:

    ChainGrounder([ GrammarGrounder(all phrases), CharNgramGrounder ])

  * known phrasing  -> T1 fires (exact, source="grammar")
  * unseen phrasing -> T1 abstains, the lexical T2 retrieves or abstains
  * the grounded atom is then run through the DLM proof engine

Honest note: on the v0.0003 benchmark the lexical T2 is the *default fallback*
because it beats the from-scratch learned encoder (see RESULTS_GROUNDING.md,
NEGATIVE_LEDGER NL-6). The learned T2 is intentionally NOT used here.
"""
from __future__ import annotations

from dlm import ByteTokenizer, ChainGrounder, GrammarGrounder, Pattern
from dlm.deduce import Engine
from dlm.grounder_learn import CharNgramGrounder, LearnedGrounder, synthesize_pairs
from dlm.kb import KnowledgeBase
from dlm.rules import fact, rule
from dlm.terms import Var

# phrases the grammar knows (T1)
KNOWN = [
    Pattern("is {x} a parent of {y}", "parent({x},{y})"),
    Pattern("{x} is a parent of {y}", "parent({x},{y})"),
    Pattern("is {x} a grandparent of {y}", "grandparent({x},{y})"),
    Pattern("is {x} an ancestor of {y}", "ancestor({x},{y})"),
    Pattern("is {x} a sibling of {y}", "sibling({x},{y})"),
]

ENTITIES = ("alice", "bob", "carol", "dave")


def build_hybrid(*, use_learned: bool = False):
    """T1 over all known phrases, then a lexical (or learned) retrieval T2."""
    train_pairs = synthesize_pairs(KNOWN, ENTITIES, seed=0)
    if use_learned:
        t2 = LearnedGrounder(ByteTokenizer(max_len=64), proj_dim=128, seed=0)
        t2.fit(train_pairs, epochs=150, lr=3e-3, seed=0)
    else:
        t2 = CharNgramGrounder(train_pairs)
    return ChainGrounder([GrammarGrounder(KNOWN), t2])


def build_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for f in [("parent", "alice", "bob"), ("parent", "bob", "carol"),
              ("parent", "carol", "dave")]:
        kb.add_fact(fact(*f))
    x, y, z = Var("x"), Var("y"), Var("z")
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, y), name="anc_base"))
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, z),
                       fact("ancestor", z, y), name="anc_step"))
    kb.add_rule(rule(fact("grandparent", x, y), fact("parent", x, z),
                       fact("parent", z, y), name="gp"))
    return kb


def main() -> None:
    grounder = build_hybrid()
    engine = Engine(build_kb())

    queries = [
        "is alice a parent of bob?",           # T1 (known phrasing)
        "is alice an ancestor of dave?",       # T1
        "is alice the mother of bob?",         # unseen phrasing -> T1 abstains,
                                               # lexical T2 may retrieve parent
        "is berlin the capital of germany?",   # out of domain -> abstain
    ]

    print("== hybrid grounding + proof ==\n")
    for q in queries:
        g = grounder.ground(q)
        if not g.ok:
            print(f"Q: {q}\n   -> ABSTAIN ({g.reason})\n")
            continue
        sols = list(engine.prove(g.atom))
        print(f"Q: {q}")
        print(f"   grounded : {g.atom}   [source={g.source}, conf={g.confidence:.2f}]")
        if sols:
            best = min(sols, key=lambda s: s.proof.depth())
            print(f"   proof    : true  (depth {best.proof.depth()}, leaves {best.proof.leaves()})")
            print("   trace    :")
            print("\n".join("      " + line for line in best.proof.render().splitlines()))
        else:
            print("   proof    : not derivable")
        print()

    print("note: the 'mother' query shows the honest limit of the lexical T2 -- it\n"
          "      retrieved ancestor(alice, bob) instead of parent(alice, bob).\n"
          "      Exact grounding is Tier 2 and imperfect (see RESULTS_GROUNDING.md,\n"
          "      NEGATIVE_LEDGER NL-6). Nothing here is generation; an unsafe atom\n"
          "      would be caught by the KB/ingestion gate, not by fluency.")


if __name__ == "__main__":
    main()