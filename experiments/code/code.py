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
import urllib.parse as up
from dataclasses import dataclass, field
from typing import Dict, List

from dlm.web import UA, Web  # transport is the model's; UA re-exported for callers
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
        self.web = Web(cache_dir, offline=offline)   # the model's cached web client
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


def url_json(url: str, *, pause: float = 0.0, retries: int = 1,
             client: Web = None) -> object:
    """JSON for ``url`` via the model's web client.

    ``pause``/``retries`` are kept for call compatibility; transport and byte
    caching are handled by :class:`dlm.web.Web` (abstain -> ``None`` -> raise).
    """
    client = client or Web("cache")
    data = client.get_json(url)
    if data is None:
        raise RuntimeError(f"no JSON response for {url}")
    return data


def url_bytes(url: str, *, pause: float = 0.0, retries: int = 1,
              client: Web = None) -> bytes:
    client = client or Web("cache")
    raw = client.get_bytes(url)
    if raw is None:
        raise RuntimeError(f"no response for {url}")
    return raw


def search_url(query: str, page: int, per_page: int) -> str:
    return GH_API + "/search/repositories?" + up.urlencode({
        "q": query, "sort": "stars", "order": "desc",
        "per_page": int(per_page), "page": int(page)})