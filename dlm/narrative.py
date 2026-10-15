"""DLM v0.0050 -- the leveled narrative realizer (untrusted, kernel-checked).

The v0.0043 pipeline could *list* facts and *name* a core concept, but every
sentence had the same flat shape (one atom -> one template) and the only
"structure" output was a raw source-order arrow chain.  This layer gives the
final natural-language output a measured **level**:

    N1 relation      "main imports torch."                    (a fact)
    N2 meaning       "Net is a PyTorch module."               (acquired meaning applied)
    N3 idiom         "train performs a training step."        (single-subject conjunction)
    N4 composition   "train runs one gradient step: reset ->  (a NAMED, bounded
                      forward/loss -> backward -> update."     subgraph, not a raw chain)
    N5 architecture  "Net.forward is a conv -> relu -> ...    (role-normalised topology)
                      -> linear -> softmax network."
    N9 absence       "Net does not contain a maxpool2d        (a certified NEGATIVE,
                      layer."                                  closed-world negation)

v0.0050 adds the first NEGATIVE sentence (N9): ``absent(?m,?l)`` is derivable only
by stratified closed-world negation over a GIVEN candidate universe, and it is
NON-MONOTONIC -- adding one ``has_layer`` fact retracts the matching sentence.
Pure Horn deduction can never produce it.  Typing (D6) is deliberately NOT a
sentence level: it GATES admission (an ill-typed theory makes the reader abstain),
it never asserts a truth.

Nothing here asserts truth.  Every sentence carries the atoms (``support``) that
entail it and ``run.py`` refuses to print a sentence whose support is not in the
kernel closure.  The naming ("gradient step", "convolution block") is presentation
done by the UNTRUSTED realizer; the *facts* (calls/before/has_layer, acquired
``meaning``) come from the kernel closure.  No library symbol is named by the
interpreter; the level-4/5 boundary uses acquired meanings where available and a
small, auditable presentation lexicon otherwise (never consulted for truth).

v0.0053 exports ``LEVEL_NOTE`` (each rung's KIND: presentation vs deduction vs
knowledge-dependent) and ``analyze_sentences(sentences, closed)`` -- a read-only
report over an already-built reading (per-level counts, certification, whether
every support atom is really in the kernel closure, the negative sentences, and
which rungs are presentation-only / knowledge-dependent).  The north-star BODY
uses the same ``reading`` and this report; see ``experiments/mnist/run.py``.
"""
from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import Atom
from .gist import concept_atoms, concept_str

__all__ = ["LEVELS", "LEVEL_NAMES", "LEVEL_NOTE", "reading", "reading_level",
           "reading_score", "analyze_sentences"]

# The reading ladder.  N-numbers are the "sentence level" of the final output.
LEVELS: Dict[int, str] = {
    1: "relation",
    2: "meaning",
    3: "idiom",
    4: "composition",
    5: "architecture",
    6: "causal",
    7: "purpose",
    8: "analogy",
    9: "absence",
}
LEVEL_NAMES = {v: k for k, v in LEVELS.items()}

# --- untrusted presentation lexicon (never consulted for truth) --------------
# Normalise concrete ops to architecture ROLES so the topology reads the same
# across differently-named layers.  Mirrors experiments/abstraction ROLE_CUES.
ROLE_CUES: Tuple[Tuple[str, str], ...] = (
    ("conv", "conv"), ("max_pool", "pool"), ("pool", "pool"),
    ("dropout", "dropout"), ("flatten", "flatten"), ("relu", "relu"),
    ("log_softmax", "softmax"), ("softmax", "softmax"),
    ("linear", "linear"), ("fc", "linear"),
)
# A gradient reset marks the left boundary of one optimisation step.
RESET_CUES: Tuple[str, ...] = ("zero_grad", "zero")
LAYER_ROLES = frozenset({"conv", "pool", "dropout", "flatten", "linear", "softmax", "relu"})

# Effect slug -> readable purpose (presentation; the FACT is api_effect(symbol,effect)).
EFFECT_PHRASES: Dict[str, str] = {
    "prevents_gradient_accumulation": "prevent gradient accumulation",
    "computes_gradients": "compute the gradients",
    "applies_parameter_update": "apply the parameter update",
    "disables_dropout_and_batchnorm": "disable dropout and batch-norm during inference",
    "persists_model_state": "persist the trained model",
}

