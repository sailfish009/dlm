"""DLM v0.0001 — 6 GB GPU feasibility probe.

Measures the real device cost of the decider head on this host's RTX 2060.
There is no encoder in v0.0001, so this is the only GPU-resident component.
Writes artifacts/vram_probe.json.
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

from dlm.decider import Decider, torch_decider

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artifacts", "vram_probe.json")


def cpu_learning_check() -> dict:
    rng = np.random.default_rng(0)
    n = 512
    X = rng.normal(size=(n, 8))
    # separable rule: positive iff feature 0 + feature 1 > 0
    y = (X[:, 0] + X[:, 1] > 0).astype(float)
    dec = Decider(seed=0)
    dec.fit(X[:384], y[:384], epochs=500, lr=0.1)
    acc = float(np.mean((dec.predict_proba(X[384:]) > 0.5) == (y[384:] > 0.5)))
    t = dec.calibrate(X[384:], y[384:])
    return {"params": dec.num_params(), "holdout_acc": acc, "temperature": t}


def gpu_probe() -> dict:
    import torch

    if not torch.cuda.is_available():
        return {"cuda": False}
    dev = "cuda"
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    base = torch.cuda.memory_allocated()
    model, n_params = torch_decider(8, 16, seed=0)
    model.to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)
    batch = torch.randn(1024, 8, device=dev)
    target = (batch[:, 0:1] + batch[:, 1:2] > 0).float()
    t0 = time.perf_counter()
    for _ in range(50):
        opt.zero_grad()
        loss = torch.nn.functional.binary_cross_entropy_with_logits(model(batch), target)
        loss.backward()
        opt.step()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    dt = (time.perf_counter() - t0) / 50
    peak_alloc = torch.cuda.max_memory_allocated()
    peak_reserved = torch.cuda.max_memory_reserved()
    total = torch.cuda.get_device_properties(0).total_memory
    return {
        "cuda": True,
        "device": torch.cuda.get_device_name(0),
        "params": n_params,
        "base_alloc_bytes": base,
        "peak_alloc_bytes": peak_alloc,
        "peak_reserved_bytes": peak_reserved,
        "total_bytes": total,
        "headroom_factor": total / max(1, peak_reserved),
        "step_ms": dt * 1e3,
    }


def main() -> None:
    report = {
        "cpu_decider": cpu_learning_check(),
        "gpu": gpu_probe(),
    }
    report["verdict"] = (
        "fits_6gb"
        if report["gpu"].get("total_bytes")
        and report["gpu"]["peak_reserved_bytes"] < 6 * 1024**3
        else "unknown"
    )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()