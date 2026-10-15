"""Random GitHub acquisition -- no human selection, fully cached and reproducible.

Pipeline (public endpoints, single-token constants only)::

    GitHub  search/repositories   -> a seeded page of small Python repos
    codeload.github.com tarball   -> the repo's ``*.py`` sources
    experiments/code/extract.py   -> (imports module module) Horn facts

Repos are chosen by a seeded shuffle over a ``language:python`` + size-bounded
search pool, so the sample is reproducible and not hand-picked.  Every API
response and every extracted file map is cached under ``cache/`` keyed by repo,
so ``offline=True`` reproduces a run byte-for-byte.  Rate limits are respected
with exponential backoff.
"""
from __future__ import annotations

import io
import tarfile
from random import Random
from typing import Dict, List, Sequence, Tuple

try:
    from . import code, extract
except ImportError:  # run as a top-level script
    import code
    import extract

DEFAULT_QUERY = "language:python fork:false stars:>200 size:<1500"


def search_pool(*, query: str, pages: int, per_page: int, cache, pause: float,
                retries: int) -> List[dict]:
    """Concatenated raw search items across the first ``pages`` pages (cached)."""
    items: List[dict] = []
    for page in range(1, max(1, int(pages)) + 1):
        key = "gh_search_%s_p%d_n%d" % (query, page, per_page)

        def produce(page=page) -> dict:
            return code.url_json(code.search_url(query, page, per_page),
                                 pause=pause, retries=retries, client=cache.web)

        d = cache.get(key, produce)
        items.extend(d.get("items", []) or [])
    return items


def pick_repos(n: int, *, seed: int, query: str = DEFAULT_QUERY, pages: int = 3,
               per_page: int = 50, cache, pause: float, retries: int) -> List[Tuple[str, str]]:
    """Seeded sample of distinct ``(full_name, default_branch)`` candidates."""
    pool = search_pool(query=query, pages=pages, per_page=per_page,
                       cache=cache, pause=pause, retries=retries)
    seen, cands = set(), []
    for it in pool:
        full = it.get("full_name")
        if not full or full in seen:
            continue
        seen.add(full)
        cands.append((full, it.get("default_branch") or "main"))
    Random(seed).shuffle(cands)
    return cands[: max(0, int(n))]


def fetch_files(full: str, ref: str, *, cache, pause: float, retries: int,
                max_files: int, max_file_bytes: int) -> Dict[str, str]:
    """Repo tarball -> {path: source} for the ``*.py`` files (cached, bounded)."""
    key = "gh_files_%s@%s_f%d_b%d" % (full, ref, max_files, max_file_bytes)

    def produce() -> Dict[str, str]:
        raw = code.url_bytes("%s/%s/tar.gz/%s" % (code.CODELOAD, full, ref),
                             pause=pause, retries=retries, client=cache.web)
        out: Dict[str, str] = {}
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
            members = sorted((m for m in tf.getmembers() if m.isfile()), key=lambda m: m.name)
            for m in members:
                if not m.name.endswith(".py") or m.size > max_file_bytes:
                    continue
                try:
                    out[m.name] = tf.extractfile(m).read().decode("utf-8", "replace")
                except Exception:  # noqa: BLE001 -- unreadable member
                    continue
                if len(out) >= max_files:
                    break
        return out

    return cache.get(key, produce)


def acquire(n: int, *, seed: int = 0, cache_dir: str, offline: bool = False,
            query: str = DEFAULT_QUERY, pages: int = 3, per_page: int = 50,
            max_files: int = 250, max_file_bytes: int = 300_000,
            pause: float = 0.5, retries: int = 4) -> List[code.Repo]:
    """Pull ``n`` small random Python repos -> Repo objects carrying import facts."""
    cache = code.CodeCache(cache_dir, offline=offline)
    repos: List[code.Repo] = []
    cands = pick_repos(max(n * 3, n + 6), seed=seed, query=query, pages=pages,
                       per_page=per_page, cache=cache, pause=pause, retries=retries)
    for full, ref in cands:
        try:
            files = fetch_files(full, ref, cache=cache, pause=pause, retries=retries,
                                max_files=max_files, max_file_bytes=max_file_bytes)
        except Exception:  # noqa: BLE001 -- one bad repo must not sink the run
            continue
        edges = extract.import_edges(files)
        if len(edges) < 2:
            continue  # too small to be a useful neighbourhood
        repo = code.Repo(name=full, ref=ref, files=files)
        repo.facts = extract.repo_facts(files, prefix=code.slug(full))
        repos.append(repo)
        if len(repos) >= n:
            break
    return repos