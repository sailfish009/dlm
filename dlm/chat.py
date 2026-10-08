"""Interactive grounded dialogue for DLM. No text generation anywhere.

    dlm-chat              # installed console script
    python -m dlm.chat    # same thing

The session is the v0.0003 `DialogueSession`:

    your sentence -- ChainGrounder([grammar T1, lexical T2]) --> atoms
        statement -> KB growth (noted)      question -> proof -> yes/no + trace
        no grounder -> abstain              contradicts KB -> reject

Facts you assert are tagged `user`; conclusions that depend on them are labelled
`provenance=user`. Nothing here is generated: the only dynamic text is a
rendering of a proof tree.

Commands inside the loop:
    :help   :kb   :facts   :rules   :user   :quit
"""
from __future__ import annotations

import shlex
from typing import List, Optional

from .dialogue import ABSTAIN, ANSWER, ASSERT, REJECT, DialogueSession
from .grounder_learn import CharNgramGrounder, synthesize_pairs
from .grounding import ChainGrounder, GrammarGrounder, Pattern
from .kb import KnowledgeBase
from .rules import fact, rule
from .terms import Var

__all__ = [
    "ENTITIES", "QUERY_PATTERNS", "ASSERT_PATTERNS", "TRAIN_PATTERNS",
    "build_kb", "build_session", "handle", "banner", "main",
]

ENTITIES = ("alice", "bob", "carol", "dave", "erin")

# Questions start with "is"; statements are "X is ...". Distinct surface forms,
# so `say()` can trust the grounder's `kind`.
QUERY_PATTERNS: List[Pattern] = [
    Pattern("is {x} a parent of {y}", "parent({x},{y})"),
    Pattern("is {x} a grandparent of {y}", "grandparent({x},{y})"),
    Pattern("is {x} an ancestor of {y}", "ancestor({x},{y})"),
    Pattern("is {x} a sibling of {y}", "sibling({x},{y})"),
]
ASSERT_PATTERNS: List[Pattern] = [
    Pattern("{x} is a parent of {y}", "parent({x},{y})", kind="assert"),
]
TRAIN_PATTERNS: List[Pattern] = ASSERT_PATTERNS + QUERY_PATTERNS


def build_kb() -> KnowledgeBase:
    """The starter domain: one family, plus ancestor/grandparent rules."""
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


def build_session() -> DialogueSession:
    """T1 grammar over known phrasing, then the adopted lexical T2 fallback."""
    grounder = ChainGrounder([
        GrammarGrounder(TRAIN_PATTERNS),
        CharNgramGrounder(synthesize_pairs(TRAIN_PATTERNS, ENTITIES, seed=0)),
    ])
    return DialogueSession(build_kb(), grounder)


def banner() -> str:
    return (
        "DLM dialogue (grounded, no generation). Domain: alice->bob->carol->dave.\n"
        "  ask   : is alice an ancestor of dave\n"
        "  tell  : erin is a parent of frank      (grows the KB)\n"
        "  deny  : alice is not a parent of dave  (consistency check)\n"
        "  cmds  : :help :kb :facts :rules :user :quit\n"
        "Honest note: unseen phrasing falls back to a lexical grounder, which can\n"
        "pick the WRONG atom (then the proof is sound but about the wrong thing);\n"
        "ungrounded input abstains instead of guessing."
    )


_HELP = (
    ":kb      fact/rule counts\n"
    ":facts   list the facts\n"
    ":rules   list the rules\n"
    ":user    facts you asserted (user provenance)\n"
    ":quit    leave (Ctrl-D also works)"
)


def handle(session: DialogueSession, line: str) -> Optional[str]:
    """Process one input line. Returns the text to print, or None to quit."""
    text = line.strip()
    if not text:
        return "(empty input — try: is alice an ancestor of dave)"
    if text.startswith(":"):
        cmd = text.split()[0]
        if cmd in (":quit", ":exit", ":q"):
            return None
        if cmd == ":help":
            return _HELP
        if cmd == ":kb":
            return f"facts={session.kb.num_facts} rules={session.kb.num_rules}"
        if cmd == ":facts":
            return "\n".join(f"  {a}" for a in sorted(session.kb.facts(), key=str)) or "  (none)"
        if cmd == ":rules":
            return "\n".join(f"  {r}" for r in sorted(session.kb.rules(), key=str)) or "  (none)"
        if cmd == ":user":
            return "\n".join(f"  {a}" for a in sorted(session.user_facts)) or "  (none)"
        return f"unknown command {cmd!r} — try :help"

    reply = session.say(text)
    out = [f"DLM: {reply.text}"]
    g = reply.grounding
    if g is not None and g.ok:
        out.append(f"     [grounded={g.source} atom={g.atom} provenance={reply.provenance}"
                   f" kind={reply.kind}]")
    elif reply.kind in (ABSTAIN, REJECT):
        out.append(f"     [{reply.kind}: {reply.reason or 'no grounding'}]")
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    session = build_session()
    print(banner())
    while True:
        try:
            line = input("you> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        out = handle(session, line)
        if out is None:
            break
        print(out)
    print(f"bye — facts={session.kb.num_facts} (user-asserted={len(session.user_facts)})")
    return 0


if __name__ == "__main__":  # python -m dlm.chat
    raise SystemExit(main())