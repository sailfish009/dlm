#!/usr/bin/env python3
"""Serve a tiny local web fixture, fetch it, and emit observations."""
import http.server
import json
import re
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "experiments/web_rule_repl/site"
CACHE = ROOT / "experiments/web_rule_repl/cache/index.html"
OUT = ROOT / "experiments/web_rule_repl/web_observations.l"


def serve():
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=str(SITE), **k)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def singular(s):
    return s[:-1] if s.endswith("s") and len(s) > 2 else s


def main():
    httpd, port = serve()
    url = f"http://127.0.0.1:{port}/index.html"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            html = r.read().decode("utf-8")
    finally:
        httpd.shutdown()
    CACHE.write_text(html, encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", html)
    quotes = [q.strip() for q in re.findall(r"(?:A|All) [^.<]+\.", text)]
    rows = []
    for i, q in enumerate(quotes):
        m = re.match(r"A (\w+) is a (\w+)", q, re.I)
        if m:
            rows.append((f"w{i}", url, q, singular(m.group(1).lower()), singular(m.group(2).lower())))
            continue
        m = re.match(r"All (\w+) are (\w+)", q, re.I)
        if m:
            rows.append((f"w{i}", url, q, singular(m.group(1).lower()), singular(m.group(2).lower())))
    lines = ["(define *web-observations*", "  (list"]
    for rid, u, q, s, o in rows:
        lines.append(f'    (w-observation "{rid}" "{u}" "{q}" \'{s} \'{o})')
    lines.extend(["  ))", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} observations={len(rows)} url={url}")
    for row in rows:
        print(" ", row[2])


if __name__ == "__main__":
    main()
