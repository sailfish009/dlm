#!/usr/bin/env python3
"""Small deterministic NumPy graph embedding sidecar (advisory only)."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def embed(graph):
    nodes = graph["nodes"]
    ids = [n["id"] for n in nodes]
    index = {node_id: i for i, node_id in enumerate(ids)}
    n = len(nodes)
    dim = len(nodes[0]["features"])
    x = np.asarray([n["features"] for n in nodes], dtype=np.float64)
    a = np.eye(n, dtype=np.float64)
    for e in graph.get("edges", []):
        if e["from"] in index and e["to"] in index:
            a[index[e["to"]], index[e["from"]]] = 1.0
    deg = np.maximum(a.sum(axis=1, keepdims=True), 1.0)
    a_hat = a / np.sqrt(deg)
    a_hat = a_hat / np.sqrt(np.maximum(a_hat.sum(axis=0, keepdims=True), 1.0))
    rng = np.random.default_rng(20261109)
    w = rng.normal(0.0, 1.0 / np.sqrt(dim), size=(dim, dim))
    h = np.tanh(a_hat @ x @ w + x @ w)
    norms = np.linalg.norm(h, axis=1, keepdims=True)
    h = h / np.maximum(norms, 1e-12)
    out = []
    for node_id, vec in zip(ids, h):
        vals = [int(round(float(v) * 1000000)) for v in vec]
        raw = json.dumps([node_id, vals], separators=(",", ":")).encode()
        out.append((node_id, vals, "h" + hashlib.sha256(raw).hexdigest()[:16]))
    return out


def sexp(rows):
    lines = ["(define *graph-embeddings*", "  (list"]
    for node_id, vals, digest in rows:
        v = " ".join(str(x) for x in vals)
        lines.append(f'    (mg-embedding "{node_id}" {len(vals)} (list {v}) "{digest}")')
    lines.extend(["  ))", ""])
    return "\n".join(lines)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "experiments/graph_embed_repl/graph.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "experiments/graph_embed_repl/embeddings.l"
    rows = embed(load(src))
    Path(dst).write_text(sexp(rows), encoding="utf-8")
    print(f"wrote {dst} nodes={len(rows)}")


if __name__ == "__main__":
    main()
