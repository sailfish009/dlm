"""Network-free tests of the v0.0040 web-knowledge layer (acquire -> meaning).

These exercise the separation the version introduces: the GIVEN bridge rules name
no PyTorch symbol, and the ACQUIRED ``meaning`` facts come from a cached web
lookup.  Nothing here touches the network.
"""
import json
import os

from experiments.mnist.extract import extract
from experiments.mnist.knowledge import (CONCEPT_CUES, acquire_knowledge,
                                         extract_definition, load_knowledge,
                                         meaning_facts, reduce_definition,
                                         resolve, symbol_candidates)
from experiments.mnist.run import run
from experiments.mnist.semantics import BRIDGE_FORMS, bridge_forms, meaning_forms

CACHE = os.path.join(os.path.dirname(__file__), "..", "experiments", "mnist", "cache")

TINY = '''
import torch
import torch.nn as nn


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 2)

    def forward(self, x):
        return self.fc1(x)


def train(model, loader, optimizer):
    loss = model(loader)
    loss.backward()
    optimizer.step()
    return loss


def test(model, loader):
    model.eval()
    with torch.no_grad():
        loss = model(loader)
    return loss.item()


def main():
    model = Net()
    train(model, None, None)
    test(model, None)
    torch.save(model.state_dict(), "m.pt")
'''


# -- the given bridge rules contain no library symbol -----------------------
def test_bridge_rules_name_no_pytorch_symbol():
    text = " ".join(str(part) for rule in BRIDGE_FORMS for part in _flatten(rule))
    for forbidden in ("nn_module", "loss_backward", "optimizer_step", "model_eval",
                      "torch_no_grad", "torch_save", "dataloader", "conv2d", "linear"):
        assert forbidden not in text, forbidden
    # the only PyTorch-ish name allowed is the *concept* vocabulary itself
    assert "module_base" in text and "backpropagation" in text


def _flatten(node):
    if isinstance(node, (tuple, list)):
        for x in node:
            yield from _flatten(x)
    else:
        yield node


# -- the reduction chooses library-looking symbols only ---------------------
def test_symbol_candidates_are_reduced():
    ext = extract(TINY, "main")
    cands = symbol_candidates(ext["facts"], ext["labels"])
    assert cands.get("nn_module") == "nn.Module"
    assert cands.get("loss_backward") == "loss.backward"
    assert cands.get("torch_save") == "torch.save"
    # local names, defined names, and non-library builtins are dropped
    assert "model" not in cands and "net" not in cands
    assert "range" not in cands and "print" not in cands


# -- resolution against an inventory (no network) ---------------------------
def test_resolve_rules():
    inv = {
        "torch.nn.Module": "generated/torch.nn.Module.html",
        "torch.nn.Conv2d": "generated/torch.nn.Conv2d.html",
        "torch.ao.quantization.Conv2d": "x.html",
        "torch.Tensor.backward": "generated/torch.Tensor.backward.html",
        "torch.autograd.backward": "generated/torch.autograd.backward.html",
        "torch.optim.Optimizer.step": "generated/torch.optim.Optimizer.step.html",
        "torch.save": "generated/torch.save.html",
    }
    assert resolve("torch.save", inv) == ("torch.save", "exact")
    assert resolve("Conv2d", inv)[0] == "torch.nn.Conv2d"        # shortest wins
    assert resolve("nn.Module", inv)[0] == "torch.nn.Module"
    # receiver hint disambiguates a bare method tail
    assert resolve("loss.backward", inv)[0] == "torch.Tensor.backward"
    assert resolve("optimizer.step", inv)[0] == "torch.optim.Optimizer.step"
    assert resolve("NoSuchThing", inv) == (None, "miss")