# Regime predicates (certified) used to CONTRAST two analogous routines.
REGIME_PHRASES: Dict[str, str] = {
    "backpropagates": "backpropagates",
    "optimizes": "updates the parameters",
    "trains": "performs a training step",
    "evaluates": "runs in evaluation mode",
    "uses_grad_free": "computes without gradients",
    "loads_data": "builds the data loaders",
    "builds_model": "constructs the network",
}
REGIME_ORDER: Tuple[str, ...] = (
    "trains", "backpropagates", "optimizes", "evaluates", "uses_grad_free",
    "loads_data", "builds_model",
)


def _slug(text: str) -> str:
    """Identical to experiments/mnist/extract.py:slug (support strings must match)."""
    out = re.sub(r"[^a-z0-9]+", "_", str(text).strip().lower())
    return out.strip("_") or "unknown"


def _astr(a: Atom) -> str:
    return "(" + " ".join([a.pred] + [t.name for t in a.args]) + ")"


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def role_of(slug: str) -> str:
    for cue, role in ROLE_CUES:
        if cue in slug:
            return role
    return slug


def reading_level(sentences: Sequence[dict]) -> int:
    return max((s["level"] for s in sentences), default=0)


def reading_score(sentences: Sequence[dict], *, top: int = len(LEVELS)) -> float:
    """Fraction of the N1..top ladder that has at least one certified sentence."""
    got = {s["level"] for s in sentences if s.get("certified")}
    return round(sum(1 for n in range(1, top + 1) if n in got) / top, 3)


def _emit(out: List[dict], level: int, text: str, support: Iterable[str],
          closed: set) -> None:
    sup = list(support)
    out.append({"level": level, "kind": LEVELS[level], "text": _cap(text),
                "support": sup, "certified": all(tok in closed for tok in sup)})


# --- N1 relation -------------------------------------------------------------
def _relations(closed: set, labels: Dict[str, str], module: str) -> List[dict]:
    out: List[dict] = []
    for a in sorted(closed, key=_astr):
        if a.pred == "imports" and a.args[0].name == module:
            out.append((a, f"{labels.get(a.args[0].name, a.args[0].name)} imports "
                           f"{labels.get(a.args[1].name, a.args[1].name)}."))
    return out


def _n1(closed: set, labels: Dict[str, str], module: str) -> List[dict]:
    closed_strs = {_astr(a) for a in closed}
    out: List[dict] = []
    for a, text in _relations(closed, labels, module):
        _emit(out, 1, text, [_astr(a)], closed_strs)
    return out


# --- N2 meaning --------------------------------------------------------------
def _n2(closed: set, labels: Dict[str, str]) -> List[dict]:
    closed_strs = {_astr(a) for a in closed}
    out: List[dict] = []
    for a in sorted(closed, key=_astr):
        if a.pred == "is_module":
            _emit(out, 2, f"{labels.get(a.args[0].name, a.args[0].name)} is a "
                          f"neural-network module.", [_astr(a)], closed_strs)
    for a in sorted(closed, key=_astr):
        if a.pred == "has_layer":
            _emit(out, 2, f"{labels.get(a.args[0].name, a.args[0].name)} defines a "
                          f"{labels.get(a.args[1].name, a.args[1].name)} layer.",
                  [_astr(a)], closed_strs)
    return out


# --- N3 idiom ----------------------------------------------------------------
IDIOM_TEMPLATES: Dict[str, str] = {
    "trains": "{0} performs a training step.",
    "backpropagates": "{0} calls backpropagation.",
    "optimizes": "{0} updates the parameters with an optimizer.",
    "evaluates": "{0} runs the model in evaluation mode.",
    "uses_grad_free": "{0} computes without gradients.",
    "loads_data": "{0} builds the data loaders.",
    "builds_model": "{0} constructs the network.",
    "orchestrates": "{0} trains then tests the model for each epoch.",
    "saves_model": "{0} saves the trained model.",
}


