#!/usr/bin/env python3
"""Untrusted cached-web adapter: JSON claims -> Maru claim forms.

No network access is performed here. The JSON file is a cached representation
with source/version/scope provenance. The DLM core sees only claim data.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


import re

SYMBOL = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
TRUSTS = {"declared", "observed", "hypothesis", "guessed"}


def sx_atom(pred, args):
    if not isinstance(pred, str) or not SYMBOL.match(pred):
        raise ValueError(f"invalid predicate: {pred!r}")
    return f"'(atom {pred} ({' '.join(json.dumps(str(a), ensure_ascii=False) for a in args)}))"


def symbol(x, what):
    if not isinstance(x, str) or not SYMBOL.match(x):
        raise ValueError(f"invalid {what}: {x!r}")
    return f"'{x}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out', required=True)
    ns = ap.parse_args()
    data = json.loads(Path(ns.input).read_text(encoding="utf-8"))
    claims = data['claims'] if isinstance(data, dict) else data
    forms = []
    for c in claims:
        trust = c.get("trust", "hypothesis")
        if trust not in TRUSTS:
            raise ValueError(f"invalid trust: {trust!r}")
        forms.append(
            f"(p107-claim {json.dumps(c['id'], ensure_ascii=False)} {sx_atom(c['pred'], c['args'])} "
            f"{json.dumps(c['source'], ensure_ascii=False)} {json.dumps(c.get('version', 'v1'), ensure_ascii=False)} "
            f"{symbol(c.get('scope', 'web'), 'scope')} '{trust} "
            f"{json.dumps(c.get('extractor', 'cache'), ensure_ascii=False)})")
    Path(ns.out).write_text("(define web-claims (list\n  " + "\n  ".join(forms) + "))\n", encoding="utf-8")
    print(f"claims={len(forms)}")


if __name__ == '__main__':
    main()
