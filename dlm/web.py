"""Cached external-source acquisition; transport is a sense, never a truth oracle."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable

from .ingest import source_document
from .ir import Form

UA = {"User-Agent": "dlm-ir-ingest/0.0.65 (+https://github.com/sailfish009/dlm)"}
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"
GITHUB_API = "https://api.github.com"
STACKEXCHANGE_API = "https://api.stackexchange.com/2.3"


class CachedWeb:
    """Bounded stdlib HTTP client with deterministic byte cache and abstention."""

    def __init__(self, cache_dir: str | Path, *, offline: bool = False,
                 timeout: float = 30.0, max_bytes: int = 2_000_000):
        self.root = Path(cache_dir) / "fetch"
        self.root.mkdir(parents=True, exist_ok=True)
        self.offline = offline
        self.timeout = float(timeout)
        self.max_bytes = int(max_bytes)

    def _path(self, url: str) -> Path:
        return self.root / (hashlib.sha256(url.encode()).hexdigest() + ".bin")

    def get_bytes(self, url: str) -> bytes | None:
        path = self._path(url)
        if path.exists():
            raw = path.read_bytes()
            return raw if len(raw) <= self.max_bytes else None
        if self.offline:
            return None
        try:
            request = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read(self.max_bytes + 1)
        except (urllib.error.URLError, OSError, ValueError):
            return None
        if len(raw) > self.max_bytes:
            return None
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(raw)
        os.replace(temporary, path)
        return raw

    def get_text(self, url: str) -> str | None:
        raw = self.get_bytes(url)
        return None if raw is None else raw.decode("utf-8", "replace")

    def get_json(self, url: str):
        raw = self.get_bytes(url)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            return None


def _url(base: str, **params) -> str:
    return base + "?" + urllib.parse.urlencode(params)


def wikipedia_documents(web: CachedWeb, query: str, limit: int = 3) -> tuple[Form, ...]:
    search = web.get_json(_url(WIKIPEDIA_API, action="query", format="json",
                               list="search", srsearch=query, srlimit=int(limit)))
    if not isinstance(search, dict):
        return ()
    documents = []
    for hit in (search.get("query", {}).get("search") or [])[:limit]:
        title = hit.get("title")
        if not title:
            continue
        endpoint = WIKIPEDIA_SUMMARY + urllib.parse.quote(title.replace(" ", "_"), safe="")
        summary = web.get_json(endpoint)
        if not isinstance(summary, dict) or not summary.get("extract"):
            continue
        uri = (((summary.get("content_urls") or {}).get("desktop") or {}).get("page")
               or endpoint)
        revision = str((summary.get("revision") or ""))
        documents.append(source_document(
            provider="wikipedia", uri=uri, title=str(summary.get("title") or title),
            content=str(summary["extract"]), media_type="text/plain",
            source_group="wikipedia:" + str(summary.get("pageid") or title),
            revision=revision, trust="acquired"))
    return tuple(documents)


def github_documents(web: CachedWeb, query: str, limit: int = 3) -> tuple[Form, ...]:
    result = web.get_json(_url(GITHUB_API + "/search/repositories", q=query,
                               sort="stars", order="desc", per_page=int(limit)))
    if not isinstance(result, dict):
        return ()
    documents = []
    for item in (result.get("items") or [])[:limit]:
        full = item.get("full_name")
        if not full:
            continue
        readme = web.get_json(GITHUB_API + f"/repos/{full}/readme")
        content = ""
        revision = str(item.get("default_branch") or "")
        if isinstance(readme, dict):
            encoded = readme.get("content")
            if encoded:
                try:
                    content = base64.b64decode(encoded).decode("utf-8", "replace")
                except (ValueError, TypeError):
                    content = ""
            revision = str(readme.get("sha") or revision)
        if not content:
            content = str(item.get("description") or "")
        if not content:
            continue
        documents.append(source_document(
            provider="github", uri=str(item.get("html_url") or f"https://github.com/{full}"),
            title=full, content=content, media_type="text/markdown",
            source_group="github:" + full.casefold(), revision=revision,
            trust="acquired"))
    return tuple(documents)


def web_search_documents(web: CachedWeb, query: str, limit: int = 3,
                         site: str = "stackoverflow") -> tuple[Form, ...]:
    """Use Stack Exchange's public search index as a reproducible web-search source."""
    result = web.get_json(_url(STACKEXCHANGE_API + "/search/advanced", order="desc",
                               sort="relevance", q=query, site=site,
                               pagesize=int(limit), filter="withbody"))
    if not isinstance(result, dict):
        return ()
    documents = []
    for item in (result.get("items") or [])[:limit]:
        qid = str(item.get("question_id") or item.get("link") or item.get("title") or "")
        title = str(item.get("title") or "")
        body = str(item.get("body") or title)
        if not qid or not body:
            continue
        documents.append(source_document(
            provider="web-search", uri=str(item.get("link") or "https://stackoverflow.com"),
            title=title, content=body, media_type="text/html",
            source_group=f"stackexchange:{site}:{qid}",
            revision=str(item.get("last_activity_date") or ""), trust="acquired"))
    return tuple(documents)


def fetch_document(web: CachedWeb, url: str, *, provider: str = "web",
                   title: str = "", media_type: str = "text/html",
                   source_group: str = "", revision: str = "") -> Form | None:
    text = web.get_text(url)
    if text is None:
        return None
    return source_document(provider=provider, uri=url, title=title or url,
                           content=text, media_type=media_type,
                           source_group=source_group, revision=revision)


def acquire_documents(query: str, *, cache_dir: str | Path = "cache",
                      offline: bool = False,
                      providers: Iterable[str] = ("wikipedia", "github", "web-search"),
                      limit: int = 3, web: CachedWeb | None = None) -> tuple[Form, ...]:
    """Acquire heterogeneous documents. Failure means abstention, never guessed data."""
    web = web or CachedWeb(cache_dir, offline=offline)
    acquired: list[Form] = []
    for provider in providers:
        if provider == "wikipedia":
            acquired.extend(wikipedia_documents(web, query, limit))
        elif provider == "github":
            acquired.extend(github_documents(web, query, limit))
        elif provider == "web-search":
            acquired.extend(web_search_documents(web, query, limit))
        else:
            raise ValueError(f"unknown acquisition provider: {provider}")
    # Exact mirrored content is one independence group even across providers.
    from .ir import field, replace_field
    hashes: dict[str, int] = {}
    for document in acquired:
        digest = field(field(document, "provenance"), "content-hash")[1]
        hashes[digest] = hashes.get(digest, 0) + 1
    unique = {}
    for document in acquired:
        provenance = field(document, "provenance")
        digest = field(provenance, "content-hash")[1]
        if hashes[digest] > 1:
            provenance = replace_field(provenance, "source-group", ("source-group", "content:" + digest))
            document = replace_field(document, "provenance", provenance)
        unique.setdefault(field(document, "id")[1], document)
    return tuple(unique[key] for key in sorted(unique))