def _n3(closed: set, labels: Dict[str, str]) -> List[dict]:
    closed_strs = {_astr(a) for a in closed}
    out: List[dict] = []
    for pred in ("trains", "backpropagates", "optimizes", "evaluates", "uses_grad_free",
                 "loads_data", "builds_model", "orchestrates", "saves_model"):
        tmpl = IDIOM_TEMPLATES[pred]
        for a in sorted(closed, key=_astr):
            if a.pred == pred:
                _emit(out, 3, tmpl.format(labels.get(a.args[0].name, a.args[0].name)),
                      [_astr(a)], closed_strs)
    return out


# --- N4 composition ----------------------------------------------------------
def _gradient_window(ops: Sequence[str], meanings: Dict[str, str]):
    """Locate one bounded optimisation step inside a source-ordered pipeline.

    end   = the first op whose acquired meaning is ``parameter_update``
    start = the nearest preceding op that resets the gradient (or pipeline start)
    Requires an op whose acquired meaning is ``backpropagation`` inside the window.
    """
    up = [i for i, o in enumerate(ops) if meanings.get(o) == "parameter_update"]
    if not up:
        return None
    end = up[0]
    start = 0
    for i in range(end, -1, -1):
        if any(c in ops[i] for c in RESET_CUES):
            start = i
            break
    window = list(ops[start:end + 1])
    if not any(meanings.get(o) == "backpropagation" for o in window):
        return None
    return start, end, window


def _stage(op: str, meanings: Dict[str, str]) -> str:
    if any(c in op for c in RESET_CUES):
        return "reset"
    m = meanings.get(op)
    if m == "backpropagation":
        return "backward"
    if m == "parameter_update":
        return "update"
    return "forward/loss"


def _n4(closed: set, labels: Dict[str, str], pipelines: Dict[str, List[str]],
        meanings: Dict[str, str]) -> List[dict]:
    closed_strs = {_astr(a) for a in closed}
    out: List[dict] = []
    for owner in sorted(pipelines):
        ops = pipelines[owner]
        found = _gradient_window(ops, meanings)
        if found is None:
            continue
        start, end, window = found
        display = labels.get(owner, owner)
        chain = " -> ".join(f"{labels.get(o, o)} ({_stage(o, meanings)})" for o in window)
        support = []
        for a, b in zip(window, window[1:]):
            support.append(f"(before {_slug(f'{display}__{a}')} {_slug(f'{display}__{b}')})")
        for o in window:
            support.append(f"(calls {owner} {o})")
        _emit(out, 4, f"Inside {display}, one gradient step runs in a fixed order: {chain}.",
              support, closed_strs)
    return out


# --- N6 causal ---------------------------------------------------------------
def _effect_phrase(effect: str) -> str:
    return EFFECT_PHRASES.get(effect, effect.replace("_", " "))


def _n6(closed: set, labels: Dict[str, str]) -> List[dict]:
    """Realise ``explains(F, S, E)`` from acquired api_effect facts + direct calls."""
    closed_strs = {_astr(a) for a in closed}
    out: List[dict] = []
    for a in sorted(closed, key=_astr):
        if a.pred != "explains":
            continue
        f, s, e = (t.name for t in a.args)
        support = [_astr(a), f"(calls {f} {s})", f"(api_effect {s} {e})"]
        _emit(out, 6, f"{labels.get(f, f)} calls {labels.get(s, s)} in order to "
                      f"{_effect_phrase(e)}.", support, closed_strs)
    return out


# --- N7 purpose --------------------------------------------------------------
def _n7(closed: set, labels: Dict[str, str], entity_phrases: Dict[str, str]) -> List[dict]:
    """Realise the derived core concept (the gist) -- abstains when nothing fires."""
    closed_strs = {_astr(a) for a in closed}
    out: List[dict] = []
    for a in concept_atoms(closed):
        p = labels.get(a.args[0].name, a.args[0].name)
        if a.pred == "recognizes":
            phrase = entity_phrases.get(a.args[1].name, a.args[1].name)
            text = (f"{p} is a program that trains a neural-network model to "
                    f"recognize {phrase}.")
        elif a.pred == "trains_model":
            text = f"{p} trains a neural-network model."
        else:  # is_supervised
            text = f"{p} is trained with supervised learning."
        _emit(out, 7, text, [concept_str(a)], closed_strs)
    return out


# --- N5 architecture ---------------------------------------------------------

