"""DLM v0.0024 -- the fused core: a weighted clause set *is* the whole model.

(Unchanged since v0.0018/v0.0019.  v0.0020-v0.0024 add no core code; they add
separate, untrusted work -- :mod:`dlm.ssl` (IR self-supervision), :mod:`dlm.io`
(the data boundary), ``experiments/webloop`` (random-web dual-ability
self-supervision) and :mod:`dlm.selfsup` (the verifiable-reward self-supervised
loop that feeds this core the programs it verifies) -- which feed this core
frames and atoms and consume only kernel verdicts.)

One object does three jobs:

* a :class:`Clause` is a Horn rule the kernel uses (**truth**);
* the *same* clause is a weighted feature the scorer uses (**order**);
* a :class:`Theory` is an ordered set of clauses -- it is the rule set, the
  feature set and the model at once.

There is no separate feature map, model form or proposer: the theory *is* the
model.  Matching is one-way **subsumption** (a clause pattern's variables bind,
a matched clause/atom's variables stay opaque), so the scorer is a weighted
unification pattern matcher sharing the engine's term machinery.  Induction
(LGG) adds clauses, :func:`learn` reweights them, inference is the kernel's
proof.  Everything serialises to one form::

    (theory <name> (clause <name> <weight> (head) (body)...) ...)

Trust invariant: a clause's *structure* is truth, its *weight* is order.  A
weight never reaches the kernel and can never make an unprovable atom provable.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import (
    Atom,
    Const,
    Form,
    KnowledgeBase,
    Proof,
    Rule,
    SexpError,
    Subst,
    Sym,
    Term,
    Var,
    atom_to_form,
    closure,
    dump,
    form_to_atom,
    parse,
    prove,
    rule_to_form,
)


# ============================================================================
# 1. one matching mechanism: one-way subsumption
# ============================================================================
def _freshen(atom: Atom, mapping: Dict[Var, Var], prefix: str) -> Atom:
    """Rename each variable of ``atom`` apart (deterministic, ``prefix``+index)."""
    args: List[Term] = []
    for t in atom.args:
        if isinstance(t, Var):
            if t not in mapping:
                mapping[t] = Var(f"{prefix}{len(mapping)}")
            args.append(mapping[t])
        else:
            args.append(t)
    return Atom(atom.pred, tuple(args))


def _match_atom(pattern: Atom, target: Atom, subst: Subst) -> Optional[Subst]:
    """One-way match: bind ``pattern`` vars, treat ``target`` vars as opaque."""
    if pattern.pred != target.pred or pattern.arity != target.arity:
        return None
    out: Subst = dict(subst)
    for p, t in zip(pattern.args, target.args):
        if isinstance(p, Var):
            if p in out:
                if out[p] != t:
                    return None
            else:
                out[p] = t
        elif p != t:
            return None
    return out


def _match_body(
    patterns: List[Atom], candidates: List[Atom], subst: Subst
) -> Optional[Subst]:
    """Match pattern body atoms to distinct candidate atoms under ``subst``."""
    if not patterns:
        return subst
    first, rest = patterns[0], patterns[1:]
    for i, candidate in enumerate(candidates):
        extended = _match_atom(first, candidate, subst)
        if extended is None:
            continue
        got = _match_body(rest, candidates[:i] + candidates[i + 1 :], extended)
        if got is not None:
            return got
    return None


def head_subsumes(clause_rule: Rule, atom: Atom) -> bool:
    """Could ``clause_rule`` derive ``atom`` *structurally*?  (head match only.)

    A sound-but-bounded proxy: the clause head pattern must subsume the atom.
    The body is not checked, so this never reads the label.
    """
    return _match_atom(_freshen(clause_rule.head, {}, "__c"), atom, {}) is not None


def subsumes(pattern_rule: Rule, rule: Rule) -> bool:
    """One-way whole-shape cover: pattern head + each body atom matched distinctly."""
    mapping: Dict[Var, Var] = {}
    subst = _match_atom(_freshen(pattern_rule.head, mapping, "__c"), rule.head, {})
    if subst is None:
        return False
    body = [_freshen(b, mapping, "__c") for b in pattern_rule.body]
    return _match_body(body, list(rule.body), subst) is not None


# ============================================================================
# 2. the fused unit and the model
# ============================================================================
@dataclass(frozen=True)
class Clause:
    """A Horn rule plus a search weight -- truth and order in one object."""

    rule: Rule
    weight: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.rule, Rule):
            raise TypeError(f"a clause needs a Rule, got {self.rule!r}")
        if not isinstance(self.weight, (int, float)) or isinstance(self.weight, bool):
            raise TypeError(f"a weight must be a number, got {self.weight!r}")

    @property
    def name(self) -> str:
        return self.rule.name if self.rule.name is not None else dump(rule_to_form(self.rule))


@dataclass(frozen=True)
class Theory:
    """An ordered set of weighted clauses: the rules, features and model at once."""

    name: str
    clauses: Tuple[Clause, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "clauses", tuple(self.clauses))

    # -- views ------------------------------------------------------------
    def rules(self) -> Tuple[Rule, ...]:
        return tuple(c.rule for c in self.clauses)

    def names(self) -> Tuple[str, ...]:
        return tuple(c.name for c in self.clauses)

    @property
    def params(self) -> int:
        return len(self.clauses)

    def weights(self) -> Dict[str, float]:
        return {c.name: c.weight for c in self.clauses}

    def with_weights(self, weights: Dict[str, float]) -> "Theory":
        return Theory(
            self.name,
            tuple(Clause(c.rule, float(weights.get(c.name, c.weight))) for c in self.clauses),
        )

    def to_kb(self, base: Optional[KnowledgeBase] = None) -> KnowledgeBase:
        """Install only the rules (truth); weights stay behind."""
        kb = base.copy() if base is not None else KnowledgeBase()
        for rule in self.rules():
            kb.add_rule(rule)
        return kb

    def sorted(self) -> "Theory":
        return Theory(self.name, tuple(sorted(self.clauses, key=lambda c: (-c.weight, c.name))))

    # -- the fused feature/matcher ---------------------------------------
    def matched(self, item: object) -> Tuple[str, ...]:
        """Names of clauses whose pattern covers ``item`` (Atom or Rule)."""
        if isinstance(item, Atom):
            return tuple(c.name for c in self.clauses if head_subsumes(c.rule, item))
        if isinstance(item, Rule):
            return tuple(c.name for c in self.clauses if subsumes(c.rule, item))
        raise TypeError(f"a theory matches Atoms or Rules, got {item!r}")

    def features(self, item: object) -> Tuple[str, ...]:
        return ("bias", *self.matched(item))

    def score(self, item: object) -> float:
        w = self.weights()
        return sum(w[n] for n in self.matched(item))

    def top_features(self, n: int = 12) -> List[Tuple[str, float]]:
        return sorted(
            ((c.name, c.weight) for c in self.clauses),
            key=lambda kv: (-abs(kv[1]), kv[0]),
        )[:n]


# ============================================================================
# 3. the learner: hard-negative perceptron *on the clauses themselves*
# ============================================================================
def learn(
    theory: Theory,
    pairs: Iterable[Tuple[object, object]],
    *,
    epochs: int = 1,
    lr: float = 0.1,
) -> Tuple[Theory, int]:
    """Reweight clauses so positives outscore negatives; returns (theory, updates)."""
    weights = theory.weights()
    updates = 0
    for _ in range(max(0, int(epochs))):
        for positive, negative in pairs:
            pos = theory.matched(positive)
            neg = theory.matched(negative)
            if sum(weights[n] for n in pos) <= sum(weights[n] for n in neg):
                for n in pos:
                    weights[n] = weights.get(n, 0.0) + lr
                for n in neg:
                    weights[n] = weights.get(n, 0.0) - lr
                updates += 1
    return theory.with_weights(weights), updates


# ============================================================================
# 4. the dual learner: LGG (join) + greedy covering (meet) -> clauses
# ============================================================================
def _lgg_column(terms: Tuple[Term, ...], mapping: Dict[Tuple[Term, ...], Var]) -> Term:
    """LGG of one argument column; equal columns share one variable."""
    if all(t == terms[0] for t in terms):
        return terms[0]
    if terms not in mapping:
        mapping[terms] = Var(f"G{len(mapping)}")
    return mapping[terms]


def lgg_atoms(examples: Sequence[Atom]) -> Atom:
    """Least general generalization (anti-unification) of ground atoms."""
    if not examples:
        raise ValueError("lgg_atoms needs at least one example")
    first = examples[0]
    if any(a.pred != first.pred or a.arity != first.arity for a in examples):
        raise ValueError("lgg examples must share a predicate and arity")
    mapping: Dict[Tuple[Term, ...], Var] = {}
    args = tuple(
        _lgg_column(tuple(a.args[i] for a in examples), mapping) for i in range(first.arity)
    )
    return Atom(first.pred, args)


def variate(atom: Atom) -> Atom:
    """Replace each distinct constant by a fresh variable (``H0``, ``H1``...)."""
    seen: Dict[Term, Var] = {}
    args: List[Term] = []
    for t in atom.args:
        if isinstance(t, Var):
            args.append(t)
            continue
        if t not in seen:
            seen[t] = Var(f"H{len(seen)}")
        args.append(seen[t])
    return Atom(atom.pred, tuple(args))


def _signatures(kb: KnowledgeBase, target: Atom) -> List[Tuple[str, int]]:
    """Predicate/arity vocabulary available as a body literal (deterministic)."""
    sigs = {(target.pred, target.arity)}
    for f in kb.facts():
        sigs.add((f.pred, f.arity))
    for r in kb.rules():
        sigs.add((r.head.pred, r.head.arity))
    return sorted(sigs)


def literal_space(
    kb: KnowledgeBase, target: Atom, variables: Iterable[Var], *, max_arity: int = 3
) -> List[Atom]:
    """Candidate body atoms over the theory signature -- deterministic, deduped."""
    vars_ = tuple(variables)
    out: List[Atom] = []
    seen = set()
    for pred, arity in _signatures(kb, target):
        if arity <= 0 or arity > max_arity:
            continue
        for combo in itertools.product(vars_, repeat=arity):
            atom = Atom(pred, tuple(combo))
            key = (pred, tuple(str(x) for x in atom.args))
            if key not in seen:
                seen.add(key)
                out.append(atom)
    return out


def covers(
    kb: KnowledgeBase,
    rules: Iterable[Rule],
    positives: Iterable[Atom],
    negatives: Iterable[Atom],
) -> bool:
    """True iff adding ``rules`` derives every positive and no negative (kernel)."""
    trial = kb.copy()
    for rule in rules:
        try:
            trial.add_rule(rule)
        except ValueError:
            return False
    closed = closure(trial)
    return set(positives) <= closed and not (set(negatives) & closed)


def induce_clauses(
    kb: KnowledgeBase,
    positives: Iterable[Atom],
    negatives: Iterable[Atom],
    *,
    max_body: int = 2,
    extra_vars: int = 1,
    max_arity: int = 3,
    budget: int = 20000,
) -> Tuple[Clause, ...]:
    """Greedy shortest-consistent covering; clause weight = coverage fraction.

    Head = LGG of a predicate's positives; the body grows one literal at a time
    (shortest first), rejecting any candidate whose kernel closure covers a
    negative.  The weight is an *ordering* hint only; the rules are structure and
    a kernel still has to assert anything built on them.
    """
    pos = tuple(positives)
    negs = frozenset(negatives)
    by_pred: Dict[str, List[Atom]] = {}
    for atom in pos:
        by_pred.setdefault(atom.pred, []).append(atom)

    hypotheses: List[Clause] = []
    spent = 0
    for pred in sorted(by_pred):
        examples = sorted(by_pred[pred], key=str)
        head = lgg_atoms(examples) if len(examples) > 1 else variate(examples[0])
        head_vars = {str(v) for v in head.variables()}
        variables = list(head.variables()) + [Var(f"E{i}") for i in range(extra_vars)]
        universe = literal_space(kb, examples[0], variables, max_arity=max_arity)
        uncovered = set(examples)
        index = 0
        while uncovered:
            best: Optional[Rule] = None
            best_closed: set = set()
            for length in range(1, max_body + 1):
                level: List[Tuple[int, str, Rule, set]] = []
                for combo in itertools.combinations(universe, length):
                    if spent >= budget:
                        break
                    spent += 1
                    body_vars = {str(x) for lit in combo for x in lit.args if isinstance(x, Var)}
                    if not head_vars <= body_vars:
                        continue
                    candidate = Rule(head, combo, f"lgg_{pred}_{index}")
                    trial = kb.copy()
                    for c in hypotheses:
                        trial.add_rule(c.rule)
                    try:
                        trial.add_rule(candidate)
                    except ValueError:
                        continue
                    closed = closure(trial)
                    if negs & closed:
                        continue
                    gain = len(uncovered & closed)
                    if gain > 0:
                        level.append((gain, str(candidate), candidate, closed))
                if level:
                    level.sort(key=lambda t: (t[0], t[1]), reverse=True)
                    _, _, best, best_closed = level[0]
                    break
                if spent >= budget:
                    break
            if best is None:
                break
            covered_now = len(uncovered & best_closed)
            hypotheses.append(Clause(best, covered_now / len(examples)))
            uncovered = {a for a in uncovered if a not in best_closed}
            index += 1
            if spent >= budget:
                break
    return tuple(hypotheses)


# ============================================================================
# 5. the kernel gate: rank with the theory, then let the kernel decide
# ============================================================================
@dataclass(frozen=True)
class Decision:
    """One fused decision: the atom the *kernel* accepted, plus the tried order."""

    chosen: Optional[Atom]
    proof: Optional[Proof]
    ranked: Tuple[Tuple[Atom, float], ...]

    @property
    def abstained(self) -> bool:
        return self.chosen is None

    def to_dict(self) -> dict:
        return {
            "chosen": None if self.chosen is None else str(self.chosen),
            "abstained": self.abstained,
            "proved": self.proof is not None,
            "ranked": [{"atom": str(a), "score": s} for a, s in self.ranked],
        }


def solve(
    kb: KnowledgeBase,
    theory: Theory,
    candidates: Iterable[Atom],
) -> Decision:
    """Rank candidates by ``theory.score``; choose the first the kernel proves.

    The score can change *which* provable atom wins but never makes an
    unprovable one assert: the kernel's closure is the gate, and an empty gate
    abstains visibly.
    """
    closed = closure(kb)
    scored = sorted(
        ((a, theory.score(a)) for a in candidates),
        key=lambda t: (-t[1], str(t[0])),
    )
    ranked = tuple((a, float(s)) for a, s in scored)
    for atom, _ in scored:
        if atom in closed:
            return Decision(atom, prove(kb, atom), ranked)
    return Decision(None, None, ranked)


# ============================================================================
# 6. one form: (theory <name> (clause ...) ...)
# ============================================================================
_SAFE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-=<>.,?*+%$")


def _sym_or_str(text: object) -> Form:
    """A name as a bare ``Sym`` when symbol-safe, else a quoted ``str``."""
    s = str(text)
    return Sym(s) if s and all(ch in _SAFE for ch in s) else s


def _is_number(value: Form) -> bool:
    if not isinstance(value, Sym):
        return False
    try:
        float(str(value))
    except ValueError:
        return False
    return True


def _weight_sym(w: float) -> Sym:
    """A weight as a symbol that reads back to the same float (``+`` on positives)."""
    text = repr(float(w))
    return Sym("+" + text if w > 0 and not text.startswith("+") else text)


def _parse_clause_parts(form: Form) -> Tuple[Optional[str], float, Form, Tuple[Form, ...]]:
    """Split ``(clause [name] [weight] (head) (body)...)`` into its parts."""
    if not isinstance(form, tuple) or not form or form[0] != Sym("clause"):
        raise SexpError(f"not a clause form: {form!r}")
    rest = list(form[1:])
    head_idx = next((i for i, x in enumerate(rest) if isinstance(x, tuple)), None)
    if head_idx is None:
        raise SexpError(f"clause form has no head: {form!r}")
    lead = rest[:head_idx]
    name: Optional[str] = None
    weight = 0.0
    if len(lead) == 1:
        if _is_number(lead[0]):
            weight = float(str(lead[0]))
        else:
            name = str(lead[0])
    elif len(lead) == 2:
        name = str(lead[0])
        try:
            weight = float(str(lead[1]))
        except ValueError as exc:
            raise SexpError(f"clause weight is not a number: {lead[1]!r}") from exc
    elif len(lead) > 2:
        raise SexpError(f"too many items before the head: {form!r}")
    return name, weight, rest[head_idx], tuple(rest[head_idx + 1 :])


def clause_to_form(clause: Clause) -> tuple:
    """``(clause <name> <weight> (head) (body)...)`` -- structure and order in one."""
    rule = clause.rule
    parts: list = [Sym("clause")]
    if rule.name is not None:
        parts.append(_sym_or_str(rule.name))
    parts.append(_weight_sym(float(clause.weight)))
    parts.append(atom_to_form(rule.head))
    parts.extend(atom_to_form(b) for b in rule.body)
    return tuple(parts)


def clause_from_form(form: Form) -> Clause:
    """Read a clause form back (name and weight optional)."""
    name, weight, head_form, body_forms = _parse_clause_parts(form)
    if not body_forms:
        raise SexpError("a clause needs a non-empty body")
    return Clause(
        Rule(form_to_atom(head_form), tuple(form_to_atom(b) for b in body_forms), name),
        weight,
    )


def theory_to_form(theory: Theory) -> tuple:
    """``(theory <name> (clause ...) ...)`` -- the whole model in one form."""
    return (Sym("theory"), _sym_or_str(theory.name), *(clause_to_form(c) for c in theory.clauses))


def theory_from_form(form: Form) -> Theory:
    """Read a ``(theory ...)`` form back into a :class:`Theory`."""
    if not isinstance(form, tuple) or len(form) < 2 or form[0] != Sym("theory"):
        raise SexpError(f"not a theory form: {form!r}")
    return Theory(str(form[1]), tuple(clause_from_form(f) for f in form[2:]))


def theory_sexp(theory: Theory) -> str:
    """Canonical S-expr text of a theory."""
    return dump(theory_to_form(theory))


def theory_from_sexp(text: str) -> Theory:
    """Parse exactly one ``(theory ...)`` form into a :class:`Theory`."""
    forms = parse(text)
    if len(forms) != 1:
        raise SexpError(f"expected exactly one theory form, got {len(forms)}")
    return theory_from_form(forms[0])


# ============================================================================
# 7. one end-to-end experiment: induce -> learn -> verify
# ============================================================================
def _chain_kb(n: int) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(n - 1):
        kb.add_fact(Atom("parent", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


def _reach(n: int) -> Dict[str, set]:
    reach = {f"n{i}": set() for i in range(n)}
    for i in range(n - 1):
        reach[f"n{i}"].add(f"n{i + 1}")
    for i in range(n - 2, -1, -1):
        for j in list(reach[f"n{i}"]):
            reach[f"n{i}"] |= reach.get(j, set())
    return reach


def run_experiment(*, n: int = 12, train_end: int = 6, epochs: int = 40, budget: int = 20000) -> dict:
    """Train on early chain entities, hold out later ones; induce, learn, verify."""
    kb = _chain_kb(n)
    reach = _reach(n)

    def anc(a: str, b: str) -> Atom:
        return Atom("ancestor", (Const(a), Const(b)))

    train = [f"n{i}" for i in range(train_end)]
    test = [f"n{i}" for i in range(train_end, n)]
    all_names = [f"n{i}" for i in range(n)]
    positives = sorted((anc(a, b) for a in train for b in train if a != b and b in reach[a]), key=str)
    negatives = sorted((anc(a, b) for a in train for b in train if a != b and b not in reach[a]), key=str)
    held_pos = [anc(a, b) for a in all_names for b in test if a != b and b in reach[a]]
    held_neg = [anc(a, b) for b in test for a in all_names if a != b and b not in reach[a]]

    induced = induce_clauses(kb, positives, negatives, budget=budget)

    # the fused learner orders *clauses* by their shape: a good recursive clause
    # must be preferred over a reversed decoy.  Weight is order, never truth.
    recursive = next((c for c in induced if len(c.rule.body) == 2), None)
    decoy = Clause(
        Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("parent", (Var("y"), Var("x"))),), "decoy"),
        0.0,
    )
    theory0 = Theory("ancestor", tuple(Clause(c.rule, 0.0) for c in (*induced, decoy)))
    pairs = [] if recursive is None else [(recursive.rule, decoy.rule)]
    learned, updates = learn(theory0, pairs, epochs=epochs, lr=0.1)

    # the kernel only ever sees structure (no decoy); the decoy is order only
    proving = Theory("ancestor", induced)
    kb_full = proving.to_kb(kb)
    proved = sum(1 for a in held_pos if a in closure(kb_full))
    false_assert = sum(1 for a in held_neg if a in closure(kb_full))

    # ordering demo: the learned weight separates the recursive clause from the decoy
    order = {
        "recursive_score": round(learned.score(recursive.rule), 4) if recursive else None,
        "decoy_score": round(learned.score(decoy.rule), 4),
    }
    order["separated"] = (
        recursive is not None and order["recursive_score"] > order["decoy_score"]
    )

    held = sorted(set(held_pos) | set(held_neg), key=str)
    decision = solve(kb_full, learned, held)
    text = theory_sexp(learned)
    parsed = theory_from_sexp(text)
    roundtrip = {
        "rules": [str(r) for r in parsed.rules()] == [str(r) for r in learned.rules()],
        "weights": parsed.weights() == learned.weights(),
    }
    proved_from_form = sum(1 for a in held_pos if a in closure(parsed.to_kb(kb)))

    return {
        "train_positives": len(positives),
        "train_negatives": len(negatives),
        "clauses": [str(c.rule) for c in induced],
        "weights": learned.weights(),
        "params": learned.params,
        "updates": updates,
        "order": order,
        "heldout_positives_proved": proved,
        "heldout_positives_total": len(held_pos),
        "heldout_negatives_false_assert": false_assert,
        "heldout_negatives_total": len(held_neg),
        "theory_form": text,
        "theory_roundtrip": roundtrip,
        "heldout_proved_from_parsed_form": proved_from_form,
        "gate": {"chosen": None if decision.chosen is None else str(decision.chosen),
                 "proved": decision.proof is not None},
    }


def _main() -> None:
    import json

    print(json.dumps(run_experiment(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _main()
