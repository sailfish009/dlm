"""Acquire the target source and cache it (untrusted I/O).

The transport is the model's (:mod:`dlm.web.Web`); this module keeps only the
north-star's GIVEN URL and the human-readable ``<cache>/main.py`` replay file.
``--offline`` replays the byte-identical cached copy so results are reproducible
without the network.
"""
from __future__ import annotations

import os

from dlm.web import Web

URL = "https://raw.githubusercontent.com/pytorch/examples/main/mnist/main.py"


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
    src = Web(cache_dir, offline=offline).get_text(url)
    if src is None:
        raise FileNotFoundError(f"offline and no cache at {path}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(src)
    return src