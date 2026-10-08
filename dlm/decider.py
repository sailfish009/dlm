"""DLM v0.0001 — the discriminative decider (System-1 head).

A small MLP (8 -> hidden -> 1) trained with NumPy on the retrieval feature
vectors. It ranks candidates and provides a *calibrated* probability that a
candidate applies, which is what lets the pipeline abstain instead of guessing.

Parameter count with the defaults: 8*16 + 16 + 16 + 1 = 177. Under the 6 GB
constraint this is irrelevant for memory; the point of the constraint is that
the whole system must avoid loading a large encoder. ``torch_decider`` mirrors
the same network in PyTorch so the VRAM probe can measure real device cost.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60.0, 60.0)))


@dataclass
class Decider:
    n_features: int = 8
    hidden: int = 16
    seed: int = 0
    W1: np.ndarray = field(init=False)
    b1: np.ndarray = field(init=False)
    W2: np.ndarray = field(init=False)
    b2: np.ndarray = field(init=False)
    temperature: float = 1.0

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.seed)
        self.W1 = rng.normal(0, 1.0 / np.sqrt(self.n_features), (self.n_features, self.hidden))
        self.b1 = np.zeros(self.hidden)
        self.W2 = rng.normal(0, 1.0 / np.sqrt(self.hidden), (self.hidden, 1))
        self.b2 = np.zeros(1)

    # -- forward -----------------------------------------------------------
    def logits(self, X: np.ndarray) -> np.ndarray:
        X = np.atleast_2d(X)
        a1 = np.tanh(X @ self.W1 + self.b1)
        return (a1 @ self.W2 + self.b2).ravel()

    def predict_proba(self, X: np.ndarray, calibrated: bool = True) -> np.ndarray:
        z = self.logits(X)
        if calibrated and self.temperature > 0:
            z = z / self.temperature
        return _sigmoid(z)

    def num_params(self) -> int:
        return int(self.W1.size + self.b1.size + self.W2.size + self.b2.size)

    # -- training ----------------------------------------------------------
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 400,
        lr: float = 0.05,
        l2: float = 1e-3,
        seed: int = 0,
    ) -> "Decider":
        X = np.atleast_2d(X).astype(np.float64)
        y = np.asarray(y, dtype=np.float64).reshape(-1, 1)
        n = X.shape[0]
        for _ in range(epochs):
            a1 = np.tanh(X @ self.W1 + self.b1)
            p = _sigmoid(a1 @ self.W2 + self.b2)
            dz2 = (p - y) / n
            dW2 = a1.T @ dz2 + l2 * self.W2
            db2 = dz2.sum(axis=0)
            da1 = dz2 @ self.W2.T
            dz1 = da1 * (1.0 - a1**2)
            dW1 = X.T @ dz1 + l2 * self.W1
            db1 = dz1.sum(axis=0)
            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2
        return self

    def calibrate(self, X: np.ndarray, y: np.ndarray) -> float:
        """Fit a single temperature on held-out logits (Platt-style)."""
        z = self.logits(X)
        y = np.asarray(y, dtype=np.float64).ravel()
        best_t, best_nll = 1.0, np.inf
        for t in np.linspace(0.25, 4.0, 76):
            p = _sigmoid(z / t)
            nll = -np.mean(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12))
            if nll < best_nll:
                best_nll, best_t = nll, float(t)
        self.temperature = best_t
        return best_t


def torch_decider(n_features: int = 8, hidden: int = 16, seed: int = 0):
    """The same MLP in PyTorch, for device/VRAM measurement. Returns (model, params)."""
    import torch
    from torch import nn

    torch.manual_seed(seed)
    model = nn.Sequential(
        nn.Linear(n_features, hidden),
        nn.Tanh(),
        nn.Linear(hidden, 1),
    )
    n_params = sum(p.numel() for p in model.parameters())
    return model, n_params