def _block_label(roles: Sequence[str]) -> str:
    parts = []
    if "conv" in roles:
        parts.append("a convolution block")
    if "pool" in roles or "flatten" in roles:
        parts.append("downsampling")
    if "linear" in roles:
        parts.append("a classifier head")
    return ", then ".join(parts) if parts else "a layered network"


def _n5(closed: set, labels: Dict[str, str], pipelines: Dict[str, List[str]]) -> List[dict]:
    closed_strs = {_astr(a) for a in closed}
    best = None
    for owner in sorted(pipelines):
        ops = pipelines[owner]
        roles = [role_of(o) for o in ops]
        n_layer = sum(1 for r in roles if r in LAYER_ROLES)
        if n_layer < 3:
            continue
        # prefer a forward method when one exists, then the longest role chain
        score = (1 if "forward" in owner else 0, n_layer, len(ops))
        if best is None or score > best[0]:
            best = (score, owner, ops, roles)
    if best is None:
        return []
    _score, owner, ops, roles = best
    display = labels.get(owner, owner)
    chain = " -> ".join(roles)
    # support = the ordered ``before`` chain of the forward steps (base facts,
    # in the closure).  The role names are an untrusted presentation of those steps.
    support = [f"(before {_slug(f'{display}__{a}')} {_slug(f'{display}__{b}')})"
               for a, b in zip(ops, ops[1:])]
    text = (f"{display} is a small network ({_block_label(roles)}). In order it runs: {chain}.")
    out: List[dict] = []
    _emit(out, 5, text, support, closed_strs)
    return out


# --- N8 analogy --------------------------------------------------------------
def _regime(closed: set, owner: str) -> List[str]:
    """Certified regime predicates HOLDING of ``owner``, in a fixed reading order."""
    have = {a.pred for a in closed if a.args and a.args[0].name == owner}
    return [p for p in REGIME_ORDER if p in have]


def _regime_phrase(preds: Sequence[str]) -> str:
    words = [REGIME_PHRASES[p] for p in preds]
    if not words:
        return "does something else"
    if len(words) == 1:
        return words[0]
    return ", ".join(words[:-1]) + " and " + words[-1]


def _shared_symbols(closed: set, a: str, b: str) -> List[str]:
    """Symbols BOTH routines call directly (from certified ``calls`` atoms)."""
    ca = {x.args[1].name for x in closed if x.pred == "calls" and x.args[0].name == a}
    cb = {x.args[1].name for x in closed if x.pred == "calls" and x.args[0].name == b}
    return sorted(ca & cb)


def _n8(closed: set, labels: Dict[str, str], pipelines: Dict[str, List[str]]) -> List[dict]:
    """Structural analogy: two routines with shared calls but divergent regime.

    The alignment is CERTIFIED: the shared symbols come from ``calls`` atoms and
    the contrast from regime atoms, both in the closure.  No similarity is
    *asserted*; it is read off two provable facts plus a provable difference.
    """
    closed_strs = {_astr(a) for a in closed}
    owners = sorted(pipelines)
    out: List[dict] = []
    for i in range(len(owners)):
        for j in range(i + 1, len(owners)):
            a, b = owners[i], owners[j]
            ra, rb = _regime(closed, a), _regime(closed, b)
            if not ra or not rb or (set(ra) & set(rb)):
                continue                       # need a genuine, DISJOINT regime split
            shared = _shared_symbols(closed, a, b)
            if not shared:
                continue                       # nothing to align
            # prefer shared symbols that carry a known meaning (structure, not noise)
            sym = sorted(shared, key=lambda s: (s not in LAYER_ROLES, s))[:3]
            sym_txt = ", ".join(labels.get(s, s) for s in sym)
            support = [f"(calls {a} {s})" for s in sym]
            support += [f"(calls {b} {s})" for s in sym]
            support += [f"({p} {a})" for p in ra] + [f"({p} {b})" for p in rb]
            text = (f"{labels.get(a, a)} and {labels.get(b, b)} are the same routine "
                    f"in two regimes: both call {sym_txt}, but {labels.get(a, a)} "
                    f"{_regime_phrase(ra)}, while {labels.get(b, b)} {_regime_phrase(rb)}.")
            _emit(out, 8, text, support, closed_strs)
    return out


