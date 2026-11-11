#!/usr/bin/env python3
"""Cached web sentence → Maru web-observation sidecar."""
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://simple.wikipedia.org/api/rest_v1/page/summary/Dog"
PAT = re.compile(r"\b([A-Z][A-Za-z]+)s? are (?:a |an )?([a-z]+)\b")


def singular(s):
    return s[:-1] if s.endswith("s") and len(s) > 2 else s


def fetch(cache):
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    req = urllib.request.Request(URL, headers={"User-Agent": "dlm-web-observation/1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    cache.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def main():
    root = Path(__file__).resolve().parents[1]
    cache = root / "experiments/web_nl_repl/cache/dog.json"
    text = fetch(cache).get("extract", "")
    first = text.split(". ")[0]
    m = PAT.search(first)
    if not m:
        raise SystemExit("no observation extracted")
    subj = singular(m.group(1).lower())
    obj = singular(m.group(2).lower())
    quote = m.group(0).strip()
    out = root / "experiments/web_nl_repl/web_observations.l"
    out.write_text(
        "(define *web-observations*\n"
        "  (list\n"
        f'    (w-observation "w0" "{URL}" "{quote}" \'{subj} \'{obj})))\n',
        encoding="utf-8",
    )
    print(f"wrote {out} {subj}->{obj} quote={quote}")


if __name__ == "__main__":
    main()
