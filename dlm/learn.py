"""IR-native axiom revision: every input, candidate, verdict and transition is a Form."""
from __future__ import annotations

import math
from typing import Iterable, Sequence

from .ir import (Form, canonical_json, field, node_id, replace_field, sorted_forms,
                 validate_model_state, validate_rule, validate_transition)
from .kernel import (Rule, closure, episode_data, rule_from_ir, rule_to_ir,
                     safe, state_tier)
from .language import (default_language, execute_programs, program_origins,
                       update_program_stats)


class GroundConflict(ValueError):
    pass


def _memory_record(rule: Form, status: str, round_no: int,
                   sources: Sequence[str] = (), reason: str = "admitted") -> Form:
    return ("experience-record", ("id", node_id(rule)), ("rule", rule),
            ("status", status), ("round", round_no),
            ("support-sources", *tuple(sorted(sources))), ("reason", reason))


def new_state(episodes: Iterable[Form], *, ground: Iterable[Form] = (),
              experience: Iterable[Form] = (), subject: Form = ("none",),
              language: Form | None = None, lr: float = 0.2,
              margin: float = 1.0) -> Form:
    ground, experience = tuple(ground), tuple(experience)
    state: Form = (
        "model-state",
        ("version", "0.0.65"),
        ("round", 0),
        ("evidence", *tuple(episodes)),
        ("theory", ("ground", *sorted_forms(ground)),
         ("experience", *sorted_forms(experience))),
        ("memory", *(_memory_record(rule, "active", 0, reason="initial")
                      for rule in sorted_forms(experience))),
        language or default_language(),
        ("decision", ("lr", float(lr)), ("margin", float(margin)),
         ("updates", 0), ("weights",), ("replay",)),
        ("candidates",),
        ("verdicts",),
        ("events",),
        ("metrics", ("checks", 0), ("held-coverage", 0),
         ("held-total", 0), ("held-false", 0)),
        ("subject", subject),
    )
    validate_model_state(state)
    return state


def _episodes(state: Form, role: str | None = None) -> tuple[Form, ...]:
    result = tuple(field(state, "evidence")[1:])
    return result if role is None else tuple(
        episode for episode in result if episode_data(episode)["role"] == role)


def _theory_form(state: Form) -> Form:
    return field(state, "theory")


def _rules(state: Form) -> tuple[Rule, ...]:
    return state_tier(state, "ground") + state_tier(state, "experience")


def _replace_theory(state: Form, ground: Sequence[Rule], experience: Sequence[Rule]) -> Form:
    return replace_field(state, "theory",
                         ("theory", ("ground", *(rule_to_ir(r) for r in ground)),
                          ("experience", *(rule_to_ir(r) for r in experience))))


def _append_memory(state: Form, *records: Form) -> Form:
    return replace_field(state, "memory", ("memory", *field(state, "memory")[1:], *records))


def _blocked_rules(state: Form) -> set[Form]:
    return {field(record, "rule")[1] for record in field(state, "memory")[1:]
            if field(record, "status")[1] == "retracted"}


def synthesize(state: Form) -> tuple[Form, ...]:
    """Run the TreeLisp programs persisted inside the model state."""
    return execute_programs(state)


def _predicates(state: Form) -> tuple[tuple[str, ...], tuple[str, ...]]:
    facts, goals = set(), set()
    for episode in _episodes(state):
        data = episode_data(episode)
        facts |= {a.pred for a in data["facts"]}
        goals |= {a.pred for a in data["confirmed"]}
    return tuple(sorted(facts)), tuple(sorted(goals))


def _features(state: Form, candidate: Form) -> tuple[str, ...]:
    rule = rule_from_ir(candidate)
    facts, goals = _predicates(state)
    result = {"bias", f"head={rule.head.pred}", f"body={len(rule.body)}",
              "shape=" + ",".join(atom.pred for atom in rule.body)}
    result |= {f"fact={p}&head={rule.head.pred}" for p in facts}
    result |= {f"goal={p}&head={rule.head.pred}" for p in goals}
    result |= {f"program={name}" for name in program_origins(state, candidate)}
    return tuple(sorted(result))


