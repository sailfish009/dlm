"""DLM v0.0056 -- ability self-evaluation (untrusted, kernel-only).

The model's deduction targets are **unrestricted**: whatever its rules promise to
conclude.  There is no fixed goal list.  :func:`target_predicates` reads the
theory and returns every predicate some rule has as its head -- those are the
conclusions the model has committed to being able to reach.

:func:`ability_profile` then reads the **kernel closure only** and reports, for
every target, whether the model currently PROVES it (at least one atom derived)
or is BLOCKED, and by which absent premises.  :func:`weak_spots` turns that into
an ordered agenda (actionable external premises first), and :func:`improvement`
scores one self-improvement round.

Nothing is asserted here.  A weak spot is a *question*, not a fact: "this target
cannot fire because this premise is missing".  Only the kernel decides truth, and
:mod:`dlm.curriculum` is what acts on the question.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

from . import Atom, KnowledgeBase, Rule, closure

__all__ = ["Ability", "WeakSpot", "rule_heads", "target_predicates",
           "ability_profile", "weak_spots", "improvement"]


def rule_heads(rules: Iterable[Rule]) -> Tuple[str, ...]:
    """Every predicate some rule can conclude (sorted, de-duplicated)."""
    return tuple(sorted({r.head.pred for r in rules}))


def target_predicates(rules: Iterable[Rule], facts: Iterable[Atom] = ()) -> Tuple[str, ...]:
    """The model's deduction PROMISES: all rule heads, plus any fact predicate.

    Including fact predicates means a target the model can only *observe* (never
    derive) still shows up in the profile as an unproved rule-less target -- an
    honest gap.  Order is sorted for determinism.
    """
    heads = {r.head.pred for r in rules}
    preds = {a.pred for a in facts if a.args}
    return tuple(sorted(heads | preds))


def _derived_counts(closed: Iterable[Atom]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for a in closed:
        counts[a.pred] = counts.get(a.pred, 0) + 1
    return counts


@dataclass(frozen=True)
class Ability:
    """A read-only snapshot of what the model can and cannot currently conclude."""

    targets: Tuple[str, ...]
    proved: Mapping[str, int]           # target -> # atoms in the kernel closure
    open: Tuple[str, ...]               # targets with zero derived atoms
    blocked: Mapping[str, Tuple[str, ...]]  # open target -> absent body predicates
    external: Mapping[str, Tuple[str, ...]]  # open target -> absent *acquirable* premises
    rules_for: Mapping[str, int]        # target -> # rules with that head
    derived_total: int
    evidence: Optional[dict] = None

    # -- queries -----------------------------------------------------------
    def is_proved(self, pred: str) -> bool:
        return self.proved.get(pred, 0) > 0

    @property
    def actionable(self) -> Tuple[str, ...]:
        """Weak targets whose missing premise is externally acquirable."""
        return tuple(sorted(t for t in self.open if self.external.get(t)))

    def to_dict(self) -> dict:
        return {
            "targets": list(self.targets),
            "proved": {k: self.proved[k] for k in self.targets if self.proved.get(k)},
            "open": list(self.open),
            "blocked": {k: list(v) for k, v in self.blocked.items()},
            "external": {k: list(v) for k, v in self.external.items()},
            "rules_for": dict(self.rules_for),
            "derived_total": self.derived_total,
            "actionable": list(self.actionable),
            "evidence": self.evidence,
        }


def ability_profile(rules: Sequence[Rule], closed: Iterable[Atom], *,
                    facts: Iterable[Atom] = (), external: Iterable[str] = (),
                    targets: Optional[Sequence[str]] = None,
                    evidence: Optional[dict] = None) -> Ability:
    """Assess the model against its own deduction targets, from the closure only.

    ``closed`` is the kernel closure (the ground truth of what can be proved);
    ``rules`` is the theory; ``external`` lists predicates that only acquired
    (searched) knowledge can supply -- so a blocker naming one of them is a
    question the model could answer on the web, and the rest are structural gaps
    it cannot.  ``evidence`` (optional) is ``{"positives": set, "negatives": set}``
    for a held-out recall / false-assert read.
    """
    rules = tuple(rules)
    closed = set(closed)
    derived = _derived_counts(closed)
    derived_preds = set(derived)
    extern = frozenset(external)
    tlist = tuple(targets) if targets is not None else target_predicates(rules, facts)

    head_rules: Dict[str, list] = {}
    for r in rules:
        head_rules.setdefault(r.head.pred, []).append(r)

    proved: Dict[str, int] = {}
    open_t: list = []
    blocked: Dict[str, Tuple[str, ...]] = {}
    ext: Dict[str, Tuple[str, ...]] = {}
    rules_for: Dict[str, int] = {}
    for t in tlist:
        rules_for[t] = len(head_rules.get(t, ()))
        proved[t] = derived.get(t, 0)
        if proved[t]:
            continue
        open_t.append(t)
        missing = set()
        for r in head_rules.get(t, ()):
            for lit in r.body:
                if lit.pred != t and lit.pred not in derived_preds:
                    missing.add(lit.pred)
        blocked[t] = tuple(sorted(missing))
        ext[t] = tuple(sorted(missing & extern))

    ev = None
    if evidence is not None:
        pos = set(evidence.get("positives", ()))
        neg = set(evidence.get("negatives", ()))
        fn = sorted((a for a in pos if a not in closed), key=str)
        fp = sorted((a for a in neg if a in closed), key=str)
        ev = {
            "positives": len(pos),
            "negatives": len(neg),
            "recall": (1.0 if not pos else (len(pos) - len(fn)) / len(pos)),
            "false_negatives": [str(a) for a in fn],
            "false_asserts": [str(a) for a in fp],
        }

    return Ability(
        targets=tlist,
        proved=proved,
        open=tuple(open_t),
        blocked=blocked,
        external=ext,
        rules_for=rules_for,
        derived_total=len(closed),
        evidence=ev,
    )


@dataclass(frozen=True)
class WeakSpot:
    """One target the model cannot yet conclude, and why.

    ``kind`` is ``"premise"`` when the target has rules but a body premise is
    absent, ``"absent"`` when the target has no rule at all (a pure observation
    the model can never derive), and ``"rule"`` when it has a rule but no missing
    (non-self) premise -- a rule that simply never fires.
    """

    kind: str
    target: str
    missing: Tuple[str, ...]
    external: Tuple[str, ...]
    rules_for: int

    @property
    def actionable(self) -> bool:
        return bool(self.external)

    def to_dict(self) -> dict:
        return {"kind": self.kind, "target": self.target,
                "missing": list(self.missing), "external": list(self.external),
                "rules_for": self.rules_for, "actionable": self.actionable}


def weak_spots(ab: Ability) -> Tuple[WeakSpot, ...]:
    """Ordered agenda: actionable external premises first, then the rest."""
    spots = []
    for t in ab.open:
        missing = ab.blocked.get(t, ())
        ext = ab.external.get(t, ())
        if ext:
            kind = "premise"
        elif ab.rules_for.get(t, 0) == 0:
            kind = "absent"
        elif missing:
            kind = "premise"
        else:
            kind = "rule"
        spots.append(WeakSpot(kind, t, tuple(missing), tuple(ext),
                              ab.rules_for.get(t, 0)))
    return tuple(sorted(spots, key=lambda s: (not s.actionable, s.target)))


def improvement(before: Ability, after: Ability) -> dict:
    """Score a self-improvement round against the previous ability snapshot.

    Progress is measured at the TARGET level (a target newly proved, or an
    already-proved target with more derived atoms) -- never by the mere presence of
    a supplied predicate.  This is what stops a scrambled/irrelevant fact from
    looking like improvement: only the kernel's actual derivations count.
    """
    gained = tuple(sorted(t for t in before.targets
                          if not before.is_proved(t) and after.is_proved(t)))
    deepened = tuple(sorted(t for t in before.targets
                            if before.is_proved(t)
                            and after.proved.get(t, 0) > before.proved.get(t, 0)))
    regressed = tuple(sorted(t for t in before.targets
                             if before.is_proved(t) and not after.is_proved(t)))
    delta = after.derived_total - before.derived_total
    return {
        "gained": gained,
        "deepened": deepened,
        "regressed": regressed,
        "delta_derived": delta,
        "improved": bool(gained or deepened),
    }