def test_reduce_definition_and_extract():
    assert reduce_definition("Base class for all neural network modules.") == "module_base"
    assert reduce_definition("Computes the gradient of current tensor wrt graph leaves.") \
        == "backpropagation"
    assert reduce_definition("Set the module in evaluation mode.") == "evaluation"
    assert reduce_definition("Context-manager that disables gradient calculation.") == "gradient_free"
    assert reduce_definition("Saves an object to a disk file.") == "serialization"
    assert reduce_definition("During training, randomly zeroes some of the elements ...") == "layer"
    assert reduce_definition("Returns the indices of the maximum value.") is None
    # first concept in priority order wins on an ambiguous string
    assert reduce_definition("base class for all neural network convolution") == "module_base"
    # definition extraction pulls the first paragraph after the object anchor
    page = '<dt id="torch.no_grad"></dt><dd><p>Context-manager that disables gradient calculation.</p>'
    assert extract_definition(page, "torch.no_grad") == "Context-manager that disables gradient calculation."


# -- the cached acquisition is complete and correct for the values we need --
def test_cached_meanings_are_correct():
    kb = load_knowledge(CACHE)
    syms = kb["symbols"]
    want = {
        "nn.Module": "module_base", "Conv2d": "layer", "Dropout": "layer",
        "Linear": "layer", "DataLoader": "data_loading", "loss.backward": "backpropagation",
        "optimizer.step": "parameter_update", "model.eval": "evaluation",
        "torch.no_grad": "gradient_free", "torch.save": "serialization",
    }
    for label, concept in want.items():
        rec = syms[label]
        assert rec["concept"] == concept, (label, rec["concept"])
        assert rec["definition"], label          # every meaning cites a definition
        assert rec["url"] and "pytorch.org" in rec["url"]
        assert "docs" in rec["providers"]


def test_acquire_offline_uses_cache_and_abstains_without_one(tmp_path):
    ext = extract(TINY, "main")
    got = acquire_knowledge(ext["facts"], ext["labels"], CACHE, offline=True)
    assert got["meanings"]["nn_module"] == "module_base"
    assert got["meanings"]["loss_backward"] == "backpropagation"
    assert got["stats"]["offline"] is True
    assert got["stats"]["fetched_new"] == 0
    # with an empty cache and no network, everything abstains
    empty = acquire_knowledge(ext["facts"], ext["labels"], str(tmp_path), offline=True)
    assert empty["meanings"] == {}


def test_meaning_facts_shape():
    facts = meaning_facts({"nn_module": "module_base"})
    assert facts == [("meaning", "nn_module", "module_base")]
    assert meaning_forms({"nn_module": "module_base"}) == [("meaning", "nn_module", "module_base")]


# -- the run's understanding really depends on the ACQUIRED facts -----------
def test_understanding_requires_acquired_meaning():
    full = run(TINY, "inline://tiny")
    text = " ".join(s["text"] for s in full["narrative"])
    assert "is a neural-network module" in text
    assert "calls backpropagation" in text
    assert full["knowledge"]["meanings"]["nn_module"] == "module_base"

    # strip ALL acquired meanings: structure remains, semantics disappears
    empty = run(TINY, "inline://tiny",
                knowledge={"meanings": {}, "records": [], "stats": {"offline": True}})
    et = " ".join(s["text"] for s in empty["narrative"])
    assert "is a neural-network module" not in et
    assert "calls backpropagation" not in et
    assert "imports torch" in et          # structural facts still understood
    assert empty["all_sentences_verified"] is True


def test_knowledge_is_deterministic():
    a = run(TINY, "inline://tiny")
    b = run(TINY, "inline://tiny")
    assert a == b


# -- the cache is plain JSON (diff-able provenance) -------------------------
def test_knowledge_cache_is_json():
    with open(os.path.join(CACHE, "pytorch_knowledge.json"), encoding="utf-8") as fh:
        kb = json.load(fh)
    assert kb["version"] >= 1
    assert kb["source"].endswith("objects.inv")
    for concept, _ in CONCEPT_CUES:
        assert any(r.get("concept") == concept for r in kb["symbols"].values()), concept