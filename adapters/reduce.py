#!/usr/bin/env python3
"""Untrusted reduction: Python source -> DLM ground facts (S-expression data).

This is a developer-side adapter, not part of the trusted kernel. It performs no
inference: it only renames syntax into atoms and records provenance spans. The
kernel decides what follows. `--check` re-reduces and compares the facts hash so
a stale facts file cannot be used silently.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

# Given vocabulary: how a library symbol is named in the reduction.
# The concept mapping is a separate, replaceable knowledge file.
LAYER_CLASSES = {
    'Conv2d': 'conv2d', 'Linear': 'linear', 'Dropout': 'dropout',
    'MaxPool2d': 'maxpool2d', 'BatchNorm2d': 'batchnorm2d',
    'LayerNorm': 'layernorm', 'GRU': 'gru', 'LSTM': 'lstm',
    'MultiheadAttention': 'attention',
}


def dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return None if base is None else f'{base}.{node.attr}'
    if isinstance(node, ast.Call):
        return dotted(node.func)
    return None


def esc(text: str) -> str:
    return json.dumps(text, ensure_ascii=True)


def reduce_source(text: str, record: str):
    tree = ast.parse(text)
    facts: list[tuple[str, tuple[str, ...], str]] = []  # (pred, args, span)

    def add(pred: str, args: tuple[str, ...], line: int) -> None:
        facts.append((pred, args, f'{record}:L{line}'))

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            add('method_of', ('main', f'main.{node.name}'), node.lineno)
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    callee = dotted(sub.func)
                    if callee:
                        add('calls', (f'main.{node.name}', callee), sub.lineno)
                if isinstance(sub, ast.Attribute):
                    name = dotted(sub)
                    if name:
                        add('attr', (f'main.{node.name}', name), sub.lineno)
        if isinstance(node, ast.Call):
            callee = dotted(node.func)
            if callee:
                add('calls', ('main', callee), node.lineno)
                tail = callee.rsplit('.', 1)[-1]
                if tail in LAYER_CLASSES:
                    add('has_layer', ('net', LAYER_CLASSES[tail]), node.lineno)
    # deterministic order, de-duplicated by (pred, args)
    seen = set()
    out = []
    for pred, args, span in sorted(facts, key=lambda f: (f[0], f[1], f[2])):
        key = (pred, args)
        if key in seen:
            continue
        seen.add(key)
        out.append((pred, args, span))
    return out


def render(facts) -> str:
    lines = []
    for pred, args, span in facts:
        rendered = ' '.join(esc(a) for a in args)
        lines.append(f'  (fact107 {esc(pred)} ({rendered}) {esc(span)})')
    return '(facts107\n' + '\n'.join(lines) + ')\n'


def facts_hash(facts) -> str:
    payload = json.dumps([[p, list(a)] for p, a, _ in facts], sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--record', default='main.py')
    ap.add_argument('--out', required=True)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    text = Path(args.source).read_text()
    facts = reduce_source(text, args.record)
    digest = facts_hash(facts)
    if args.check:
        old = Path(args.out).read_text()
        marker = f'; facts-sha256 {digest}'
        if marker not in old:
            raise SystemExit(f'facts file is stale: expected {marker}')
        body = render(facts)
        if body not in old:
            raise SystemExit('facts body does not match a fresh reduction')
        if old.count('(fact104') + old.count('(fact107') != len(facts):
            raise SystemExit('facts body has a different number of facts')
        print(f'{marker}\n; source-sha256 {hashlib.sha256(text.encode()).hexdigest()}')
        return
    header = (f'; reduced from {args.record} by adapters/reduce.py (untrusted)\n'
              f'; source-sha256 {hashlib.sha256(text.encode()).hexdigest()}\n'
              f'; facts-sha256 {digest}\n')
    Path(args.out).write_text(header + render(facts))
    print(f'facts={len(facts)} sha256={digest}')


if __name__ == '__main__':
    main()