def _decision(state: Form):
    decision = field(state, "decision")
    lr = float(field(decision, "lr")[1])
    margin = float(field(decision, "margin")[1])
    updates = int(field(decision, "updates")[1])
    weights = {weight[1]: float(weight[2]) for weight in field(decision, "weights")[1:]}
    replay = tuple(field(decision, "replay")[1:])
    return lr, margin, updates, weights, replay


def _with_decision(state: Form, weights: dict[str, float], updates: int,
                   replay: Sequence[Form]) -> Form:
    lr, margin, _, _, _ = _decision(state)
    decision = ("decision", ("lr", lr), ("margin", margin), ("updates", updates),
                ("weights", *(("weight", key, weights[key]) for key in sorted(weights))),
                ("replay", *tuple(replay)[-128:]))
    return replace_field(state, "decision", decision)


def value(state: Form, candidate: Form) -> float:
    _, _, _, weights, _ = _decision(state)
    return sum(weights.get(feature, 0.0) for feature in _features(state, candidate))


def rank(state: Form, candidates: Sequence[Form] | None = None) -> tuple[Form, ...]:
    actions = tuple(candidates if candidates is not None else field(state, "candidates")[1:])
    return tuple(sorted(actions, key=lambda action: (-value(state, action), canonical_json(action))))


def noul(state: Form, candidate: Form) -> float:
    score = max(-30.0, min(30.0, value(state, candidate)))
    return 1.0 / (1.0 + math.exp(-score))


def choice(state: Form, candidates: Sequence[Form] | None = None) -> Form:
    ordered = rank(state, candidates)
    return ordered[0] if ordered else ("noul",)


def ordinal_score(state: Form, levels: Sequence[Form]) -> float:
    if not levels:
        return 0.0
    logits = [value(state, action) for action in levels]
    maximum = max(logits)
    masses = [math.exp(x - maximum) for x in logits]
    total = sum(masses)
    return sum(index * mass / total for index, mass in enumerate(masses))


def _feedback(state: Form, candidate: Form, reward: float) -> Form:
    lr, _, updates, weights, replay = _decision(state)
    scale = max(-10.0, min(10.0, reward))
    for feature in _features(state, candidate):
        weights[feature] = weights.get(feature, 0.0) + lr * scale
    return _with_decision(state, weights, updates + 1, replay)


def _contrast(state: Form, positive: Form, negative: Form) -> Form:
    """Native state/action margin contrast using only kernel feedback."""
    lr, margin, updates, weights, replay = _decision(state)
    gap = value(state, positive) - value(state, negative)
    if gap < margin:
        for feature in _features(state, positive):
            weights[feature] = weights.get(feature, 0.0) + lr
        for feature in _features(state, negative):
            weights[feature] = weights.get(feature, 0.0) - lr
        updates += 1
    record = ("contrast", ("positive", node_id(positive)),
              ("negative", node_id(negative)), ("margin", margin), ("gap", gap))
    return _with_decision(state, weights, updates, (*replay, record))


def evaluate(state: Form, candidate: Form) -> Form:
    try:
        validate_rule(candidate)
        rule = rule_from_ir(candidate)
        formal = safe(rule)
    except (ValueError, TypeError):
        rule, formal = None, False
    episodes = _episodes(state)
    if not formal or rule is None:
        return ("verdict", ("formal", False), ("coverage", 0),
                ("debt", sum(len(episode_data(e)["confirmed"]) for e in episodes)),
                ("false-asserts", 0), ("support-sources",),
                ("mdl", 0), ("reward", -100.0), ("useful", False))
    theory = _rules(state)
    coverage = debt = false_asserts = 0
    sources: set[str] = set()
    for episode in episodes:
        data = episode_data(episode)
        before = closure(data["facts"], theory)
        after = closure(data["facts"], theory + (rule,))
        gained = (data["confirmed"] & after) - before
        coverage += len(gained)
        debt += len(data["confirmed"] - after)
        false_asserts += len(data["contradicted"] & after)
        if gained:
            sources.add(str(data["source"]))
    mdl = 1 + len(rule.body)
    reward = 4.0 * coverage + 2.0 * len(sources) - debt - 20.0 * false_asserts - .1 * mdl
    useful = coverage > 0 and false_asserts == 0
    return ("verdict", ("formal", True), ("coverage", coverage), ("debt", debt),
            ("false-asserts", false_asserts),
            ("support-sources", *tuple(sorted(sources))), ("mdl", mdl),
            ("reward", reward), ("useful", useful))


