"""A corpus of small PyTorch-like trainer programs (untrusted, deterministic).

Each program is REAL Python, reduced by ``experiments.mnist.extract`` and given
meaning by ``experiments.mnist.knowledge`` -- i.e. it goes through the same
north-star pipeline as ``main.py``.  The generator varies the *behaviour* flags
(train/backprop/step/eval/no-grad/save/loader/scheduler and the layer set) so the
understanding predicates are **not** extensionally degenerate: the conjunctions
the generaliser mines mean something.

The real PyTorch MNIST example is added by ``north_star_source`` and is held out
for deductive transfer (the generalisation is learned on the corpus and applied
to the north star, mirroring ``experiments/code``).
"""
from __future__ import annotations

from itertools import product
from typing import Dict, List, Tuple

LayerInit = {
    "conv2d": "self.c1 = nn.Conv2d(1, 10, 3)",
    "linear": "self.fc = nn.Linear(10, 10)",
    "dropout": "self.do = nn.Dropout(0.5)",
}
LayerForward = {
    "conv2d": "self.c1(x)",
    "linear": "self.fc(x)",
    "dropout": "self.do(x)",
    "max_pool2d": "F.max_pool2d(x, 2)",
}
ForwardOp = {"relu": "F.relu(x)"}   # kept for callers that import it


def program(*, layers: Tuple[str, ...] = ("conv2d", "linear"),
            backward: bool = True, step: bool = True,
            ev: bool = True, nograd: bool = True,
            save: bool = True, loader: bool = True, sched: bool = False,
            entry: str = "main") -> str:
    """Render one valid program.  ``backward``/``step`` are independent so that
    accumulation-style trains (backward, no step) and manual-step trains exist."""
    inits = "\n".join("        " + LayerInit[l] for l in layers if l in LayerInit)
    flines: List[str] = []
    for l in layers:
        if l in LayerForward:
            flines.append("        x = " + LayerForward[l])
            flines.append("        x = F.relu(x)")
    fops = "\n".join(flines)
    p: List[str] = [
        "import torch", "import torch.nn as nn", "import torch.optim as optim",
        "import torch.nn.functional as F", "",
        "class Net(nn.Module):", "    def __init__(self):",
        "        super(Net, self).__init__()", inits,
        "    def forward(self, x):", fops, "        return x", "",
    ]
    trains = backward or step
    if trains:
        p += ["def train(model, optimizer, loader):", "    optimizer.zero_grad()",
              "    output = model(None)", "    loss = F.nll_loss(output, None)"]
        if backward:
            p += ["    loss.backward()"]
        if step:
            p += ["    optimizer.step()"]
        p += [""]
    if ev:
        p += ["def test(model, loader):", "    model.eval()"]
        if nograd:
            p += ["    with torch.no_grad():", "        output = model(None)"]
        else:
            p += ["    output = model(None)"]
        p += [""]
    p += [f"def {entry}():", "    model = Net()",
          "    optimizer = optim.Adadelta(model.parameters())"]
    if loader:
        p += ["    loader = torch.utils.data.DataLoader(None)"]
    if sched:
        p += ["    scheduler = optim.lr_scheduler.StepLR(optimizer, 1)"]
    p += ["    for epoch in range(3):"]
    body: List[str] = []
    if trains:
        body += ["        train(model, optimizer, loader if loader is not None else None)"]
    if ev:
        body += ["        test(model, loader if loader is not None else None)"]
    if sched:
        body += ["        scheduler.step()"]
    p += body or ["        pass"]
    if save:
        p += ["    torch.save(model.state_dict(), 'm.pt')"]
    return "\n".join(p) + "\n"


def corpus() -> List[Dict]:
    """A curated, deterministic corpus of (name, source) programs.

    Feature axes are crossed so the defining conjunctions vary: layer subsets,
    train with/without backward, with/without step, eval with/without no-grad,
    save / loader / scheduler.  Whole programs are held out for transfer.
    """
    out: List[Dict] = []
    idx = 0
    layer_sets = [("conv2d", "linear"), ("conv2d", "linear", "dropout"),
                  ("linear",), ("conv2d", "dropout"), ("conv2d", "linear", "max_pool2d")]
    for (layers, backward, step, ev, nograd, save, loader, sched) in [
        # a spread, not the full product (keeps the run small and the concepts crisp)
        (("conv2d", "linear"), True, True, True, True, True, True, True),      # full trainer
        (("conv2d", "linear", "dropout"), True, True, True, True, True, True, False),
        (("linear",), True, True, True, True, False, True, False),
        (("linear",), True, True, True, False, True, True, False),             # eval w/o no_grad
        (("conv2d", "linear", "max_pool2d"), True, False, True, True, False, True, False),  # accumulate
        (("conv2d", "dropout"), False, True, False, False, False, False, False),  # step only
        (("conv2d", "linear", "dropout"), True, True, False, False, True, True, False),  # train only, save
        (("linear",), True, True, False, False, False, False, False),          # minimal train
        (("conv2d", "linear"), True, True, True, True, False, False, False),   # train+eval, no io
        (("conv2d", "linear", "dropout"), True, True, True, True, True, False, True),  # no loader
        (("linear", "dropout"), True, True, True, True, True, True, True),     # no conv
        (("conv2d",), True, True, True, True, False, True, False),
    ]:
        out.append({"name": f"p{idx}", "source": program(layers=layers, backward=backward,
                    step=step, ev=ev, nograd=nograd, save=save, loader=loader, sched=sched)})
        idx += 1
    return out


# The real north-star program (added by run.py from the mnist cache) is held out.
NORTH_STAR = "northstar"