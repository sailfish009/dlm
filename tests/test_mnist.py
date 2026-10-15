"""Network-free tests of the MNIST north-star slice (reduction -> NL)."""
from experiments.mnist.extract import extract
from experiments.mnist.run import run

TINY = '''
import torch
import torch.nn as nn


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 2)
        self.fc2 = nn.Linear(2, 1)

    def forward(self, x):
        x = self.fc1(x)
        return self.fc2(x)


def train(model, loader, optimizer):
    model.train()
    optimizer.zero_grad()
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


def test_extract_finds_relations():
    ext = extract(TINY, "main")
    facts = set(ext["facts"])
    assert ("defines", "main", "net") in facts
    assert ("inherits", "net", "nn_module") in facts
    assert ("method_of", "net", "net_forward") in facts
    assert ("creates", "net_init", "linear") in facts
    assert ("calls", "train", "loss_backward") in facts
    assert ("calls", "main", "torch_save") in facts
    # pipelines are in source order and share step atoms
    steps = ext["pipelines"]["train"]
    assert steps.index("model_train") < steps.index("optimizer_step")
    assert ("before", "train_model_train", "train_optimizer_zero_grad") in facts


def test_run_derives_verified_understanding():
    r = _result()
    assert r["all_sentences_verified"] is True
    assert r["false_final_count"] == 0
    assert r["counts"]["learned_rules"] >= 1
    # the message uses the trusted kernel: every sentence is backed by closure atoms
    text = " ".join(s["text"] for s in r["narrative"])
    assert "is a PyTorch neural-network module" in text
    assert "calls backpropagation" in text
    assert r["proof"] is not None and r["proof"]["verified"] is True
    assert r["ground_proof"] is not None and r["ground_proof"]["verified"] is True


def test_ir_is_a_form_and_roundtrips():
    r = _result()
    ir = r["ir"]
    assert ir.startswith("(understanding ")
    assert r["learned"]  # at least one induced rule is reported
    # one small file cannot identify the general call law (needs cross-repo data)
    assert r["law_transfer"]["general_law_identifiable_from_one_file"] is False


def test_run_is_deterministic():
    assert _result() == run(TINY, "inline://tiny")


_RESULT = {}


def _result():
    if "r" not in _RESULT:
        _RESULT["r"] = run(TINY, "inline://tiny")
    return _RESULT["r"]