#!/usr/bin/env python3
"""Cached multi-page web observation extraction for the NL boundary."""
import json
import re
import urllib.request
from pathlib import Path

LEX = {"cat", "dog", "bird", "mammal", "animal", "plant", "living-thing", "living thing"}

PAGES = [
    ("Dog", "https://simple.wikipedia.org/api/rest_v1/page/summary/Dog"),
    ("Cat", "https://simple.wikipedia.org/api/rest_v1/page/summary/Cat"),
]


def singular(s):
    return s[:-1] if s.endswith("s") and len(s) > 2 else s


def fetch(url, cache):
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    req = urllib.request.Request(url, headers={"User-Agent": "dlm-web-observation/1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    cache.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def extract(text):
    first = text.split(". ")[0]
    if " are " not in first:
        return None
    left, right = first.split(" are ", 1)
    m = re.match(r"([A-Za-z]+)", left)
    if not m:
        return None
    subj = singular(m.group(1).lower())
    words = re.findall(r"[a-z]+", right.split(".")[0].lower())
    obj = None
    for w in words:
        if singular(w) in LEX:
            obj = singular(w)
            break
    if not obj:
        return None
    quote = first.strip()
    return subj, obj, quote


def main():
    root = Path(__file__).resolve().parents[1]
    cache_dir = root / "experiments/web_multi_repl/cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, url in PAGES:
        data = fetch(url, cache_dir / f"{name.lower()}.json")
        got = extract(data.get("extract", ""))
        if got:
            rows.append((url, *got))
    out = root / "experiments/web_multi_repl/web_observations.l"
    lines = ["(define *web-observations*", "  (list"]
    for i, (url, subj, obj, quote) in enumerate(rows):
        lines.append(f'    (w-observation "w{i}" "{url}" "{quote}" \'{subj} \'{obj})')
    lines.extend(["  ))", ""])
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out} observations={len(rows)}")
    for url, subj, obj, quote in rows:
        print(f"  {subj}->{obj}  {quote}")


if __name__ == "__main__":
    main()
