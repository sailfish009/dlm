"""Acquire the target source and cache it (untrusted I/O).

The north-star target is the PyTorch MNIST example.  ``--offline`` replays the
byte-identical cached copy so results are reproducible without the network.
"""
from __future__ import annotations

import os
import urllib.request

URL = "https://raw.githubusercontent.com/pytorch/examples/main/mnist/main.py"
UA = {"User-Agent": "dlm-research/0.1"}


def _cache_path(cache_dir: str, url: str) -> str:
    base = os.path.basename(url.rstrip("/")) or "source.py"
    return os.path.join(cache_dir, base)


def acquire(url: str = URL, cache_dir: str = "cache", offline: bool = False,
            local: str = "") -> str:
    if local:
        with open(local, "r", encoding="utf-8") as fh:
            return fh.read()
    os.makedirs(cache_dir, exist_ok=True)
    path = _cache_path(cache_dir, url)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    if offline:
        raise FileNotFoundError(f"offline and no cache at {path}")
    req = urllib.request.Request(url, headers=UA)
    src = urllib.request.urlopen(req, timeout=40).read().decode("utf-8")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(src)
    return src