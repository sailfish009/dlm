"""DLM v0.0054 -- the model's access to the internet (untrusted, cached I/O).

The model is not only a deductive kernel: more than half of it is *automation*.
It reads code, and to understand that code it must reach outside itself -- the
meaning of a library symbol, what a dataset contains, what an API call does --
none of that lives in the program.  The internet is where the model looks, so web
access is part of the MODEL, not of an experiment harness.

``Web`` is the one primitive every acquisition path uses: a URL in, cached bytes
out.  Nothing here is trusted or interpreted; it is the model's senses, not its
judgment.  Two guarantees keep research reproducible:

* every response is cached under ``<cache_dir>/fetch/`` keyed by URL, so an
  ``offline=True`` replay is byte-for-byte deterministic and needs no network;
* ``get_*`` never raises on a transport/HTTP failure -- it abstains (``None``),
  because an unreachable source is "I do not know", not a crash.

The docs sites serve a tiny JavaScript redirect stub for their stable URLs; the
fetch follows the site's own canonical target (recorded in the page) so the
cached body is the real definition page, not the redirect.
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

__all__ = ["UA", "Web", "js_redirect_target"]

UA: Dict[str, str] = {
    "User-Agent": "dlm-research/0.1 (+https://github.com/sailfish009/dlm)"
}

# A documented JS redirect on the docs site: ``location.replace("../../2.14/...")``.
_JS_REDIRECT = re.compile(r"location\.(?:replace|href)\s*(?:\(|=)\s*[\"']([^\"']+)[\"']")


def js_redirect_target(page: str) -> Optional[str]:
    """The relative target of a JavaScript redirect stub, or ``None``."""
    m = _JS_REDIRECT.search(page)
    return m.group(1) if m else None


class Web:
    """Cached HTTP client.  The model's senses; it asserts nothing.

    ``cache_dir`` is the run's cache root; raw responses live in its ``fetch/``
    subdirectory so they never collide with the reduced (interpreted) records an
    acquisition layer writes beside them.
    """

    def __init__(self, cache_dir: str, offline: bool = False,
                 timeout: float = 40.0) -> None:
        self.root = cache_dir
        self.cache_dir = os.path.join(cache_dir, "fetch")
        self.offline = offline
        self.timeout = timeout
        os.makedirs(self.cache_dir, exist_ok=True)

    # -- cache keying -------------------------------------------------------
    def _key(self, url: str) -> str:
        return base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii")[:120] + ".bin"

    def _path(self, url: str) -> str:
        return os.path.join(self.cache_dir, self._key(url))

    # -- raw transport ------------------------------------------------------
    def _fetch(self, url: str) -> Optional[bytes]:
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, OSError, ValueError):
            return None

    def get_bytes(self, url: str) -> Optional[bytes]:
        """Cached bytes for ``url``; ``None`` (abstain) when offline and uncached."""
        path = self._path(url)
        if os.path.exists(path):
            with open(path, "rb") as fh:
                return fh.read()
        if self.offline:
            return None
        raw = self._fetch(url)
        # Follow the docs' own JS redirect to the versioned page (its canonical
        # target), so the cached body is the definition, not the redirect stub.
        if raw is not None and len(raw) < 4000:
            target = js_redirect_target(raw.decode("utf-8", "replace"))
            if target and not target.startswith("http"):
                import urllib.parse as _up
                joined = _up.urljoin(url, target)
                if joined != url:
                    followed = self._fetch(joined)
                    if followed:
                        raw = followed
        if raw is not None:
            with open(path, "wb") as fh:
                fh.write(raw)
        return raw

    def get_text(self, url: str, encoding: str = "utf-8") -> Optional[str]:
        raw = self.get_bytes(url)
        return None if raw is None else raw.decode(encoding, "replace")

    def get_json(self, url: str) -> Any:
        """Cached JSON for ``url``; ``None`` (abstain) on any failure."""
        raw = self.get_bytes(url)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except ValueError:
            return None

    def exists(self, url: str) -> bool:
        return os.path.exists(self._path(url))