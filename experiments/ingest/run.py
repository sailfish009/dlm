#!/usr/bin/env python3
"""Acquire heterogeneous text and commit its typed IR-TREE projection."""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dlm import (CachedWeb, Store, acquire_documents, commit_transition,  # noqa: E402
                 document_to_episode, fetch_document, field, ingest_transition,
                 new_state, source_document)


def _media(path: str) -> str:
    if path.endswith(".py"):
        return "text/x-python"
    if path.endswith((".md", ".markdown")):
        return "text/markdown"
    return mimetypes.guess_type(path)[0] or "text/plain"


def run(args) -> dict:
    store = Store(args.store)
    if store.exists() and not args.fresh:
        state = store.load()
    else:
        state = new_state(())
        store.create(state, overwrite=args.fresh)

    documents = []
    for filename in args.file:
        path = Path(filename).resolve()
        raw = path.read_bytes()
        if len(raw) > args.max_bytes:
            raise ValueError(f"local input exceeds --max-bytes: {path}")
        documents.append(source_document(
            provider="local", uri=path.as_uri(), title=path.name,
            content=raw.decode("utf-8", "replace"), media_type=_media(str(path)),
            source_group="local:" + str(path), trust="observed"))

    web = CachedWeb(args.cache, offline=args.offline, max_bytes=args.max_bytes)
    for url in args.url:
        document = fetch_document(web, url, provider="web", title=url,
                                  media_type=_media(url), source_group="url:" + url)
        if document is not None:
            documents.append(document)

    providers = tuple(x.strip() for x in args.providers.split(",") if x.strip())
    if args.query:
        documents.extend(acquire_documents(
            args.query, cache_dir=args.cache, offline=args.offline,
            providers=providers, limit=args.limit, web=web))

    existing = {field(document, "id")[1] for document in field(state, "documents")[1:]}
    novel = tuple(document for document in documents if field(document, "id")[1] not in existing)
    if novel:
        transition = ingest_transition(state, novel, role="train",
                                       min_confidence=args.min_confidence)
        state = store.append(state, transition)

    records = []
    for document in novel:
        episode = document_to_episode(document, min_confidence=args.min_confidence)
        provenance = field(document, "provenance")
        records.append({
            "id": field(document, "id")[1],
            "provider": field(provenance, "provider")[1],
            "source_group": field(provenance, "source-group")[1],
            "uri": field(provenance, "uri")[1],
            "claims": len(field(document, "claims")) - 1,
            "admitted_facts": len(field(episode, "facts")) - 1,
        })
    return {
        "status": "ingested" if novel else "abstain-no-new-document",
        "new_documents": len(novel),
        "total_documents": len(field(state, "documents")) - 1,
        "records": records,
        "store": str(args.store),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="")
    parser.add_argument("--providers", default="wikipedia,github,web-search")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--cache", type=Path, default=ROOT / "experiments/ingest/cache")
    parser.add_argument("--store", type=Path, default=ROOT / "experiments/ingest/store")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=2_000_000)
    parser.add_argument("--min-confidence", type=float, default=.85)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = run(args)
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
