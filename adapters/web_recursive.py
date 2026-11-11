#!/usr/bin/env python3
"""Actual Simple Wikipedia pages → subclass edges → self-supervised path labels."""
import json, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "experiments/web_recursive_repl/cache"
OUT = ROOT / "experiments/web_recursive_repl/web_data.l"

PAGES = ["Dog", "Cat", "Bird", "Sparrow", "Mammal", "Animal", "Plant"]
LEX = [("living creature", "living-thing"), ("living thing", "living-thing"),
       ("mammal", "mammal"), ("animal", "animal"), ("bird", "bird")]
HELD_EDGES = {("animal", "living-thing"), ("plant", "living-thing")}


def fetch(title):
    path = CACHE / f"{title.lower()}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    url = f"https://simple.wikipedia.org/api/rest_v1/page/summary/{title}"
    req = urllib.request.Request(url, headers={"User-Agent": "dlm-web-recursive/1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def singular(s):
    return s[:-1] if s.endswith("s") and len(s) > 2 else s


def target_after_are(sent):
    low = sent.lower()
    if " are " not in low:
        return None
    tail = low.split(" are ", 1)[1]
    for phrase, sym in LEX:
        if phrase in tail:
            return sym
    return None


def extract(title):
    data = fetch(title)
    text = data.get("extract", "")
    subj = singular(title.lower())
    for sent in re.split(r"(?<=[.!?])\s+", text):
        obj = target_after_are(sent)
        if obj and obj != subj:
            return subj, obj, sent.strip()
    return None


def main():
    rows = []
    for title in PAGES:
        got = extract(title)
        if got:
            rows.append((title, *got))
    # edges and sources
    edges = [(s, o, q) for _, s, o, q in rows]
    train = [(i, s, o) for i, (s, o, q) in enumerate(edges) if (s, o) not in HELD_EDGES]
    # path labels of length >=2 over train edges
    adj = {}
    for _, s, o in train:
        adj.setdefault(s, []).append(o)
    paths = []
    def walk(start, cur, depth):
        if depth >= 2:
            paths.append((start, cur))
        if depth >= 3:
            return
        for nxt in adj.get(cur, []):
            walk(start, nxt, depth + 1)
    for s in adj:
        walk(s, s, 0)
    paths = sorted(set(paths))
    # negative pairs: reverse of a path
    negs = sorted(set((b, a) for a, b in paths if (b, a) not in paths))
    lines = ["(define *web-edges*", "  (list"]
    for i, (s, o, q) in enumerate(edges):
        lines.append(f'    (l-fact "e{i}" (l-atom \'subclass (list \'{s} \'{o})))')
    lines.extend(["  ))", "", "(define *web-sources*", "  (list"])
    for s, o, q in edges:
        lines.append(f'    "{s}->{o}: {q}"')
    lines.extend(["  ))", "", "(define *train-facts*", "  (list"])
    for i, s, o in train:
        lines.append(f'    (l-fact "t{i}" (l-atom \'subclass (list \'{s} \'{o})))')
    lines.extend(["  ))", "", "(define *train-pos*", "  (list"])
    for a, b in paths:
        lines.append(f"    (l-atom 'isa (list '{a} '{b}))")
    lines.extend(["  ))", "", "(define *neg*", "  (list"])
    for a, b in negs[:12]:
        lines.append(f"    (l-atom 'isa (list '{a} '{b}))")
    lines.extend(["  ))", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} pages={len(rows)} edges={len(edges)} train={len(train)} pos={len(paths)} neg={len(negs)}")
    for s, o, q in edges:
        print(f"  {s}->{o}: {q[:100]}")


if __name__ == "__main__":
    main()