def _verdict_value(verdict: Form, name: str):
    return field(verdict, name)[1]


def _retract(state: Form) -> tuple[Form, tuple[Rule, ...]]:
    ground = state_tier(state, "ground")
    experience = state_tier(state, "experience")
    episodes = _episodes(state)
    for episode in episodes:
        data = episode_data(episode)
        if data["contradicted"] & closure(data["facts"], ground):
            raise GroundConflict("immutable Ground contradicts external evidence")
    kept: list[Rule] = []
    dropped: list[Rule] = []
    for rule in experience:
        trial = _replace_theory(state, ground, kept)
        verdict = evaluate(trial, rule_to_ir(rule))
        (kept if _verdict_value(verdict, "false-asserts") == 0 else dropped).append(rule)
    return _replace_theory(state, ground, kept), tuple(dropped)


def _held_metrics(state: Form) -> tuple[int, int, int]:
    episodes = _episodes(state, "validation") or _episodes(state)
    rules = _rules(state)
    covered = total = false_asserts = 0
    for episode in episodes:
        data = episode_data(episode)
        closed = closure(data["facts"], rules)
        covered += len(data["confirmed"] & closed)
        total += len(data["confirmed"])
        false_asserts += len(data["contradicted"] & closed)
    return covered, total, false_asserts


def _set_metrics(state: Form, checks: int) -> Form:
    old_checks = int(field(field(state, "metrics"), "checks")[1])
    covered, total, false_asserts = _held_metrics(state)
    return replace_field(state, "metrics",
                         ("metrics", ("checks", old_checks + checks),
                          ("held-coverage", covered), ("held-total", total),
                          ("held-false", false_asserts)))


