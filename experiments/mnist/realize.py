"""Grounded realizer: kernel atoms -> natural-language sentences.

The realizer is UNTRUSTED and templated.  It never invents: every sentence is
attached to the atoms (its ``support``) that entail it, and ``run.py`` refuses to
emit a sentence whose support is not in the kernel closure.  So the text is a
*gloss over a proof*, not free generation -- which is exactly why it can be
checked.  Where the reduction captured nothing, there is no sentence (abstain).
"""
from __future__ import annotations

from typing import Dict, List

try:
    from .extract import slug
except ImportError:  # direct `python experiments/mnist/run.py`
    from extract import slug

TEMPLATES: Dict[str, str] = {
    "imports": "{0} imports {1}.",
    "defines": "{0} defines {1}.",
    "is_module": "{0} is a PyTorch neural-network module.",
    "inherits": "{0} extends {1}.",
    "has_layer": "{0} contains a {1} layer.",
    "trains": "{0} performs a training step.",
    "backpropagates": "{0} calls backpropagation (loss.backward).",
    "optimizes": "{0} updates the parameters with the optimizer.",
    "evaluates": "{0} runs the model in evaluation mode.",
    "uses_grad_free": "{0} computes without gradients (no_grad).",
    "loads_data": "{0} builds the MNIST data loaders.",
    "builds_model": "{0} constructs the network.",
    "orchestrates": "{0} trains then tests the model for each epoch.",
    "saves_model": "{0} saves the trained model.",
}


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def realize(closed: set, labels: Dict[str, str], pipelines: Dict[str, List[str]],
            module: str, base: set = frozenset()) -> List[dict]:
    """Select, order and template the understanding atoms; each carries support."""
    def name(s: str) -> str:
        return labels.get(s, s)

    def support_key(a) -> tuple:
        return (a.pred,) + tuple(t.name for t in a.args)

    out: List[dict] = []

    def emit(pred: str, atom, text: str) -> None:
        out.append({"pred": pred, "text": _cap(text), "support": ["(%s)" % " ".join(support_key(atom))]})

    # direct imports (module-level only)
    for a in sorted(closed, key=lambda a: (a.pred,) + tuple(t.name for t in a.args)):
        if a.pred == "imports" and a.args[0].name == module:
            emit("imports", a, TEMPLATES["imports"].format(name(a.args[0].name), name(a.args[1].name)))

    # understanding predicates, in the declared order
    order = ["is_module", "inherits", "has_layer", "trains", "backpropagates", "optimizes",
             "evaluates", "uses_grad_free", "loads_data", "builds_model", "orchestrates",
             "saves_model"]
    for pred in order:
        tmpl = TEMPLATES.get(pred)
        if not tmpl:
            continue
        for a in sorted(closed, key=lambda a: tuple(t.name for t in a.args)):
            if a.pred != pred:
                continue
            emit(pred, a, tmpl.format(*[name(t.name) for t in a.args]))

    # what the entry point reaches only through the learned (transitive) rule
    direct = {a.args[1].name for a in base
              if a.pred == "calls" and a.args[0].name == module}
    indirect = sorted({a.args[1].name for a in closed
                       if a.pred == "calls" and a.args[0].name == module
                       and a.args[1].name in labels} - direct)
    interesting = [x for x in indirect if x in ("loss_backward", "optimizer_step", "model_eval")]
    for x in interesting:
        out.append({"pred": "calls+", "text": _cap(f"{name(module)} indirectly reaches {name(x)} "
                                                    f"(derived by the induced call rule, not a direct call)."),
                    "support": [f"(calls {module} {x})"]})

    # ordered pipeline per owner, citing the (before step step) atoms
    for owner, steps in pipelines.items():
        if len(steps) < 3 or owner not in ("train", "test", "main"):
            continue
        chain = " -> ".join(name(s) for s in steps)
        seq = list(zip(steps, steps[1:]))
        support = [f"(before {slug(f'{owner}__{a}')} {slug(f'{owner}__{b}')})" for a, b in seq]
        out.append({"pred": "pipeline", "text": _cap(f"Inside {name(owner)} the steps run in order: {chain}."),
                    "support": support})
    return out