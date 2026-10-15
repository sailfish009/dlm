"""GitHub code extraction for the codessl experiment.

Widens the v0.0039 learning scope from web prose/claims (``experiments/web``)
to **source code**, with no human selection:

* GitHub ``search/repositories`` -> a pseudo-random page of candidate repos
  (filtered by language/size), seeded so a run is replayable.
* ``codeload.github.com`` tarball -> the repo's ``*.py`` sources.
* ``experiments/code/extract.py`` parses each file with the stdlib ``ast`` and
  emits function-free binary Horn facts about the **module import graph**:
  ``(imports <module> <module>)``.

Unlike the web case there is no sampled weak supervision: the repo's own
ground-truth import graph is the exact oracle for the base facts, and its
transitive closure is the exact target.  Everything is cached under ``cache/``
so ``offline=True`` reproduces a run byte-for-byte and never touches the
network.  Rate limits are respected with exponential backoff.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.parse as up
import urllib.request as ur
from dataclasses import dataclass, field
from typing import Dict, List

UA = {"User-Agent": "dlm-research/0.1 (research; +https://github.com/sailfish009/dlm)"}
GH_API = "https://api.github.com"
CODELOAD = "https://codeload.github.com"


def slug(text: str) -> str:
    """Single-token canonical constant (spaces/punctuation -> underscore)."""
    out = re.sub(r"[^a-z0-9]+", "_", str(text).strip().lower())
    return out.strip("_") or "unknown"


@dataclass(frozen=True)
class Fact:
    pred: str
    subj: str
    obj: str

    def sexp(self) -> str:
        return f"({self.pred} {self.subj} {self.obj})"

    def key(self) -> str:
        return self.sexp()


@dataclass
class Repo:
    name: str                                   # owner/repo
    ref: str                                    # default branch
    files: Dict[str, str] = field(default_factory=dict)   # path -> source
    facts: List[Fact] = field(default_factory=list)       # (imports mod mod)


class CodeCache:
    """Tiny JSON cache (same contract as ``experiments/web``'s ``WebCache``)."""

    def __init__(self, cache_dir: str, offline: bool = False) -> None:
        self.dir = cache_dir
        self.offline = offline
        os.makedirs(cache_dir, exist_ok=True)
        self._mem: Dict[str, object] = {}

    def _path(self, key: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", key)
        if len(safe) > 120:
            digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
            safe = safe[:80] + "_" + digest
        return os.path.join(self.dir, safe + ".json")

    def get(self, key: str, producer):
        if key in self._mem:
            return self._mem[key]
        path = self._path(key)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                self._mem[key] = json.load(fh)
            return self._mem[key]
        if self.offline:
            raise FileNotFoundError(f"offline: cache miss for {key!r} ({path})")
        value = producer()
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(value, fh, ensure_ascii=False)
        self._mem[key] = value
        return value


def url_json(url: str, *, pause: float, retries: int) -> object:
    last: Exception | None = None
    for attempt in range(max(1, int(retries))):
        time.sleep(pause * (2 ** attempt))
        try:
            with ur.urlopen(ur.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except Exception as exc:  # noqa: BLE001 -- retry on any transport/HTTP error
            last = exc
    raise last if last else RuntimeError("no response")


def url_bytes(url: str, *, pause: float, retries: int) -> bytes:
    last: Exception | None = None
    for attempt in range(max(1, int(retries))):
        time.sleep(pause * (2 ** attempt))
        try:
            with ur.urlopen(ur.Request(url, headers=UA), timeout=90) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
    raise last if last else RuntimeError("no response")


def search_url(query: str, page: int, per_page: int) -> str:
    return GH_API + "/search/repositories?" + up.urlencode({
        "q": query, "sort": "stars", "order": "desc",
        "per_page": int(per_page), "page": int(page)})