# --- N9 absence (D5 closed-world negation) ----------------------------------
def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def _n9(closed: set, labels: Dict[str, str]) -> List[dict]:
    """Realise the certified NEGATIVE ``absent(M, L)`` (stratified negation).

    This is the first NEGATIVE sentence in the reading: ``absent`` is derivable
    only by closed-world negation over a GIVEN candidate universe, and it is
    NON-MONOTONIC -- adding one ``has_layer`` fact retracts the matching
    sentence.  Pure Horn deduction can never produce it.  The sentence is a
    kernel-certified conclusion, not an assertion of absence-in-general.
    """
    closed_strs = {_astr(a) for a in closed}
    out: List[dict] = []
    for a in sorted(closed, key=_astr):
        if a.pred != "absent":
            continue
        m = labels.get(a.args[0].name, a.args[0].name)
        l = labels.get(a.args[1].name, a.args[1].name)
        _emit(out, 9, f"{m} does not contain {_article(l)} {l} layer.",
              [_astr(a)], closed_strs)
    return out


# What each rung IS, so a sentence analysis can separate presentation from
# deduction.  Only N9 changes the conclusion set (it is the certified NEGATIVE,
# non-monotonic); N2/N6/N7/N8 lean on ACQUIRED knowledge; N3/N4/N5/N8 are
# presentation of certified structure.
LEVEL_NOTE: Dict[int, str] = {
    1: "fact (monotone)",
    2: "acquired meaning applied",
    3: "presentation: idiom",
    4: "presentation: named composition",
    5: "presentation: role topology",
    6: "certified why (acquired api_effect)",
    7: "purpose/gist (NEEDS searched domain knowledge)",
    8: "presentation: certified analogy",
    9: "deduction: certified NEGATIVE (non-monotonic)",
}


def analyze_sentences(sentences: Sequence[dict], closed: set) -> dict:
    """Analyse the final NL output sentence by sentence (untrusted).

    Separates the *presentation* reach (how many rungs speak) from the
    *deduction* content: every sentence's ``support`` atoms must lie in the
    kernel closure, and only N9 is a non-monotonic conclusion.  This is a
    read-only report over an already-certified reading; it asserts nothing.
    """
    closed_strs = {_astr(a) for a in closed}
    by_level: Dict[int, List[dict]] = {}
    for s in sentences:
        by_level.setdefault(s["level"], []).append(s)
    support_atoms: set = set()
    for s in sentences:
        support_atoms.update(s["support"])
    uncertified = [s["text"] for s in sentences if not s.get("certified")]
    levels = sorted(by_level)
    return {
        "sentence_count": len(sentences),
        "by_level": {n: len(by_level[n]) for n in levels},
        "rung_kind": {n: LEVEL_NOTE.get(n, "?") for n in levels},
        "levels_present": levels,
        "max_level": max(levels) if levels else 0,
        "certified": sum(1 for s in sentences if s.get("certified")),
        "uncertified": uncertified,
        "all_support_in_closure": all(t in closed_strs for t in support_atoms),
        "distinct_support_atoms": len(support_atoms),
        "mean_support_size": round(
            sum(len(s["support"]) for s in sentences) / len(sentences), 3)
        if sentences else 0.0,
        "negative_sentences": len(by_level.get(9, [])),
        "negative_texts": [s["text"] for s in by_level.get(9, [])],
        "presentation_only_levels": [n for n in levels if n in (1, 3, 4, 5, 8)],
        "knowledge_dependent_levels": [n for n in levels if n in (2, 6, 7)],
    }


def reading(closed: set, labels: Dict[str, str], pipelines: Dict[str, List[str]],
            *, module: str = "main", meanings: Optional[Dict[str, str]] = None,
            entity_phrases: Optional[Dict[str, str]] = None) -> List[dict]:
    """Reduce a program's kernel closure to a leveled natural-language reading."""
    meanings = meanings or {}
    entity_phrases = entity_phrases or {}
    out: List[dict] = []
    out += _n1(closed, labels, module)
    out += _n2(closed, labels)
    out += _n3(closed, labels)
    out += _n4(closed, labels, pipelines, meanings)
    out += _n5(closed, labels, pipelines)
    out += _n6(closed, labels)
    out += _n7(closed, labels, entity_phrases)
    out += _n8(closed, labels, pipelines)
    out += _n9(closed, labels)
    out.sort(key=lambda s: (s["level"], s["text"]))
    return out