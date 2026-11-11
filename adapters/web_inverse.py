#!/usr/bin/env python3
"""Local web fixture: subclass facts + one teacher label, for inverse deduction."""
import http.server, re, threading, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "experiments/web_inverse_repl/site"
OUT = ROOT / "experiments/web_inverse_repl/web_observations.l"

def singular(s): return s[:-1] if s.endswith("s") and len(s) > 2 else s

def main():
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=str(SITE), **k)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{httpd.server_address[1]}/index.html"
    try:
        with urllib.request.urlopen(url, timeout=10) as r: html = r.read().decode()
    finally: httpd.shutdown()
    text = re.sub(r"<[^>]+>", " ", html)
    quotes = [q.strip() for q in re.findall(r"(?:A|An|All) [^.<]+\.", text)]
    rows = []
    for i, q in enumerate(quotes):
        m = re.match(r"(?:A|An) (\w+) is a (?:kind of )?(\w+)", q, re.I)
        if m:
            rows.append((f"w{i}", url, q, singular(m.group(1).lower()), singular(m.group(2).lower())))
        else:
            m = re.match(r"All (\w+) are (\w+)", q, re.I)
            if m: rows.append((f"w{i}", url, q, singular(m.group(1).lower()), singular(m.group(2).lower())))
    lines = ["(define *web-observations*", "  (list"]
    for rid,u,q,s,o in rows: lines.append(f'    (w-observation "{rid}" "{u}" "{q}" \'{s} \'{o})')
    lines.extend(["  ))", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} observations={len(rows)} url={url}")
    for r in rows: print(" ", r[2])

if __name__ == "__main__": main()
