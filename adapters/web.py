#!/usr/bin/env python3
"""External acquisition adapter, adapted from DLM0065 dlm/web.py.

Stdlib HTTP/cache only. Raw documents are observations, never Horn facts.
The Maru bridge is ASCII S-expression DATA with hex-encoded external fields.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "dlm-acquisition/0.0.74"}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def valid_url(url: str) -> bool:
    if not isinstance(url, str):
        return False
    try:
        parts = urllib.parse.urlsplit(url)
        return parts.scheme in ("http", "https") and bool(parts.hostname) and not parts.username and not parts.password
    except ValueError:
        return False


class Redirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not valid_url(newurl):
            raise ValueError("unsupported redirect URL")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class CachedWeb:
    """Bounded HTTP acquisition and immutable-content records; cache-only offline."""

    def __init__(self, cache_dir, *, offline=False, refresh=False, timeout=20.0, max_bytes=262144):
        if timeout <= 0 or max_bytes <= 0:
            raise ValueError("positive timeout and max_bytes required")
        self.root = Path(cache_dir) / "fetch"
        self.root.mkdir(parents=True, exist_ok=True)
        if offline and refresh:
            raise ValueError("offline and refresh are mutually exclusive")
        self.offline, self.refresh, self.timeout, self.max_bytes = offline, refresh, timeout, max_bytes
        self.opener = urllib.request.build_opener(Redirects())

    def get_record(self, url):
        if not valid_url(url):
            return None, "unsupported-url"
        path = self.root / (digest(url.encode()) + ".json")
        if path.exists() and not self.refresh:
            try:
                if path.stat().st_size > 2 * self.max_bytes + 16384:
                    return None, "oversize-cache"
                record = json.loads(path.read_text())
                raw = base64.b64decode(record["raw_base64"], validate=True)
                if (record["url"] != url or len(raw) > self.max_bytes
                        or digest(raw) != record["sha256"]
                        or not valid_url(record["final_url"])
                        or not all(isinstance(record[key], str) for key in
                                   ("fetched_at", "media_type"))):
                    return None, "invalid-cache"
                return record, None
            except (ValueError, KeyError, TypeError, OSError):
                return None, "invalid-cache"
        if self.offline:
            return None, "offline-miss"
        try:
            request = urllib.request.Request(url, headers=UA)
            with self.opener.open(request, timeout=self.timeout) as response:
                raw = response.read(self.max_bytes + 1)
                final_url = response.geturl()
                media = response.headers.get("Content-Type", "application/octet-stream")
            if len(raw) > self.max_bytes:
                return None, "oversize-response"
            if not valid_url(final_url):
                return None, "unsupported-redirect"
            record = dict(url=url, final_url=final_url, media_type=media,
                          fetched_at=datetime.now(timezone.utc).isoformat(),
                          sha256=digest(raw), raw_base64=base64.b64encode(raw).decode("ascii"))
            atomic_write(path, json.dumps(record, ensure_ascii=True, sort_keys=True).encode())
            return record, None
        except urllib.error.HTTPError as exc:
            exc.close()
            return None, "http-status:" + str(exc.code)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            return None, "http-error:" + type(exc).__name__

    def get_bytes(self, url):
        record, _ = self.get_record(url)
        return None if record is None else base64.b64decode(record["raw_base64"])

    def get_json(self, url):
        raw = self.get_bytes(url)
        try:
            return None if raw is None else json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            return None


def search_urls(web, query, provider, limit):
    """Adapt the old provider discovery; failures remain explicit, not guessed."""
    if provider == "github":
        endpoint = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(dict(q=query, per_page=limit))
        result = web.get_json(endpoint)
        if not isinstance(result, dict) or not isinstance(result.get("items"), list):
            return [], "discovery-failed"
        urls = []
        for item in result["items"][:limit]:
            if not isinstance(item, dict):
                continue
            name = item.get("full_name", "")
            if not isinstance(name, str) or not name:
                continue
            readme = web.get_json("https://api.github.com/repos/" + name + "/readme")
            if isinstance(readme, dict) and valid_url(readme.get("download_url", "")):
                urls.append(readme["download_url"])
        return urls, None if urls else "discovery-empty"
    endpoint = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        dict(action="query", format="json", list="search", srsearch=query, srlimit=limit))
    result = web.get_json(endpoint)
    hits = result.get("query") if isinstance(result, dict) else None
    hits = hits.get("search") if isinstance(hits, dict) else None
    if not isinstance(hits, list):
        return [], "discovery-failed"
    urls = ["https://en.wikipedia.org/api/rest_v1/page/summary/" +
            urllib.parse.quote(hit["title"].replace(" ", "_"), safe="")
            for hit in hits[:limit]
            if isinstance(hit, dict) and isinstance(hit.get("title"), str)]
    return urls, None if urls else "discovery-empty"


def hx(value):
    raw = value if isinstance(value, bytes) else value.encode("utf-8")
    return "h" + raw.hex()


def document_form(record):
    raw = base64.b64decode(record["raw_base64"])
    identifier = "d" + digest((record["url"] + "\n" + record["sha256"]).encode())
    fields = [("url", record["url"]), ("final-url", record["final_url"]),
              ("fetched-at", record["fetched_at"]), ("media-type", record["media_type"]),
              ("sha256", record["sha256"]), ("raw", raw)]
    # Exact bytes remain authoritative; text interpretation is a later DLM task.
    return "(document " + identifier + " " + " ".join(
        "(" + key + " " + hx(value) + ")" for key, value in fields) + \
        " (source-group c" + record["sha256"] + ") (status acquired-uninterpreted))"


def acquire(web, urls):
    documents, failures, seen = [], [], set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        record, error = web.get_record(url)
        if error:
            failures.append((url, error))
        else:
            documents.append(record)
    return documents, failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--query")
    parser.add_argument("--provider", choices=("github", "wikipedia"), default="github")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--cache", required=True)
    parser.add_argument("--output", required=True)
    transport = parser.add_mutually_exclusive_group()
    transport.add_argument("--offline", action="store_true")
    transport.add_argument("--refresh", action="store_true")
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--max-bytes", type=int, default=262144)
    args = parser.parse_args()
    if not 1 <= args.limit <= 20 or not (args.url or args.query):
        parser.error("supply --url or --query; limit must be 1..20")
    web = CachedWeb(args.cache, offline=args.offline, refresh=args.refresh,
                    timeout=args.timeout, max_bytes=args.max_bytes)
    urls, failures = list(args.url), []
    if args.query:
        found, error = search_urls(web, args.query, args.provider, args.limit)
        urls.extend(found)
        if error:
            failures.append(("query:" + args.query, error))
    # Bound acquired document count; provider discovery has additional HTTP calls.
    records, errors = acquire(web, urls[:args.limit])
    failures.extend(errors)
    bundle = "(acquisition 74 (" + " ".join(document_form(r) for r in records) + ") (" + \
        " ".join("(failure " + hx(url) + " " + hx(reason) + ")" for url, reason in failures) + "))\n"
    atomic_write(Path(args.output), bundle.encode("ascii"))
    atomic_write(Path(args.output + ".json"), json.dumps(
        dict(documents=records, failures=failures, fetched=len(records),
             status="fetched" if records else "no-data", interpretation="unresolved"),
        ensure_ascii=True, sort_keys=True, indent=2).encode())
    print(json.dumps(dict(fetched=len(records), failures=len(failures), interpretation="unresolved")))


if __name__ == "__main__":
    main()