def learn_round(state: Form, *, budget: int = 64, per_batch: int = 8,
                min_sources: int = 1) -> Form:
    """Return a pure transition. Only commit_transition may expose its after-state."""
    validate_model_state(state)
    before_ref = node_id(state)
    covered_before, _, false_before = _held_metrics(state)
    checked: list[Form] = []
    emitted: list[Form] = []
    checks = 0
    learned: list[Rule] = []
    target_round = int(field(state, "round")[1]) + 1
    try:
        work, dropped = _retract(state)
    except GroundConflict:
        event = ("learning-event", ("kind", "abstain"),
                 ("reason", "ground-contradiction"),
                 ("round", field(state, "round")[1]))
        return ("transition", ("before", before_ref),
                ("action", ("learn-round", ("budget", budget),
                            ("per-batch", per_batch), ("min-sources", min_sources))),
                ("verdicts",),
                ("events", event), ("after", state))

    if dropped:
        work = _append_memory(work, *(
            _memory_record(rule_to_ir(rule), "retracted", target_round,
                           reason="counterexample") for rule in dropped))
    pool = synthesize(work)
    work = replace_field(work, "candidates", ("candidates", *pool))
    tested: set[Form] = set()
    while checks < budget and not learned:
        existing = set(field(_theory_form(work), "ground")[1:]) | set(
            field(_theory_form(work), "experience")[1:])
        blocked = _blocked_rules(work)
        todo = [candidate for candidate in pool
                if candidate not in tested and candidate not in existing
                and candidate not in blocked]
        if not todo:
            break
        batch = rank(work, todo)[:min(per_batch, budget - checks)]
        winners = []
        for candidate in batch:
            tested.add(candidate)
            verdict = evaluate(work, candidate)
            checks += 1
            work = _feedback(work, candidate, float(_verdict_value(verdict, "reward")))
            supports = field(verdict, "support-sources")[1:]
            if _verdict_value(verdict, "useful") and len(supports) >= min_sources:
                winners.append((float(_verdict_value(verdict, "reward")),
                                canonical_json(candidate), candidate, verdict))
            checked.append(("checked", ("candidate", candidate), verdict,
                            ("admitted", False)))
        if not winners:
            continue
        _, _, chosen, chosen_verdict = max(winners)
        negatives = [
            (float(_verdict_value(record[2], "reward")), canonical_json(field(record, "candidate")[1]),
             field(record, "candidate")[1])
            for record in checked if field(record, "candidate")[1] != chosen
        ]
        if negatives:
            work = _contrast(work, chosen, min(negatives)[2])
        chosen_rule = rule_from_ir(chosen)
        ground = state_tier(work, "ground")
        experience = state_tier(work, "experience") + (chosen_rule,)
        work = _replace_theory(work, ground, experience)
        work = _append_memory(
            work, _memory_record(chosen, "active", target_round,
                                 tuple(field(chosen_verdict, "support-sources")[1:])))
        learned.append(chosen_rule)
        for index, record in enumerate(checked):
            if field(record, "candidate")[1] == chosen:
                checked[index] = ("checked", field(record, "candidate"),
                                  chosen_verdict, ("admitted", True))

    next_round = target_round
    work = replace_field(work, "round", ("round", next_round))
    previous_verdicts = field(work, "verdicts")[1:]
    work = replace_field(work, "verdicts", ("verdicts", *previous_verdicts, *checked))
    work = update_program_stats(
        work, tuple(field(record, "candidate")[1] for record in checked),
        tuple(rule_to_ir(rule) for rule in learned))
    work = _set_metrics(work, checks)
    covered_after, _, false_after = _held_metrics(work)
    improved = covered_after > covered_before or false_after < false_before
    if improved:
        event = ("learning-event", ("kind", "improvement"), ("round", next_round),
                 ("coverage-before", covered_before), ("coverage-after", covered_after),
                 ("false-before", false_before), ("false-after", false_after),
                 ("learned", *(rule_to_ir(rule) for rule in learned)),
                 ("retracted", *(rule_to_ir(rule) for rule in dropped)))
        emitted.append(event)
        work = replace_field(work, "events",
                             ("events", *field(work, "events")[1:], event))
    validate_model_state(work)
    return ("transition", ("before", before_ref),
            ("action", ("learn-round", ("budget", budget),
                        ("per-batch", per_batch), ("min-sources", min_sources))),
            ("verdicts", *checked),
            ("events", *emitted), ("after", work))


def commit_transition(state: Form, transition: Form) -> Form:
    """Recompute a transition before commit; a quoted/forged tree has no authority."""
    validate_transition(transition)
    if field(transition, "before")[1] != node_id(state):
        raise ValueError("transition does not apply to the current state")
    action = field(transition, "action")[1]
    if action[0] == "learn-round":
        expected = learn_round(
            state, budget=int(field(action, "budget")[1]),
            per_batch=int(field(action, "per-batch")[1]),
            min_sources=int(field(action, "min-sources")[1]))
    elif action[0] == "observe":
        proposed = field(transition, "after")[1]
        expected = observe(state, field(proposed, "evidence")[1:],
                           field(proposed, "subject")[1])
    else:
        raise ValueError("transition action is not an admitted capability")
    if canonical_json(expected) != canonical_json(transition):
        raise ValueError("transition failed deterministic re-verification")
    after = field(transition, "after")[1]
    validate_model_state(after)
    return after


def observe(state: Form, episodes: Iterable[Form], subject: Form) -> Form:
    """Create, but do not commit, a transition replacing external observations."""
    before = node_id(state)
    work = replace_field(state, "evidence", ("evidence", *tuple(episodes)))
    work = replace_field(work, "subject", ("subject", subject))
    work = replace_field(work, "candidates", ("candidates",))
    work = _set_metrics(work, 0)
    validate_model_state(work)
    return ("transition", ("before", before), ("action", ("observe", node_id(subject))),
            ("verdicts",), ("events",), ("after", work))


def stop_status(state: Form) -> Form:
    covered, total, false_asserts = _held_metrics(state)
    status = "saturated" if total > 0 and covered == total and false_asserts == 0 else "active"
    return ("stop-status", ("status", status), ("coverage", covered),
            ("total", total), ("false-asserts", false_asserts))
